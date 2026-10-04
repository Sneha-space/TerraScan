"""The LGD check: are the district, tehsil and village real places, each one
inside the one above it?

Checked against the government's Local Government Directory (the
lgd_villages table, filled by scripts/load_lgd.py) by fuzzy matching on the
English names - LGD has English names only.
"""

import logging

from rapidfuzz import fuzz, process, utils
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.constants import EXTRACTOR_STATES, LGD_MATCH_CUTOFF
from src.models import LgdVillage

logger = logging.getLogger(__name__)

# the location levels, top-down. Same names as the record's fields
LGD_LEVELS = ("district", "tehsil", "village")


def state_code_for(extractor: str) -> int | None:
    """
    The LGD state code from the ML's template name: "WB_BN_ROR_V1" -> 19.
    None if the state isn't in EXTRACTOR_STATES.
    """
    return EXTRACTOR_STATES.get(extractor.split("_")[0])


def _places(db: Session, code_col, name_col, *where) -> dict[int, str]:
    """{code: name} of every LGD place matching where."""
    query = select(code_col, name_col).distinct()
    if where:
        query = query.where(*where)
    return dict(db.execute(query).all())


def _best_match(name: str | None, places: dict[int, str]) -> int | None:
    """The code of the place most like name, or None if none reaches LGD_MATCH_CUTOFF."""
    if name is None or not places:
        return None
    match = process.extractOne(
        name,
        places,
        scorer=fuzz.WRatio,
        processor=utils.default_process,  # lower-case and strip punctuation first
        score_cutoff=LGD_MATCH_CUTOFF,
    )
    return match[2] if match else None  # match is (name, score, code)


def match_location(
        db : Session,
        state_code : int | None,
        district : str | None,
        tehsil : str | None,
        village : str | None,
    ) -> dict:
    """
    LGD codes for one location, checked top-down: the district inside the
    state, the tehsil inside that district, the village inside that tehsil.

    Names are English, as the ML read them. Returns
        {"district": 303, "tehsil": 2322, "village": 323061}
    A level that didn't match is None, and so is every level below it - a
    village can't be checked inside a tehsil that wasn't found. A name that
    wasn't read counts as no match.

    state_code None (unknown state) checks the district against all of India.
    """
    codes = dict.fromkeys(LGD_LEVELS)

    in_state = [] if state_code is None else [LgdVillage.state_code == state_code]
    districts = _places(db, LgdVillage.district_code, LgdVillage.district_name, *in_state)
    if not districts:
        logger.warning("no LGD districts for state %s - has scripts.load_lgd been run?", state_code)
    codes["district"] = _best_match(district, districts)
    if codes["district"] is None:
        return codes

    sub_districts = _places(
        db, LgdVillage.sub_district_code, LgdVillage.sub_district_name,
        LgdVillage.district_code == codes["district"],
    )
    codes["tehsil"] = _best_match(tehsil, sub_districts)
    if codes["tehsil"] is None:
        return codes

    villages = _places(
        db, LgdVillage.village_code, LgdVillage.village_name,
        LgdVillage.sub_district_code == codes["tehsil"],
    )
    codes["village"] = _best_match(village, villages)
    return codes
