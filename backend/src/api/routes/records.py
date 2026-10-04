from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.constants import CONFIDENCE_THRESHOLD, CRITICAL_FIELDS
from src.db.session import get_db
from src.models import Document, ExtractField, Record, RecordStatus
from src.schemas.record import VerifyRequest
from src.services.review_rules import lgd_codes_of, reasons_for_record

router = APIRouter(prefix="/records", tags=["records"])

# shown on every list row - enough to tell plots of one file apart and find them
LIST_FIELDS = ("khasra_number", "owner_name", "village", "district", "plot_area")


def _display(field: ExtractField | None) -> dict:
    """What a screen should show for one field, in both languages."""
    if field is None:
        return {"value": None, "original": None}
    return {
        "value": field.corrected_value or field.attribute_value,
        "original": field.corrected_original or field.original_value,
    }


@router.get("")
def list_records(
    status: RecordStatus | None = None,
    document_id: int | None = None,
    limit: int | None = Query(None, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Records, oldest first, with the values a list needs and why each one
    was flagged.

    Filter by status (e.g. the review queue) or by document_id (every plot
    of one file).
    """
    query = (
        select(Record, Document.original_filename)
        .join(Document)
        .order_by(Record.document_id, Record.record_number)
    )
    if status is not None:
        query = query.where(Record.status == status)
    if document_id is not None:
        query = query.where(Record.document_id == document_id)
    if limit is not None:
        query = query.limit(limit)
    rows = db.execute(query).all()

    # one query for the fields of every record on the list, not one per record
    fields_by_record = defaultdict(list)
    record_ids = [record.id for record, _ in rows]
    if record_ids:
        fields = db.scalars(
            select(ExtractField).where(ExtractField.record_id.in_(record_ids))
        )
        for f in fields:
            fields_by_record[f.record_id].append(f)

    result = []
    for record, filename in rows:
        fields = fields_by_record[record.id]
        by_name = {f.attribute_name: f for f in fields}
        result.append({
            "record_id": record.id,
            "record_number": record.record_number,
            "document_id": record.document_id,
            "filename": filename,
            "status": record.status.value,
            "values": {name: _display(by_name.get(name)) for name in LIST_FIELDS},
            "flags": reasons_for_record(record, fields),
        })
    return result


@router.get("/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db)):

    record = db.get(Record, record_id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    fields = db.scalars(
    select(ExtractField).where(ExtractField.record_id == record_id)
    ).all()

    return {
    "record_id": record.id,
    "record_number": record.record_number,
    "document_id": record.document_id,
    "page_number": record.page_number,
    "status": record.status.value,
    "filename": record.document.original_filename,
    "flags": reasons_for_record(record, fields),
    "lgd_codes": lgd_codes_of(record),
    "confidence_threshold": CONFIDENCE_THRESHOLD,
    "critical_fields": CRITICAL_FIELDS,
    "fields": [
    {
        "field_id": f.id,
        "name": f.attribute_name,
        "value": f.attribute_value,
        "corrected_value": f.corrected_value,
        "display_value": f.corrected_value or f.attribute_value,
        "original_value": f.original_value,
        "corrected_original": f.corrected_original,
        "display_original": f.corrected_original or f.original_value,
        "confidence": f.confidence,
        }for f in fields
    ]
    }


@router.post("/{record_id}/verify")
def verify_record(
    record_id: int,
    body: VerifyRequest,
    db: Session = Depends(get_db),
    ):
    """
    Save a reviewer's corrections for one record and mark it verified.

    Corrections go into corrected_value (English) and corrected_original (the
    document's language); the extracted values are never overwritten.
    An empty corrections list is valid — it means the reviewer read the record
    and accepted it as extracted.

    Raises:
        HTTPException: 404 if the record does not exist, 400 if a field_id
        does not belong to this record.
    """

    record = db.get(Record, record_id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    fields = db.scalars(
        select(ExtractField).where(ExtractField.record_id == record_id)
    ).all()

    by_id = {f.id: f for f in fields}

    for item in body.corrections:
        field = by_id.get(item.field_id)

        # stops a correction being written onto another record's field
        if field is None:
            raise HTTPException(
                status_code=400,
                detail=f"field {item.field_id} does not belong to record {record_id}",
            )

        if item.corrected_value is not None:
            field.corrected_value = item.corrected_value
        if item.corrected_original is not None:
            field.corrected_original = item.corrected_original

    record.status = RecordStatus.verified

    # nothing above touched the database until this line, so a bad field_id
    # leaves the record completely unchanged
    db.commit()

    return {
        "record_id": record.id,
        "status": record.status.value,
        "corrected_count": len(body.corrections),
    }
