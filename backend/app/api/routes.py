from fastapi import APIRouter, UploadFile, File, Depends, Form
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from app.db import get_db
from app.models import orm
from app.services.crud import get_or_create_product, get_or_create_variant, create_price_observation
from app.services.ocr_parse import parse_ocr_text
from app.services.ingest_parse import parse_circular_text, strip_html
from app.services.sources import load_sources, save_sources
from app.services.ocr import run_tesseract

router = APIRouter()
DATA_ROOT = Path(__file__).resolve().parents[3] / "data"

class CrowdSubmission(BaseModel):
    store_id: int
    product_name: str
    price: float
    size: Optional[str] = None

class CircularIngest(BaseModel):
    store_id: int
    source_url: str
    week_start: Optional[str] = None
    text: str

class CircularFromUrl(BaseModel):
    store_id: int
    source_url: str

class InstacartIngest(BaseModel):
    store_id: int
    url: str
    text: str

@router.get("/stores")
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(orm.Store).order_by(orm.Store.name).all()
    return [{"id": s.id, "name": s.name, "active": s.active} for s in stores]

@router.get("/products")
def search_products(query: str, db: Session = Depends(get_db)):
    q = f"%{query.lower()}%"
    products = db.query(orm.Product).filter(orm.Product.name.ilike(q)).limit(20).all()
    return [{"id": p.id, "name": p.name, "category": p.category} for p in products]

@router.get("/products/{product_id}/prices")
def product_prices(product_id: int, store_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = (
        db.query(orm.PriceObservation)
        .join(orm.ProductVariant, orm.PriceObservation.product_variant_id == orm.ProductVariant.id)
        .filter(orm.ProductVariant.product_id == product_id)
    )
    if store_id:
        q = q.filter(orm.PriceObservation.store_id == store_id)
    prices = q.all()
    return {
        "product_id": product_id,
        "prices": [
            {"store_id": p.store_id, "price": float(p.price), "date": p.date.isoformat(), "source": p.source_type}
            for p in prices
        ]
    }

@router.post("/ocr/run")
def run_ocr(file: UploadFile = File(...)):
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    ocr_dir = DATA_ROOT / "ocr"
    ocr_dir.mkdir(parents=True, exist_ok=True)
    dest = ocr_dir / file.filename
    dest.write_bytes(file.file.read())
    text = run_tesseract(str(dest))
    items = parse_ocr_text(text)
    return {"text": text, "items": items}

@router.post("/receipts/upload")
def upload_receipt(
    file: UploadFile = File(...),
    store_id: Optional[int] = Form(None),
    ocr_text: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    receipts_dir = DATA_ROOT / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    dest = receipts_dir / file.filename
    dest.write_bytes(file.file.read())

    receipt = orm.Receipt(store_id=store_id, raw_file_path=str(dest))
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    items = []
    text = ocr_text
    if text is None:
        try:
            text = run_tesseract(str(dest))
        except Exception:
            text = None

    if text:
        parsed = parse_ocr_text(text)
        for it in parsed:
            item = orm.ReceiptItem(receipt_id=receipt.id, raw_text=it["raw_text"], price=it["price"])
            db.add(item)
            items.append({"raw_text": it["raw_text"], "price": it["price"]})
        db.commit()

    return {"receipt_id": receipt.id, "status": "received", "items": items}

@router.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(orm.Receipt).filter(orm.Receipt.id == receipt_id).first()
    if not receipt:
        return {"error": "not found"}
    items = db.query(orm.ReceiptItem).filter(orm.ReceiptItem.receipt_id == receipt_id).all()
    return {
        "id": receipt.id,
        "store_id": receipt.store_id,
        "uploaded_at": receipt.uploaded_at.isoformat(),
        "items": [{"raw_text": i.raw_text, "price": float(i.price)} for i in items]
    }

@router.post("/crowd/submit")
def submit_crowd_price(submission: CrowdSubmission, db: Session = Depends(get_db)):
    product = get_or_create_product(db, submission.product_name)
    variant = get_or_create_variant(db, product.id, brand=None, size=submission.size, unit=None)
    crowd = orm.CrowdSubmission(store_id=submission.store_id, product_variant_id=variant.id, price=submission.price)
    db.add(crowd)
    db.commit()
    create_price_observation(db, variant.id, submission.store_id, submission.price, "crowd", "manual")
    return {"status": "ok", "submission_id": crowd.id}

@router.get("/sources")
def list_sources():
    return load_sources()

@router.patch("/sources")
def update_sources(payload: dict):
    save_sources(payload)
    return {"status": "saved"}

@router.post("/ingestion/circulars/from-url")
def ingest_from_url(payload: CircularFromUrl, db: Session = Depends(get_db)):
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    circ_dir = DATA_ROOT / "circulars"
    circ_dir.mkdir(parents=True, exist_ok=True)

    try:
        req = Request(payload.source_url, headers={"User-Agent": "CUFPI/1.0"})
        with urlopen(req) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
    except URLError as exc:
        return {"error": f"failed to fetch url: {exc}"}

    text = ""
    if "text/html" in content_type:
        raw = data.decode("utf-8", errors="ignore")
        text = strip_html(raw)
    elif "text/plain" in content_type:
        text = data.decode("utf-8", errors="ignore")
    else:
        # treat as binary file (pdf/image)
        fname = payload.source_url.split("/")[-1] or "circular.bin"
        dest = circ_dir / fname
        dest.write_bytes(data)
        try:
            text = run_tesseract(str(dest))
        except Exception as exc:
            return {"error": f"ocr failed: {exc}"}

    items = parse_circular_text(text)

    circular = orm.Circular(
        store_id=payload.store_id,
        week_start=date.today(),
        source_url=payload.source_url,
        raw_file_path="",
    )
    db.add(circular)
    db.commit()
    db.refresh(circular)

    for it in items:
        product = get_or_create_product(db, it["name"])
        variant = get_or_create_variant(db, product.id, brand=None, size=it.get("size"), unit=None)
        ci = orm.CircularItem(circular_id=circular.id, raw_text=it["raw_text"], product_variant_id=variant.id, price=it["price"], size=it.get("size"))
        db.add(ci)
        create_price_observation(db, variant.id, payload.store_id, it["price"], "circular", payload.source_url)
    db.commit()

    return {"status": "ingested", "count": len(items), "items": items}

@router.post("/ingestion/circulars/run")
def run_ingestion(payload: CircularIngest, db: Session = Depends(get_db)):
    circular = orm.Circular(
        store_id=payload.store_id,
        week_start=date.fromisoformat(payload.week_start) if payload.week_start else date.today(),
        source_url=payload.source_url,
        raw_file_path=""
    )
    db.add(circular)
    db.commit()
    db.refresh(circular)

    items = parse_circular_text(payload.text)
    for it in items:
        product = get_or_create_product(db, it["name"])
        variant = get_or_create_variant(db, product.id, brand=None, size=it.get("size"), unit=None)
        ci = orm.CircularItem(circular_id=circular.id, raw_text=it["raw_text"], product_variant_id=variant.id, price=it["price"], size=it.get("size"))
        db.add(ci)
        create_price_observation(db, variant.id, payload.store_id, it["price"], "circular", payload.source_url)
    db.commit()

    return {"status": "ingested", "count": len(items)}

@router.post("/ingestion/instacart/scan")
def scan_instacart(items: List[InstacartIngest], db: Session = Depends(get_db)):
    created = 0
    for it in items:
        db_item = orm.InstacartItem(store_id=it.store_id, url=it.url, raw_text=it.text)
        db.add(db_item)
        created += 1
    db.commit()
    return {"status": "queued", "count": created}
