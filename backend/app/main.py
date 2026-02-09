from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.db import engine
from app.models.orm import Base
from app.services.crud import ensure_store_seed
from app.db import SessionLocal

app = FastAPI(title="CUFPI Food Price Tool", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_store_seed(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"status": "ok", "message": "CUFPI backend running"}
