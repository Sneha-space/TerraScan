"""Hands waiting documents to extraction, and stores what comes back.

get_pending_documents() is the way in; save_document_results() is the way out,
or mark_document_failed() if extraction crashed before producing anything.
The only place records and fields are written. Extraction code returns
plain data; this file stores it.
"""

import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.constants import EXPECTED_FIELDS
from src.db.session import SessionLocal
from src.ml.validator_model import LandRecordExtraction
from src.models import DocStatus, Document, ExtractField, Record, RecordStatus
from src.services.lgd import match_location, state_code_for
from src.services.review_rules import needs_review
from src.services.storage import get_path

logger = logging.getLogger(__name__)

# what the ML returns for every value: (as written, English, confidence)
NOT_FOUND = (None, None, None)

def _clean(value) -> str | None:
    """
    Clean a string value by stripping whitespace and converting empty strings to None.
    """
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _join(items: list) -> tuple:
    """
    A list of ML values as one value, e.g. "95, 425".

    The confidence is the lowest in the list, so one bad read still flags the
    record. An empty list means the plot simply has none - not a failed read -
    so it gets no confidence and does not flag.
    """
    if not items:
        return NOT_FOUND
    originals = [i[0] for i in items if i[0] is not None]
    english = [i[1] for i in items if i[1] is not None]
    scores = [i[2] for i in items if i[2] is not None]
    return (
        ", ".join(originals) or None,
        ", ".join(english) or None,
        min(scores) if scores else None,
    )


def _document_fields(data: dict) -> dict:
    """The values that describe the whole document, by field name."""
    owner = data["landowner_details"]
    ownership = data["ownership_details"]
    registration = data["registration_information"]
    return {
        "owner_name": owner["name"],
        "guardian_name": owner["guardian"],
        "owner_address": owner["address"],
        "khata_number": data["khata_number"],
        "total_holding_area": data["plot_area"]["total_holding_area_dec"],
        "village": data["village"],
        "tehsil": data["tehsil"],
        "district": data["district"],
        "tenure_type": ownership["tenure_type"],
        "total_plots": ownership["total_plots"],
        # a flag the ML sets ("found" / "not_found"), not text read off the
        # page - so English only, and no score
        "mutation_status": (None, data["mutation_records"], None),
        "registration_statement": registration["statement"],
        "copy_number": registration["copy_no"],
        "certification_date": registration["certification_date"],
        "signed_by": registration["signed_by"],
        "fees_received": registration["fees_received"],
    }


def _plot_fields(plot: dict) -> dict:
    """The values that describe one plot, by field name."""
    return {
        "khasra_number": plot["plot_no"],
        "plot_area": plot["total_plot_area"],
        "occupier_share": plot["occupier_share"],
        "share_area": plot["share_area"],
        "land_classification": plot["land_classification"],
        "previous_khata_numbers": _join(plot["previous_khata_numbers"]),
    }


def add_record(
        db : Session,
        document_id : int,
        record_number : int,
        page_number : int | None,
        result : dict,
        lgd_codes : dict,
    ) -> Record:
    """
    Add one new record and it's fields to the session. Does not commit.

    result maps field name -> (as written, English, confidence). A name
    missing from result is stored as not found. lgd_codes is what
    match_location() returned for the record's location.
    """

    unknown = set(result) - set(EXPECTED_FIELDS)
    if unknown:
        logger.warning("ignored unknown field names : %s", sorted(unknown))

    triples = {}
    for name in EXPECTED_FIELDS:
        original, english, confidence = result.get(name) or NOT_FOUND
        triples[name] = (_clean(original), _clean(english), confidence)

    # a field counts as found if it was read in either language
    values = {name: t[0] or t[1] for name, t in triples.items()}
    confidences = {name: t[2] for name, t in triples.items()}

    if needs_review(values, confidences, lgd_codes):
        status = RecordStatus.needs_review
    else:
        status = RecordStatus.auto_approved

    record = Record(
        document_id=document_id,
        record_number=record_number,
        page_number=page_number,
        status=status,
        lgd_district_code=lgd_codes["district"],
        lgd_sub_district_code=lgd_codes["tehsil"],
        lgd_village_code=lgd_codes["village"],
    )
    db.add(record)
    db.flush()  # gives record.id now; still undone by a rollback

    for name, (original, english, confidence) in triples.items():
        db.add(
            ExtractField(
                record_id=record.id,
                attribute_name=name,
                attribute_value=english,
                original_value=original,
                confidence=confidence,
            )
        )

    return record


def get_pending_documents() -> list[dict]:
    """
    Every document still waiting for extraction, oldest first.

    Returns plain dicts, so the caller never needs the database:
        [{"document_id": 5, "path": "E:/.../uploads/d58c....pdf", "file_type": "pdf"}, ...]

    After processing one, pass its document_id to save_document_results(),
    which moves it to done or failed so it drops off this list.
    """
    db = SessionLocal()
    try:
        docs = db.scalars(
            select(Document)
            .where(Document.status == DocStatus.processing)
            .order_by(Document.id)
        ).all()
        return [
            {
                "document_id": doc.id,
                "path": get_path(doc.storage_key),
                "file_type": Path(doc.storage_key).suffix.lstrip("."),  # "pdf" / "jpg" / "png"
            }
            for doc in docs
        ]
    finally:
        db.close()


def save_document_results(document_id : int, extraction : dict) -> None:
    """
    Store one document's ML output, all or nothing.

    extraction is the ML output as-is - the shape of LandRecordExtraction in
    src/ml/validator_model.py. Each plot becomes one record, and the values
    that describe the whole document (owner, khata, village, ...) are copied
    onto every one of them.

    On any error - including output that doesn't match LandRecordExtraction -
    nothing is saved, the document is marked failed, and the error is raised
    again.
    """
    db = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if doc is None:
            raise ValueError(f"document {document_id} does not exist")

        validated = LandRecordExtraction.model_validate(extraction).model_dump()
        data = validated["data"]
        shared = _document_fields(data)

        # the location is the same on every plot, so it is checked once per
        # file. LGD names are English: the second value of each triple
        lgd_codes = match_location(
            db,
            state_code=state_code_for(validated["extractor"]),
            district=_clean(shared["district"][1]),
            tehsil=_clean(shared["tehsil"][1]),
            village=_clean(shared["village"][1]),
        )

        # no plots found still makes one record, so the document reaches a
        # reviewer instead of finishing with nothing to look at
        plots = data["plot_area"]["per_plot"] or [None]

        for record_number, plot in enumerate(plots, start=1):
            result = shared | (_plot_fields(plot) if plot else {})
            # the ML reads the whole document at once, so no page number
            add_record(db, document_id, record_number, None, result, lgd_codes)

        doc.status = DocStatus.done
        db.commit()

    except Exception:
        db.rollback()
        doc = db.get(Document, document_id)
        if doc is not None:
            doc.status = DocStatus.failed
            db.commit()
        raise

    finally:
        db.close()


def mark_document_failed(document_id : int) -> None:
    """
    Mark a document failed when extraction crashed before producing output.

    Call it from the worker's except. Without it, a file that breaks the ML
    stays on get_pending_documents(), gets picked up again, and crashes again
    forever. (save_document_results already does this for output it can't
    store, so it isn't needed after that.)
    """
    db = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if doc is None:
            raise ValueError(f"document {document_id} does not exist")
        doc.status = DocStatus.failed
        db.commit()
        logger.warning("document %s marked failed", document_id)
    finally:
        db.close()


if __name__ == "__main__":
    # quick test
    print(get_pending_documents())