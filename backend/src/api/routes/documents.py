"""Document routes: upload, list, and the uploaded file itself."""

import mimetypes
from datetime import timezone
from pathlib import Path

import filetype
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from src.core.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES
from src.db.session import get_db
from src.models import Document, Record, RecordStatus
from src.services.storage import get_path, save_bytes

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db : Session = Depends(get_db),
    ):

    """
    Accept a land record file, validate it, and store it.

    Raises:
        HTTPException: 413 if too large, 415 if not PDF/JPG/PNG.
    """

    data = await file.read()

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    kind = filetype.guess(data)
    if kind is None or kind.extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Only PDF, JPG, PNG allowed")

    key = save_bytes(data, kind.extension)

    doc = Document(
        original_filename=file.filename,
        storage_key=key,
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "original_filename": doc.original_filename,
        "storage_key": doc.storage_key,
        "status": doc.status.value,
    }


@router.get("")
def list_documents(db: Session = Depends(get_db)):
    """Every uploaded file, newest first, with how many records it produced."""
    needs_review = func.sum(case((Record.status == RecordStatus.needs_review, 1), else_=0))
    rows = db.execute(
        select(Document, func.count(Record.id), needs_review)
        .outerjoin(Record, Record.document_id == Document.id)
        .group_by(Document.id)
        .order_by(Document.created_at.desc(), Document.id.desc())
    ).all()

    return [
        {
            "document_id": doc.id,
            "original_filename": doc.original_filename,
            "status": doc.status.value,
            # SQLite hands back times without a timezone; they are UTC
            "created_at": doc.created_at.replace(tzinfo=timezone.utc).isoformat(),
            "record_count": record_count,
            "needs_review": review_count or 0,
        }
        for doc, record_count, review_count in rows
    ]


@router.get("/{document_id}/file")
def get_document_file(document_id: int, db: Session = Depends(get_db)):
    """
    The uploaded file itself, so the review screen can show the scan next to
    the fields.

    Raises:
        HTTPException: 404 if the document does not exist, or its file is not
        in storage.
    """
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    path = Path(get_path(doc.storage_key))
    if not path.is_file():
        raise HTTPException(status_code=404, detail="The file for this document is not in storage")

    return FileResponse(
        path,
        # the key's extension was sniffed from the bytes at upload; the
        # user's filename was not, so it never decides the type
        media_type=mimetypes.guess_type(path.name)[0],
        filename=doc.original_filename,
        content_disposition_type="inline",   # show in the page, don't download
    )
