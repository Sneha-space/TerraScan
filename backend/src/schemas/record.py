"""Request/response shapes for the record routes.

These describe JSON going in and out over HTTP. The database shape lives in
src/models/ and is allowed to differ.
"""

from pydantic import BaseModel, model_validator


class FieldCorrection(BaseModel):
    """One field a reviewer fixed on the correction screen.

    Either language or both. A language left out keeps what it had.
    """

    field_id: int
    corrected_value: str | None = None       # English
    corrected_original: str | None = None    # the document's own language

    @model_validator(mode="after")
    def needs_a_value(self):
        if self.corrected_value is None and self.corrected_original is None:
            raise ValueError("send corrected_value, corrected_original, or both")
        return self


class VerifyRequest(BaseModel):
    """Body of POST /records/{record_id}/verify.

    An object wrapping the list rather than a bare list, so extra keys can be
    added later without breaking callers.
    """

    corrections: list[FieldCorrection]
