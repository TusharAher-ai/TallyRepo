# 🏦 Tally Entry Automation Tool
**100% Free · No Backend Required · Works Offline · Tally Prime & ERP 9 Ready**

Convert bank statements (PDF/Excel/CSV) into Tally-importable files directly in your browser — no paid APIs, no cloud, no data upload.

---

## ✨ Features

| Feature | Details |
|---|---|
| **File Support** | PDF (digital), XLSX, XLS, CSV |
| **Bank Presets** | SBI, HDFC, ICICI, Axis, Kotak, PNB, Generic |
| **Smart Parsing** | Auto column detection with manual override |
| **Text to Columns** | Split merged columns (delimiter, fixed-width, date+text, regex) |
| **Rule Engine** | Keyword → Ledger rules, saved in localStorage |
| **Auto-Suggest** | Learns from past exports |
| **Voucher Detection** | Payment / Receipt / Contra auto-classified |
| **Duplicate Detection** | Flags potential duplicate entries |
| **Editable Table** | Edit any field including debit/credit amounts directly |
| **User Notes** | Add your own description per transaction (shown in Tally narration) |
| **Running Balance** | Enter opening balance — balance column auto-calculates |
| **Bulk Operations** | Assign ledger/voucher to multiple rows at once |
| **Export: Excel** | Multi-sheet with Ledger Summary + User Notes |
| **Export: CSV** | Simple comma-separated |
| **Export: XML** | Tally Prime **and** Tally ERP 9 compatible XML |

---

## 🚀 Quick Start

### GitHub Pages (Recommended)
1. Fork this repo
2. Go to **Settings → Pages → Source → main branch → / (root)**
3. Access at `https://yourusername.github.io/repo-name`

### Local (No Installation)
1. Download / clone this repo
2. Open `index.html` in any modern browser (Chrome, Firefox, Edge)
3. Click a **Sample** button to try demo data

### With Your Bank Statement
1. Download your bank statement as **Excel or PDF** from net banking
2. Upload the file → select your bank preset
3. Review & map columns → parse transactions
4. Edit any errors directly in the table
5. Add classification rules (e.g. `UPI-AMAZON` → `Amazon Expenses`)
6. Export as **Tally Prime XML** or **Tally ERP 9 XML**

---

## 🏦 Supported Banks

| Bank | Format | Notes |
|---|---|---|
| **SBI** | PDF, XLSX | E-statement from SBI YONO / net banking |
| **HDFC** | PDF, XLSX | Account statement from HDFC NetBanking |
| **ICICI** | PDF, XLSX | iMobile / net banking export |
| **Axis** | PDF, XLSX | Axis Mobile / net banking |
| **Kotak** | PDF, XLSX | Kotak 811 / net banking |
| **PNB** | PDF, XLSX | PNB One / net banking |
| **Generic** | Any | Manual column mapping |

---

## 📋 Classification Rules

Rules use keyword matching against the narration field:

```
Keyword: "UPI-AMAZON"     → Ledger: "Amazon Expenses"
Keyword: "SALARY"         → Ledger: "Salary Account"   (Receipt)
Keyword: "HDFC CREDIT"    → Ledger: "HDFC Credit Card"
Keyword: "LIC"            → Ledger: "LIC Premium"       (Payment)
Keyword: "NEFT-RENT"      → Ledger: "Rent Expense"
Keyword: "ATM"            → Ledger: "Cash Account"      (Contra)
```

Rules are saved in **browser localStorage** and persist across sessions. Export/import rules as JSON to share across devices.

---

## 📝 User Notes

Each transaction has a **User Note** field — type your own description (e.g. "Office supplies for Apr"). This note is:
- Shown in teal below the bank narration in the table
- Prepended to narration in exported XML: `"Your Note | Bank Narration"`
- Included in Excel export as a separate column

---

## 📊 Running Balance

Enter an **Opening Balance** above the transaction table. The Balance column auto-calculates row by row:

```
Balance = Opening Balance + Credits − Debits  (running total)
```

---

## 📥 Tally Import Instructions

### ⚠️ Important: Education Mode Limitation
Tally **Education Mode** has a locked financial year and will **not** import vouchers with dates outside that year. Always use a **licensed copy** of Tally Prime or ERP 9 for real data import.

### Tally Prime XML Import
1. Open **Tally Prime** → Select your company
2. `Gateway of Tally → Import → Data → Vouchers`
3. Browse to the downloaded `.xml` file → press Enter

### Tally ERP 9 XML Import
1. Open **Tally ERP 9** → Select your company
2. `Gateway of Tally → Import of Data → Vouchers`
3. Enter the full path of the `.xml` file → press Enter

### Pre-requisites (Both Versions)
- All ledger accounts in the XML must already exist in Tally
- Company name in the XML must match your Tally company **exactly** (case-sensitive)
- Create a **Suspense Account** ledger under Indirect Expenses

---

## 🗄️ XML Format Details

The tool generates correct XML with both `<DATE>` and `<EFFECTIVEDATE>` tags — both required by Tally Prime for dates to appear correctly after import:

```xml
<VOUCHER VCHTYPE="Payment" ACTION="Create" OBJVIEW="Accounting Voucher View">
  <DATE>20240913</DATE>
  <EFFECTIVEDATE>20240913</EFFECTIVEDATE>
  <VOUCHERTYPENAME>Payment</VOUCHERTYPENAME>
  <PERSISTEDVIEW>Accounting Voucher View</PERSISTEDVIEW>
  <NARRATION>Your Note | Bank Narration</NARRATION>
  ...
</VOUCHER>
```

---

## 🐍 Optional Python Backend (Scanned PDFs)

For **scanned/image-based PDFs**, use the Python backend:

```bash
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000` — no data stored, all in-memory.

Free deployment options:
- **Render.com** — connect GitHub repo
- **Railway.app** — `railway up`
- **Fly.io** — `fly launch`

---

## 🔒 Privacy

- ✅ All processing in your **browser** — no server
- ✅ No files uploaded anywhere
- ✅ No account or login required
- ✅ Rules saved locally in browser only
- ✅ Works **offline** after first load (CDN libraries cached)

---

## 🛠️ Tech Stack

| Component | Library | License |
|---|---|---|
| PDF Parsing | PDF.js | Apache 2.0 |
| Excel Read/Write | SheetJS (xlsx) | Apache 2.0 |
| Python PDF | pdfplumber | MIT |
| Python OCR | Tesseract + pytesseract | Apache 2.0 |
| API Server | FastAPI | MIT |

**Zero paid services. Zero subscriptions. Zero telemetry.**

---

## 📁 File Structure

```
tally-tool/
├── index.html          # Full app — entire frontend in one file
├── README.md           # This file
├── main.py             # Optional Python backend (scanned PDFs)
└── requirements.txt    # Python dependencies
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| PDF shows no data | Download as Excel from your bank instead; use Python backend for scanned PDFs |
| Columns not detected | Use Generic preset and map columns manually |
| Invalid dates | Edit the date cell directly in the Preview table |
| Dates missing in Tally | **Do not use Education Mode** — use licensed Tally Prime/ERP 9 |
| Tally import fails | Ledger names must exist in Tally; company name must match exactly |
| Balance wrong | Set correct Opening Balance above the transaction table |

---

## 📄 License

MIT License — Free for personal and commercial use.
