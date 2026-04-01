"""
Tally AutoEntry Tool — Optional Python Backend
================================================
For scanned / image-based PDFs that can't be parsed in the browser.
Uses: pdfplumber (text PDFs), pdf2image + pytesseract (scanned PDFs)

Run locally:
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000

Then in the browser tool, set backend URL to: http://localhost:8000
(or your Render/Railway free tier URL)

CORS is enabled for all origins (localhost development).
No data is stored — files are processed in memory only.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import re
from typing import Optional

app = FastAPI(
    title="Tally AutoEntry PDF Parser",
    description="Free, local PDF parser for bank statements",
    version="1.0.0"
)

# Allow all origins (local tool, no auth needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Tally AutoEntry PDF Backend — Free & Local",
        "endpoints": {
            "/parse-pdf": "POST — Parse a PDF bank statement",
            "/health":    "GET  — Health check",
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}


# ─────────────────────────────────────────────
# PDF Parse endpoint
# ─────────────────────────────────────────────
@app.post("/parse-pdf")
async def parse_pdf(
    file: UploadFile = File(...),
    method: str = "auto",          # auto | pdfplumber | tabula | tesseract
    bank: str = "generic",
    skip_header_rows: int = 0,
    skip_footer_rows: int = 0,
):
    """
    Parse a bank statement PDF and return structured transaction data.
    
    Returns:
        {
          "rows": [[cell1, cell2, ...], ...],  # 2D array including header
          "method_used": "pdfplumber",
          "pages": 3,
          "detected_columns": ["Date", "Narration", ...]
        }
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()
    
    # Try methods in order
    errors = []
    
    if method in ("auto", "pdfplumber"):
        result = try_pdfplumber(content, skip_header_rows, skip_footer_rows)
        if result:
            return JSONResponse(result)
        errors.append("pdfplumber: no table found")

    if method in ("auto", "tabula"):
        result = try_tabula(content, skip_header_rows, skip_footer_rows)
        if result:
            return JSONResponse(result)
        errors.append("tabula: no table found")

    if method in ("auto", "tesseract"):
        result = try_tesseract(content, skip_header_rows, skip_footer_rows)
        if result:
            return JSONResponse(result)
        errors.append("tesseract: failed")

    raise HTTPException(422, f"Could not extract table from PDF. Tried: {', '.join(errors)}. "
                            f"Try converting to Excel/CSV manually.")


# ─────────────────────────────────────────────
# Method 1: pdfplumber (best for digital PDFs with text layer)
# ─────────────────────────────────────────────
def try_pdfplumber(content: bytes, skip_header: int, skip_footer: int):
    try:
        import pdfplumber
    except ImportError:
        return None

    try:
        rows = []
        num_pages = 0
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            num_pages = len(pdf.pages)
            for page in pdf.pages:
                # Try table extraction first
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            cleaned = [clean_cell(c) for c in row if c is not None]
                            if any(c.strip() for c in cleaned):
                                rows.append(cleaned)
                else:
                    # Fall back to line-by-line text
                    text = page.extract_text()
                    if text:
                        for line in text.split('\n'):
                            parts = re.split(r'\s{2,}|\t', line.strip())
                            parts = [p.strip() for p in parts if p.strip()]
                            if len(parts) >= 3:
                                rows.append(parts)

        if len(rows) < 2:
            return None

        # Apply skip
        if skip_header > 0:
            rows = rows[skip_header:]
        if skip_footer > 0:
            rows = rows[:-skip_footer]

        return {
            "rows": rows,
            "method_used": "pdfplumber",
            "pages": num_pages,
            "detected_columns": rows[0] if rows else []
        }
    except Exception as e:
        print(f"pdfplumber error: {e}")
        return None


# ─────────────────────────────────────────────
# Method 2: tabula-py (Java-based, great for tables)
# ─────────────────────────────────────────────
def try_tabula(content: bytes, skip_header: int, skip_footer: int):
    try:
        import tabula
        import pandas as pd
    except ImportError:
        return None

    try:
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(content)
            tmp_path = f.name

        dfs = tabula.read_pdf(tmp_path, pages='all', multiple_tables=True, silent=True)
        os.unlink(tmp_path)

        if not dfs:
            return None

        all_rows = []
        header_added = False
        for df in dfs:
            df = df.fillna('').astype(str)
            if not header_added:
                all_rows.append(list(df.columns))
                header_added = True
            for _, row in df.iterrows():
                cells = [clean_cell(str(v)) for v in row.values]
                if any(c.strip() for c in cells):
                    all_rows.append(cells)

        if skip_header:
            all_rows = all_rows[skip_header:]
        if skip_footer:
            all_rows = all_rows[:-skip_footer]

        return {
            "rows": all_rows,
            "method_used": "tabula",
            "pages": len(dfs),
            "detected_columns": all_rows[0] if all_rows else []
        }
    except Exception as e:
        print(f"tabula error: {e}")
        return None


# ─────────────────────────────────────────────
# Method 3: Tesseract OCR (for scanned PDFs)
# ─────────────────────────────────────────────
def try_tesseract(content: bytes, skip_header: int, skip_footer: int):
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
        from PIL import Image
    except ImportError:
        return None

    try:
        images = convert_from_bytes(content, dpi=300)
        all_rows = []

        for img in images:
            # Use TSV output for better structure detection
            tsv = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT,
                                             config='--psm 6')
            # Group by block/line
            lines = {}
            for i, text in enumerate(tsv['text']):
                if not str(text).strip():
                    continue
                line_key = (tsv['block_num'][i], tsv['par_num'][i], tsv['line_num'][i])
                if line_key not in lines:
                    lines[line_key] = []
                lines[line_key].append((tsv['left'][i], str(text).strip()))

            for lk in sorted(lines.keys()):
                words = sorted(lines[lk], key=lambda x: x[0])
                # Group words into columns by X position gaps
                cells = []
                current = []
                prev_x = None
                for x, word in words:
                    if prev_x is not None and x - prev_x > 80:
                        if current:
                            cells.append(' '.join(current))
                        current = [word]
                    else:
                        current.append(word)
                    prev_x = x
                if current:
                    cells.append(' '.join(current))

                if len(cells) >= 3:
                    all_rows.append(cells)

        if skip_header:
            all_rows = all_rows[skip_header:]
        if skip_footer:
            all_rows = all_rows[:-skip_footer]

        return {
            "rows": all_rows,
            "method_used": "tesseract",
            "pages": len(images),
            "detected_columns": all_rows[0] if all_rows else []
        }
    except Exception as e:
        print(f"tesseract error: {e}")
        return None


def clean_cell(s):
    """Clean a cell value: strip whitespace, normalize spaces, remove line breaks."""
    return re.sub(r'\s+', ' ', str(s or '').strip())


# ─────────────────────────────────────────────
# Run directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("Starting Tally AutoEntry PDF Backend on http://localhost:8000")
    print("Open the HTML tool and set backend URL to http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
