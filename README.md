# Prism (AI Financial Discovery Copilot) MVP

Prism is a demo-ready web app that converts messy statement PDFs into a clean transaction ledger, computes key discovery metrics, and exports a one-page Discovery Brief PDF.

## Quick Start

### Backend
```bash
cd backend
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and upload PDFs from `sample-data/`.

## What It Does
- Extracts transactions from PDF statements (text-first).
- Computes fixed vs variable spend, true free cash flow, and top categories.
- Generates a one-page Discovery Brief PDF.

## API Endpoints
- `POST /api/process-pdfs` (multipart form-data `files[]`) → ledger + metrics.
- `POST /api/generate-brief` (JSON) → PDF file download.

## Confidence Scoring
The Data Quality panel is based on:
- **High**: 20+ rows, no warnings, OCR not used.
- **Medium**: 10+ rows, 0–1 warnings.
- **Low**: under 10 rows, OCR issues, or multiple warnings.

OCR usage reduces confidence automatically and is labeled “experimental”.

## Known Limitations (MVP)
- OCR depends on Poppler + Tesseract; scans may fail if Poppler is not installed.
- Parsing heuristics are best-effort; unusual statement layouts can be missed.
- Transactions are inferred by regex; multi-line layouts may collapse.
- Fixed/variable is heuristic and may misclassify edge cases.

## Sample Data
Use PDFs in `sample-data/`:
- `sample-statement.pdf`
- `sample-statement-2.pdf`

## OCR Notes
OCR requires Poppler on macOS:
```bash
brew install poppler
```
If Poppler is missing, OCR will return a warning and continue.
