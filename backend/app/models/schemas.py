from pydantic import BaseModel
from typing import Optional

class Store(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    active: bool = True

class Product(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    normalized_unit: Optional[str] = None

class PriceObservation(BaseModel):
    product_id: int
    store_id: int
    price: float
    date: str
    source_type: str
