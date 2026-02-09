from sqlalchemy.orm import Session
from datetime import date
from app.models import orm
from app.services.normalization import normalize_name, normalize_size, similarity


def get_or_create_product(db: Session, name: str) -> orm.Product:
    norm_name = normalize_name(name)
    product = db.query(orm.Product).filter(orm.Product.name == norm_name).first()
    if product:
        return product

    # Lightweight dedup: match close existing names for MVP
    candidates = db.query(orm.Product).all()
    for cand in candidates:
        if similarity(norm_name, cand.name) >= 0.92:
            return cand

    product = orm.Product(name=norm_name)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_or_create_variant(db: Session, product_id: int, brand: str | None, size: str | None, unit: str | None) -> orm.ProductVariant:
    norm_size = normalize_size(size or "") if size else None
    q = db.query(orm.ProductVariant).filter(orm.ProductVariant.product_id == product_id)
    if brand:
        q = q.filter(orm.ProductVariant.brand == brand)
    if norm_size:
        q = q.filter(orm.ProductVariant.normalized_size == norm_size)
    if unit:
        q = q.filter(orm.ProductVariant.unit == unit)
    existing = q.first()
    if existing:
        return existing

    variant = orm.ProductVariant(
        product_id=product_id,
        brand=brand,
        size=size,
        unit=unit,
        normalized_size=norm_size,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    return variant


def create_price_observation(db: Session, product_variant_id: int, store_id: int, price: float, source_type: str, source_ref: str):
    obs = orm.PriceObservation(
        product_variant_id=product_variant_id,
        store_id=store_id,
        price=price,
        date=date.today(),
        source_type=source_type,
        source_ref=source_ref,
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs


def ensure_store_seed(db: Session):
    if db.query(orm.Store).count() == 0:
        db.add_all([
            orm.Store(name="Store A"),
            orm.Store(name="Store B"),
        ])
        db.commit()
