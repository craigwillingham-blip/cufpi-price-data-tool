# CUFPI Price Data Tool

## How to ingest circulars

You can ingest circulars in two ways:

1. **From the GUI**
   - Open the app and click **Ingest Circular** in the top navigation.
   - Choose **Upload File** to upload a PDF/image, or **Use Link** to paste a circular URL.
   - Click **Process Circular**, review detected items, then **Save to Database**.

2. **From the API (PowerShell)**
```
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ingestion/circulars/run" -Body '{
  "store_id": 1,
  "source_url": "https://example.com/circular.pdf",
  "text": "Milk 1 gal $3.49\nEggs 12ct $2.99"
}' -ContentType "application/json"
```

If you want OCR on a file via the API, use `POST /ocr/run` first, then send the extracted text to `/ingestion/circulars/run`.
