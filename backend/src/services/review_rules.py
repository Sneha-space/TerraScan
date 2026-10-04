"""The rule that decides whether a record needs a human.

Used when a record is stored (ingest.py) and when a screen explains why a
record was flagged (record routes), so the two can never disagree.
"""

from src.core.constants import CONFIDENCE_THRESHOLD, CRITICAL_FIELDS
from src.services.lgd import LGD_LEVELS


def _lgd_unmatched(lgd_codes: dict) -> list:
    """
    The first location level LGD couldn't match, e.g. ["district"], or []
    if all matched. Only the first: the levels below it were never checked.
    """
    for level in LGD_LEVELS:
        if lgd_codes.get(level) is None:
            return [level]
    return []


def flag_reasons(values: dict, confidences: dict, lgd_codes: dict) -> dict:
    """
    Why a record needs review. All lists empty means it doesn't.

    values maps field name -> what was read in either language (None = not
    found). confidences maps field name -> score; None means "no score
    given" and never flags on its own. lgd_codes is what the LGD check
    found: {"district": code, "tehsil": code, "village": code}.
    """
    return {
        "missing": [name for name in CRITICAL_FIELDS if values.get(name) is None],
        "low_confidence": [
            name for name, c in confidences.items()
            if c is not None and c < CONFIDENCE_THRESHOLD
        ],
        "lgd_unmatched": _lgd_unmatched(lgd_codes),
    }


def needs_review(values: dict, confidences: dict, lgd_codes: dict) -> bool:
    """
    The flag rule. A record goes to a human if any of:
      - a critical field (CRITICAL_FIELDS) has no value,
      - any field scored below CONFIDENCE_THRESHOLD,
      - its district, tehsil or village doesn't match LGD.
    """
    return any(flag_reasons(values, confidences, lgd_codes).values())


def lgd_codes_of(record) -> dict:
    """A stored record's LGD codes, in the shape match_location() returns."""
    return {
        "district": record.lgd_district_code,
        "tehsil": record.lgd_sub_district_code,
        "village": record.lgd_village_code,
    }


def reasons_for_record(record, fields) -> dict:
    """
    flag_reasons() for a stored record and its field rows.

    Judged on what the machine read, not on a reviewer's corrections, so it
    explains why the record was flagged in the first place.
    """
    values = {f.attribute_name: f.original_value or f.attribute_value for f in fields}
    confidences = {f.attribute_name: f.confidence for f in fields}
    return flag_reasons(values, confidences, lgd_codes_of(record))
