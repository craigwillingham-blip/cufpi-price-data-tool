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

## Deploy backend on Render (for GitHub Pages)

1. Create a free account at Render and connect your GitHub account.
2. In Render, select **New > Blueprint**.
3. Choose this repo: `cufpi-price-data-tool`.
4. Render will detect `render.yaml` and create:
   - `cufpi-price-tool-api` (web service)
   - `cufpi-price-db` (Postgres)
5. Deploy. After it finishes, copy the service URL (it will look like `https://something.onrender.com`).

## Point GitHub Pages to the backend

Open the GitHub Pages UI and set the API in the **Backend Connection** box, or add `?api=YOUR_URL` to the URL, for example:

```
https://craigwillingham-blip.github.io/cufpi-price-data-tool/?api=https://YOUR-RENDER-URL
```
