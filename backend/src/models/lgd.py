from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class LgdVillage(Base):
    """
    One village from the government's Local Government Directory (LGD), with
    the sub-district, district and state it sits in.

    Reference data: filled by scripts/load_lgd.py, read by the LGD check,
    never edited by the app. One flat table shaped like the source CSV,
    because it is only ever loaded and read.
    """

    __tablename__ = "lgd_villages"

    village_code : Mapped[int] = mapped_column(primary_key=True)
    village_name : Mapped[str]
    sub_district_code : Mapped[int] = mapped_column(index=True)
    sub_district_name : Mapped[str]
    district_code : Mapped[int] = mapped_column(index=True)
    district_name : Mapped[str]
    state_code : Mapped[int] = mapped_column(index=True)
    state_name : Mapped[str]
