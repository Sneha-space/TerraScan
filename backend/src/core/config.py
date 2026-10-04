"""
Application settings.
Single source of truth for paths and limits.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]   # -> backend/

UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024              # 25 MB
ALLOWED_EXTENSIONS = {"pdf", "jpg", "png", "jpeg"}

DATABASE_URL = f"sqlite:///{BASE_DIR/ 'bhoominetra.db'}"

# Government list of every village in India (Local Government Directory, via
# dataful.in). Loaded into the database by scripts/load_lgd.py.
LGD_CSV_PATH = BASE_DIR / "data" / "lgd" / "lgd_villages_2026-07-02.csv"

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]
