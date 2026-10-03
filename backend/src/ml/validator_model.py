from typing import Optional, List, Tuple, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


TextPair = Tuple[Optional[str], Optional[str], Optional[float]]

ClassificationValue = Tuple[
    Optional[str],
    Optional[str],
    float
]



class LandOwnerDetails(BaseModel):
    name: TextPair
    guardian: TextPair
    address: TextPair



class PlotInfo(BaseModel):
    plot_no: TextPair

    total_plot_area: TextPair

    occupier_share: TextPair

    share_area: TextPair

    previous_khata_numbers: List[TextPair] = Field(
        default_factory=list
    )

    land_classification: ClassificationValue



class PlotArea(BaseModel):
    total_holding_area_dec: TextPair

    per_plot: List[PlotInfo]

class OwnershipDetails(BaseModel):
    tenure_type: TextPair
    total_plots: TextPair


class RegistrationInformation(BaseModel):
    statement: TextPair
    copy_no: TextPair
    certification_date: TextPair
    signed_by: TextPair
    fees_received: TextPair


class ExtractedData(BaseModel):
    landowner_details: LandOwnerDetails

    khasra_number: List[TextPair]

    khata_number: TextPair

    plot_area: PlotArea

    village: TextPair

    tehsil: TextPair

    district: TextPair

    ownership_details: OwnershipDetails

    mutation_records: Literal["found", "not_found", "info_required"]

    registration_information: RegistrationInformation



class LandRecordExtraction(BaseModel):
    extractor: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    data: ExtractedData

    model_config = ConfigDict(
        extra="forbid"
    )

    @field_validator("extractor")
    @classmethod
    def validate_extractor(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("extractor cannot be empty")

        return value