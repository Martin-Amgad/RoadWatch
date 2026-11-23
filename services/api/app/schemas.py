from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, PlainSerializer, field_validator

from .constants import MAX_DESCRIPTION_LENGTH
from .domain import ReportStatus, SeverityLabel

UTC_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def format_utc_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).strftime(UTC_TIMESTAMP_FORMAT)


UtcTimestamp = Annotated[
    datetime, PlainSerializer(format_utc_timestamp, return_type=str)
]


class DetectionSchema(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float] = Field(min_length=4, max_length=4)


class AnalysisResponse(BaseModel):
    analysis_id: UUID
    damage_category: str | None
    confidence: float
    detections: list[DetectionSchema]
    severity_label: SeverityLabel
    severity_score: float


class ReportCreateRequest(BaseModel):
    analysis_id: UUID
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    description: str | None = Field(default=None, max_length=MAX_DESCRIPTION_LENGTH)

    @field_validator("description")
    @classmethod
    def blank_description_becomes_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ReportCreatedResponse(BaseModel):
    report_id: UUID
    created_at: UtcTimestamp
    damage_category: str | None
    confidence: float
    severity_label: SeverityLabel
    severity_score: float
    status: ReportStatus
    cluster_id: int | None


class ReportResponse(BaseModel):
    report_id: UUID
    created_at: UtcTimestamp
    updated_at: UtcTimestamp
    image_url: str | None
    latitude: float
    longitude: float
    description: str | None
    damage_category: str | None
    confidence: float
    detections: list[DetectionSchema]
    severity_label: SeverityLabel
    severity_score: float
    status: ReportStatus
    cluster_id: int | None


class ReportDetailResponse(ReportResponse):
    cluster_mates: list[ReportResponse]


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    limit: int
    offset: int


class StatusUpdateRequest(BaseModel):
    status: ReportStatus


class HealthResponse(BaseModel):
    status: str
    model_version: str


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
