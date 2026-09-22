from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from sqlalchemy import func, select, and_, or_
from sqlalchemy.orm import Session


from src.db.session import get_db
from src.models import Record, RecordStatus, Document, ExtractField

from src.core.constants import CONFIDENCE_THRESHOLD

import filetype
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# shown on each dashboard row so records can be told apart at a glance
SUMMARY_FIELDS = ("owner_name", "khasra_number", "survey_number")


def _summary_values(db: Session, status: RecordStatus) -> dict[int, dict]:
    """SUMMARY_FIELDS for every record with this status, keyed by record id.

    One query for the whole list, not one per record. Uses the same display
    rule as GET /records/{id}: corrected value if a human typed one, else the
    extracted value.
    """
    rows = db.execute(
        select(
            ExtractField.record_id,
            ExtractField.attribute_name,
            ExtractField.attribute_value,
            ExtractField.corrected_value,
        )
        .join(Record)
        .where(
            Record.status == status,
            ExtractField.attribute_name.in_(SUMMARY_FIELDS),
        )
    ).all()

    summaries: dict[int, dict] = {}
    for r in rows:
        summaries.setdefault(r.record_id, {})[r.attribute_name] = (
            r.corrected_value or r.attribute_value
        )
    return summaries


def _records_with_status(db: Session, status: RecordStatus) -> list[dict]:
    """Dashboard rows for one status: record number, source file, page, plus
    the SUMMARY_FIELDS values (None when not found)."""
    rows = db.execute(
        select(
            Record.id,
            Record.record_number,
            Record.page_number,
            Document.original_filename,
        )
        .join(Document)
        .where(Record.status == status)
    ).all()

    summaries = _summary_values(db, status)

    return [
        {
            "record_id": r.id,
            "record_number": r.record_number,
            "page_number": r.page_number,
            "filename": r.original_filename,
            # a record missing a field row entirely still gets the key, as None
            **{name: summaries.get(r.id, {}).get(name) for name in SUMMARY_FIELDS},
        }
        for r in rows
    ]


@router.get("")
def get_dashboard(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Record.status, func.count()).group_by(Record.status)
    ).all()

    return {
        "status_counts": {status.value: count for status, count in rows},
        "needs_review": _records_with_status(db, RecordStatus.needs_review),
        "auto_approved": _records_with_status(db, RecordStatus.auto_approved),
        "verified": _records_with_status(db, RecordStatus.verified),
    }