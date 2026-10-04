from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

class ExtractField(Base):
    """
    One extracted value belongs to a record.

    Every value is kept in two languages: as written in the document (Bengali,
    Hindi, ...) and in English. A reviewer can correct either one. The extracted
    values themselves are never overwritten.
    """

    __tablename__ = "fields"

    id : Mapped[int] = mapped_column(primary_key=True)
    record_id : Mapped[int] = mapped_column(ForeignKey("records.id"), index=True)
    attribute_name : Mapped[str]
    attribute_value : Mapped[str | None]        # English
    corrected_value : Mapped[str | None]        # reviewer's fix to the English
    original_value : Mapped[str | None]         # as written in the document
    corrected_original : Mapped[str | None]     # reviewer's fix to original_value
    confidence : Mapped[float | None]
