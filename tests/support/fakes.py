"""In-memory test doubles for the API ports. Used only by tests."""

import math
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from uuid import UUID

from services.api.app.domain import (
    Analysis,
    Detection,
    NewAnalysis,
    NewReport,
    Report,
    ReportCoordinate,
    ReportPage,
    ReportQuery,
    ReportStatus,
    SeverityLabel,
    SeverityResult,
)

EARTH_RADIUS_METERS = 6_371_000.0
FAKE_CLUSTER_RADIUS_METERS = 50.0


class FakeDetector:
    model_version = "test-model-1"

    def __init__(self) -> None:
        self.detections: Sequence[Detection] = ()
        self.was_warmed_up = False

    def warm_up(self) -> None:
        self.was_warmed_up = True

    def detect(self, image_bytes: bytes) -> Sequence[Detection]:
        return self.detections


class FakeSeverityScorer:
    def score(
        self, detections: Sequence[Detection], image_width: int, image_height: int
    ) -> SeverityResult:
        if not detections:
            return SeverityResult(SeverityLabel.NONE, 0.0)
        best_confidence = max(detection.confidence for detection in detections)
        return SeverityResult(SeverityLabel.HIGH, best_confidence)


class FakeClusterer:
    """Groups points within 50 m of each other; singletons get None."""

    def __init__(self) -> None:
        self.should_fail = False

    def cluster(self, coordinates: Sequence[tuple[float, float]]) -> list[int | None]:
        if self.should_fail:
            raise RuntimeError("clustering failed")
        group_of = list(range(len(coordinates)))

        def find(index: int) -> int:
            while group_of[index] != index:
                index = group_of[index]
            return index

        for first in range(len(coordinates)):
            for second in range(first + 1, len(coordinates)):
                if _distance_meters(coordinates[first], coordinates[second]) <= (
                    FAKE_CLUSTER_RADIUS_METERS
                ):
                    group_of[find(second)] = find(first)

        roots = [find(index) for index in range(len(coordinates))]
        labels: dict[int, int] = {}
        result: list[int | None] = []
        for root in roots:
            if roots.count(root) < 2:
                result.append(None)
            else:
                result.append(labels.setdefault(root, len(labels)))
        return result


def _distance_meters(first: tuple[float, float], second: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*first, *second))
    haversine = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_METERS * math.asin(math.sqrt(haversine))


class InMemoryStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.fail_on_upload = False

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        if self.fail_on_upload:
            raise RuntimeError("upload failed")
        self.objects[path] = content

    def move(self, source_path: str, destination_path: str) -> None:
        self.objects[destination_path] = self.objects.pop(source_path)

    def delete(self, path: str) -> None:
        del self.objects[path]

    def signed_urls(self, paths: Sequence[str]) -> dict[str, str]:
        return {
            path: f"https://storage.test/{path}?token=t"
            for path in paths
            if path in self.objects
        }


class InMemoryRepository:
    def __init__(self) -> None:
        self.analyses: dict[UUID, Analysis] = {}
        self.reports: dict[UUID, Report] = {}
        self.fail_on_create_report = False
        self.fail_on_save_analysis = False

    def save_analysis(self, analysis: NewAnalysis) -> Analysis:
        if self.fail_on_save_analysis:
            raise RuntimeError("save failed")
        saved = Analysis(**vars(analysis), created_at=datetime.now(UTC))
        self.analyses[saved.id] = saved
        return saved

    def get_analysis(self, analysis_id: UUID) -> Analysis | None:
        return self.analyses.get(analysis_id)

    def create_report(self, report: NewReport, consumed_analysis_id: UUID) -> Report:
        if self.fail_on_create_report:
            raise RuntimeError("insert failed")
        now = datetime.now(UTC)
        created = Report(
            **vars(report),
            created_at=now,
            updated_at=now,
            status=ReportStatus.SUBMITTED,
            cluster_id=None,
        )
        self.reports[created.id] = created
        del self.analyses[consumed_analysis_id]
        return created

    def list_reports(self, query: ReportQuery) -> ReportPage:
        matching = [
            report
            for report in self.reports.values()
            if (query.category is None or report.damage_category == query.category)
            and (query.status is None or report.status == query.status)
        ]
        matching.sort(key=lambda r: (r.severity_score, r.created_at), reverse=True)
        window = matching[query.offset : query.offset + query.limit]
        return ReportPage(
            items=window, total=len(matching), limit=query.limit, offset=query.offset
        )

    def get_report(self, report_id: UUID) -> Report | None:
        return self.reports.get(report_id)

    def list_cluster_mates(
        self, cluster_id: int, excluding_report_id: UUID
    ) -> list[Report]:
        return [
            report
            for report in self.reports.values()
            if report.cluster_id == cluster_id and report.id != excluding_report_id
        ]

    def update_status(self, report_id: UUID, status: ReportStatus) -> Report | None:
        report = self.reports.get(report_id)
        if report is None:
            return None
        updated = Report(**{**vars(report), "status": status})
        self.reports[report_id] = updated
        return updated

    def get_all_report_coordinates(self) -> list[ReportCoordinate]:
        return [
            ReportCoordinate(report.id, report.latitude, report.longitude)
            for report in self.reports.values()
        ]

    def write_cluster_labels(self, labels: Mapping[UUID, int | None]) -> None:
        for report_id, label in labels.items():
            report = self.reports[report_id]
            self.reports[report_id] = Report(**{**vars(report), "cluster_id": label})
