import logging
import threading
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from ..constants import ANALYSIS_TTL, REPORTS_PREFIX
from ..domain import (
    Analysis,
    NewReport,
    Report,
    ReportDetail,
    ReportPage,
    ReportQuery,
    ReportStatus,
    is_allowed_transition,
)
from ..errors import ApiError, ErrorCode
from ..ports import AnalysisRepository, Clusterer, ObjectStorage, ReportRepository

logger = logging.getLogger(__name__)

Clock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(UTC)


class ReportService:
    def __init__(
        self,
        reports: ReportRepository,
        analyses: AnalysisRepository,
        storage: ObjectStorage,
        clusterer: Clusterer,
        clock: Clock = utc_now,
    ) -> None:
        self._reports = reports
        self._analyses = analyses
        self._storage = storage
        self._clusterer = clusterer
        self._clock = clock
        self._cluster_lock = threading.Lock()

    def create_report(
        self,
        analysis_id: UUID,
        latitude: float,
        longitude: float,
        description: str | None,
    ) -> Report:
        analysis = self._load_usable_analysis(analysis_id)
        report_id = uuid4()
        report_image_path = f"{REPORTS_PREFIX}/{report_id}.{_extension_of(analysis)}"
        new_report = NewReport(
            id=report_id,
            image_path=report_image_path,
            latitude=latitude,
            longitude=longitude,
            description=description,
            damage_category=analysis.damage_category,
            confidence=analysis.confidence,
            detections=analysis.detections,
            severity_label=analysis.severity.label,
            severity_score=analysis.severity.score,
        )

        self._storage.move(analysis.image_path, report_image_path)
        try:
            created = self._reports.create_report(new_report, analysis.id)
        except Exception:
            self._restore_pending_image(report_image_path, analysis.image_path)
            raise

        self._recompute_clusters_safely()
        return self._reports.get_report(created.id) or created

    def list_reports(self, query: ReportQuery) -> ReportPage:
        return self._reports.list_reports(query)

    def get_report_detail(self, report_id: UUID) -> ReportDetail:
        report = self._get_report_or_raise(report_id)
        mates = (
            self._reports.list_cluster_mates(report.cluster_id, report.id)
            if report.cluster_id is not None
            else []
        )
        return ReportDetail(report=report, cluster_mates=mates)

    def update_status(self, report_id: UUID, target: ReportStatus) -> Report:
        report = self._get_report_or_raise(report_id)
        if not is_allowed_transition(report.status, target):
            raise ApiError(
                ErrorCode.INVALID_STATUS_TRANSITION,
                f"Cannot change status from '{report.status.value}' to '{target.value}'.",
            )
        updated = self._reports.update_status(report_id, target)
        if updated is None:
            raise ApiError(ErrorCode.NOT_FOUND, "Report does not exist.")
        return updated

    def image_urls(self, image_paths: Sequence[str]) -> dict[str, str]:
        return self._storage.signed_urls(list(image_paths))

    def _load_usable_analysis(self, analysis_id: UUID) -> Analysis:
        analysis = self._analyses.get_analysis(analysis_id)
        if analysis is None:
            raise ApiError(ErrorCode.ANALYSIS_NOT_FOUND, "Analysis does not exist.")
        if self._clock() - analysis.created_at > ANALYSIS_TTL:
            raise ApiError(
                ErrorCode.ANALYSIS_EXPIRED,
                "Analysis is too old. Analyze the image again.",
            )
        return analysis

    def _get_report_or_raise(self, report_id: UUID) -> Report:
        report = self._reports.get_report(report_id)
        if report is None:
            raise ApiError(ErrorCode.NOT_FOUND, "Report does not exist.")
        return report

    def _restore_pending_image(self, report_path: str, pending_path: str) -> None:
        try:
            self._storage.move(report_path, pending_path)
        except Exception:
            logger.exception("Could not restore %s to %s", report_path, pending_path)

    def _recompute_clusters_safely(self) -> None:
        try:
            self._recompute_clusters()
        except Exception:
            logger.exception("Cluster recompute failed; report kept without cluster")

    def _recompute_clusters(self) -> None:
        with self._cluster_lock:
            coordinates = self._reports.get_all_report_coordinates()
            labels = self._clusterer.cluster(
                [(item.latitude, item.longitude) for item in coordinates]
            )
            self._reports.write_cluster_labels(
                {item.report_id: label for item, label in zip(coordinates, labels)}
            )


def _extension_of(analysis: Analysis) -> str:
    return analysis.image_path.rsplit(".", 1)[-1]
