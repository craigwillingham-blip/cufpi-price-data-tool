from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Date, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    instacart_store_id = Column(String)
    active = Column(Boolean, default=True)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    normalized_unit = Column(String)


class ProductVariant(Base):
    __tablename__ = "product_variants"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    brand = Column(String)
    size = Column(String)
    unit = Column(String)
    upc = Column(String)
    normalized_size = Column(String)

    product = relationship("Product")


class PriceObservation(Base):
    __tablename__ = "price_observations"
    id = Column(Integer, primary_key=True, index=True)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    price = Column(Numeric(10, 2))
    date = Column(Date)
    source_type = Column(String)
    source_ref = Column(String)


class Circular(Base):
    __tablename__ = "circulars"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    week_start = Column(Date)
    source_url = Column(String)
    raw_file_path = Column(String)


class CircularItem(Base):
    __tablename__ = "circular_items"
    id = Column(Integer, primary_key=True, index=True)
    circular_id = Column(Integer, ForeignKey("circulars.id"))
    raw_text = Column(Text)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    price = Column(Numeric(10, 2))
    size = Column(String)


class InstacartItem(Base):
    __tablename__ = "instacart_items"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    url = Column(String)
    raw_text = Column(Text)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    price = Column(Numeric(10, 2))
    size = Column(String)


class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    raw_file_path = Column(String)


class ReceiptItem(Base):
    __tablename__ = "receipt_items"
    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    raw_text = Column(Text)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    price = Column(Numeric(10, 2))


class CrowdSubmission(Base):
    __tablename__ = "crowd_submissions"
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"))
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)
    price = Column(Numeric(10, 2))
    submitted_at = Column(DateTime, default=datetime.utcnow)
