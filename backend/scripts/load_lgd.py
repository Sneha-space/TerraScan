"""Loads the LGD village list (LGD_CSV_PATH) into the lgd_villages table.

Run from backend/ once on every new machine, and again after deleting
bhoominetra.db:

    python -m scripts.load_lgd

Replaces whatever the table holds, all or nothing, so running it twice is safe.
"""

import csv
import time

from sqlalchemy import delete, insert

from src.core.config import LGD_CSV_PATH
from src.db.base import Base
from src.db.session import SessionLocal, engine
from src.models import LgdVillage

BATCH_SIZE = 10_000


def read_villages(path):
    """One dict per CSV row, in the table's column names."""
    # the csv module, not split(","): some names contain commas and are quoted
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            yield {
                "village_code": int(row["village_code"]),
                "village_name": row["village_name"].strip(),
                "sub_district_code": int(row["sub-district_code"]),
                "sub_district_name": row["sub-district_name"].strip(),
                "district_code": int(row["district_code"]),
                "district_name": row["district_name"].strip(),
                "state_code": int(row["state_code"]),
                "state_name": row["state_name"].strip(),
            }


def main():
    # makes the tables if the server has never run on this machine
    Base.metadata.create_all(bind=engine)

    start = time.perf_counter()
    db = SessionLocal()
    try:
        db.execute(delete(LgdVillage))
        batch, total = [], 0
        for village in read_villages(LGD_CSV_PATH):
            batch.append(village)
            if len(batch) == BATCH_SIZE:
                db.execute(insert(LgdVillage), batch)
                total += len(batch)
                batch = []
        if batch:
            db.execute(insert(LgdVillage), batch)
            total += len(batch)
        db.commit()  # nothing is kept unless every row went in
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"loaded {total:,} villages in {time.perf_counter() - start:.0f}s")


if __name__ == "__main__":
    main()
