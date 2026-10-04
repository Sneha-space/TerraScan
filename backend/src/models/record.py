import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.document import Document

class RecordStatus(enum.Enum):
    needs_review = "needs_review"
    auto_approved = "auto_approved"
    verified = "verified"

class Record(Base):
    """
    One land record inside a document.
    """

    __tablename__ = "records"
    __table_args__ = (UniqueConstraint("document_id", "record_number"),)
    id : Mapped[int] = mapped_column(primary_key=True)
    document_id : Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    record_number : Mapped[int]
    page_number : Mapped[int | None]
    dedupe_key : Mapped[str | None] = mapped_column(index=True)
    status : Mapped[RecordStatus] = mapped_column(default=RecordStatus.needs_review)

    # official LGD codes for the record's location, set by the LGD check at
    # ingest. None = no match at that level (and so none below it either)
    lgd_district_code : Mapped[int | None]
    lgd_sub_district_code : Mapped[int | None]
    lgd_village_code : Mapped[int | None]

    document : Mapped["Document"] = relationship()