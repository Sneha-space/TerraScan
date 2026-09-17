"""Application settings.

Single source of truth for paths and limits.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]   # -> backend/

UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024              # 25 MB
ALLOWED_EXTENSIONS = {"pdf", "jpg", "png", "jpeg"}

DATABASE_URL = f"sqlite:///{BASE_DIR/ 'bhoominetra.db'}"
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]