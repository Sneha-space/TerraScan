"""TerraScan API entry point.

Creates the app and mounts routers. Business logic belongs in
src/services/, not here.

Run from backend/:  uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.workers.ml_worker import start_worker,stop_event

from src.core.config import CORS_ORIGINS

from src.api.routes import documents, dashboard, records

from src.db.base import Base
from src.db.session import engine
import src.models  # noqa: F401, registers models with Base



Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app):
    start_worker()
    yield
    stop_event.set()

app = FastAPI(title="TerraScan API",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(records.router)

@app.get("/health")
def health():
    """Liveness check. Used to confirm the server is up."""
    return {"status": "ok"}