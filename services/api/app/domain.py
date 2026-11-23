from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class ReportStatus(str, Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    RESOLVED = "Resolved"


class SeverityLabel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    NONE = "None"


STATUS_TRANSITIONS: dict[ReportStatus, ReportStatus] = {
    ReportStatus.SUBMITTED: ReportStatus.UNDER_REVIEW,
    ReportStatus.UNDER_REVIEW: ReportStatus.RESOLVED,
}


def is_allowed_transition(current: ReportStatus, target: ReportStatus) -> bool:
    return STATUS_TRANSITIONS.get(current) == target


@dataclass(frozen=True)
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class SeverityResult:
    label: SeverityLabel
    score: float


@dataclass(frozen=True)
class NewAnalysis:
    id: UUID
    image_path: str
    image_width: int
    image_height: int
    detections: Sequence[Detection]
    damage_category: str | None
    confidence: float
    severity: SeverityResult


@dataclass(frozen=True)
class Analysis(NewAnalysis):
    created_at: datetime


@dataclass(frozen=True)
class NewReport:
    id: UUID
    image_path: str
    latitude: float
    longitude: float
    description: str | None
    damage_category: str | None
    confidence: float
    detections: Sequence[Detection]
    severity_label: SeverityLabel
    severity_score: float


@dataclass(frozen=True)
class Report(NewReport):
    created_at: datetime
    updated_at: datetime
    status: ReportStatus
    cluster_id: int | None


@dataclass(frozen=True)
class ReportQuery:
    category: str | None
    status: ReportStatus | None
    limit: int
    offset: int


@dataclass(frozen=True)
class ReportPage:
    items: Sequence[Report]
    total: int
    limit: int
    offset: int


@dataclass(frozen=True)
class ReportCoordinate:
    report_id: UUID
    latitude: float
    longitude: float


@dataclass(frozen=True)
class ReportDetail:
    report: Report
    cluster_mates: Sequence[Report]
