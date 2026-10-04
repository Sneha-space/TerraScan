from fastapi import APIRouter, Depends

from sqlalchemy import func, select
from sqlalchemy.orm import Session


from src.db.session import get_db
from src.models import Record, RecordStatus, Document, DocStatus, ExtractField

from src.core.constants import CONFIDENCE_THRESHOLD

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# shown on each dashboard row so records can be told apart at a glance.
# Plots of one document share an owner; the khasra number is what differs.
SUMMARY_FIELDS = ("owner_name", "khasra_number")


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


def _corrections_by_field(db: Session) -> list[dict]:
    """For every field name: how many times an officer checked it (fields of
    verified records) and how many of those they had to correct."""
    rows = db.execute(
        select(
            ExtractField.attribute_name,
            ExtractField.corrected_value,
            ExtractField.corrected_original,
        )
        .join(Record)
        .where(Record.status == RecordStatus.verified)
    ).all()

    counts: dict[str, dict] = {}
    for name, corrected_value, corrected_original in rows:
        entry = counts.setdefault(name, {"name": name, "checked": 0, "corrected": 0})
        entry["checked"] += 1
        if corrected_value is not None or corrected_original is not None:
            entry["corrected"] += 1

    return sorted(counts.values(), key=lambda e: (-e["corrected"], e["name"]))


def _districts(db: Session) -> list[dict]:
    """Records per district, split by status, biggest district first.

    Grouped on the district as written in the document - the English is a
    transliteration and spells the same place several ways.
    """
    rows = db.execute(
        select(
            Record.status,
            ExtractField.corrected_original,
            ExtractField.original_value,
            ExtractField.corrected_value,
            ExtractField.attribute_value,
        )
        .join(Record)
        .where(ExtractField.attribute_name == "district")
    ).all()

    districts: dict[str | None, dict] = {}
    for status, corrected_original, original, corrected_value, english in rows:
        key = corrected_original or original
        entry = districts.setdefault(key, {
            "original": key,
            "value": corrected_value or english,
            "total": 0,
            **{s.value: 0 for s in RecordStatus},
        })
        entry["total"] += 1
        entry[status.value] += 1

    return sorted(districts.values(), key=lambda d: -d["total"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Everything the overview screen shows, in one call."""
    doc_counts = dict(
        db.execute(select(Document.status, func.count()).group_by(Document.status)).all()
    )
    record_counts = dict(
        db.execute(select(Record.status, func.count()).group_by(Record.status)).all()
    )
    by_field = _corrections_by_field(db)

    return {
        "documents": {
            "total": sum(doc_counts.values()),
            **{s.value: doc_counts.get(s, 0) for s in DocStatus},
        },
        "records": {
            "total": sum(record_counts.values()),
            **{s.value: record_counts.get(s, 0) for s in RecordStatus},
        },
        # fields of verified records an officer left exactly as the machine read them
        "accuracy": {
            "fields_checked": sum(e["checked"] for e in by_field),
            "fields_corrected": sum(e["corrected"] for e in by_field),
        },
        "corrections_by_field": by_field,
        "districts": _districts(db),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
    }