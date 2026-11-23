from collections.abc import Mapping, Sequence
from typing import Protocol
from uuid import UUID

from .domain import (
    Analysis,
    Detection,
    NewAnalysis,
    NewReport,
    Report,
    ReportCoordinate,
    ReportPage,
    ReportQuery,
    ReportStatus,
    SeverityResult,
)


class Detector(Protocol):
    model_version: str

    def warm_up(self) -> None: ...

    def detect(self, image_bytes: bytes) -> Sequence[Detection]: ...


class SeverityScorer(Protocol):
    def score(
        self, detections: Sequence[Detection], image_width: int, image_height: int
    ) -> SeverityResult: ...


class Clusterer(Protocol):
    def cluster(self, coordinates: Sequence[tuple[float, float]]) -> list[int | None]:
        """Return one label per (latitude, longitude) pair, None for unclustered."""
        ...


class ObjectStorage(Protocol):
    def upload(self, path: str, content: bytes, content_type: str) -> None: ...

    def move(self, source_path: str, destination_path: str) -> None: ...

    def delete(self, path: str) -> None: ...

    def signed_urls(self, paths: Sequence[str]) -> dict[str, str]:
        """Return a signed URL per path; paths that cannot be signed are omitted."""
        ...


class AnalysisRepository(Protocol):
    def save_analysis(self, analysis: NewAnalysis) -> Analysis: ...

    def get_analysis(self, analysis_id: UUID) -> Analysis | None: ...


class ReportRepository(Protocol):
    def create_report(self, report: NewReport, consumed_analysis_id: UUID) -> Report:
        """Insert the report and delete its analysis in one transaction."""
        ...

    def list_reports(self, query: ReportQuery) -> ReportPage: ...

    def get_report(self, report_id: UUID) -> Report | None: ...

    def list_cluster_mates(
        self, cluster_id: int, excluding_report_id: UUID
    ) -> list[Report]: ...

    def update_status(self, report_id: UUID, status: ReportStatus) -> Report | None: ...

    def get_all_report_coordinates(self) -> list[ReportCoordinate]: ...

    def write_cluster_labels(self, labels: Mapping[UUID, int | None]) -> None: ...
