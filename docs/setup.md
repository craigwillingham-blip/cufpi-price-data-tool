# Setup

## Prereqs
- Python 3.10+
- PostgreSQL (local)
- Tesseract OCR (added to PATH)

## Backend
```
cd "C:\Users\craig\Downloads\CUFPI Price Data Tool\backend"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend (demo)
Open `frontend/index.html` in a browser.

## PowerShell ETL
```
cd "C:\Users\craig\Downloads\CUFPI Price Data Tool\scripts"
./ingest-circulars.ps1 -ConfigPath ..\config\sources.json
```

## Ingest Runner
```
./ingest-runner.ps1 -StoreId 1 -SourceUrl "https://example.com/circular.pdf" -InputPath .\sample.txt
```

## OCR Endpoint
```
POST http://127.0.0.1:8000/ocr/run (multipart file upload)
```
