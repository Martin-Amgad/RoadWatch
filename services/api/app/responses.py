from collections.abc import Mapping, Sequence

from .detections import detections_to_json
from .domain import Analysis, Detection, Report
from .schemas import (
    AnalysisResponse,
    DetectionSchema,
    ReportCreatedResponse,
    ReportDetailResponse,
    ReportResponse,
)


def to_detection_schemas(detections: Sequence[Detection]) -> list[DetectionSchema]:
    return [DetectionSchema(**item) for item in detections_to_json(detections)]


def to_analysis_response(analysis: Analysis) -> AnalysisResponse:
    return AnalysisResponse(
        analysis_id=analysis.id,
        damage_category=analysis.damage_category,
        confidence=analysis.confidence,
        detections=to_detection_schemas(analysis.detections),
        severity_label=analysis.severity.label,
        severity_score=analysis.severity.score,
    )


def to_created_response(report: Report) -> ReportCreatedResponse:
    return ReportCreatedResponse(
        report_id=report.id,
        created_at=report.created_at,
        damage_category=report.damage_category,
        confidence=report.confidence,
        severity_label=report.severity_label,
        severity_score=report.severity_score,
        status=report.status,
        cluster_id=report.cluster_id,
    )


def to_report_response(report: Report, image_urls: Mapping[str, str]) -> ReportResponse:
    return ReportResponse(**_report_fields(report, image_urls))


def to_report_detail_response(
    report: Report, cluster_mates: Sequence[Report], image_urls: Mapping[str, str]
) -> ReportDetailResponse:
    return ReportDetailResponse(
        **_report_fields(report, image_urls),
        cluster_mates=[to_report_response(mate, image_urls) for mate in cluster_mates],
    )


def _report_fields(report: Report, image_urls: Mapping[str, str]) -> dict:
    return {
        "report_id": report.id,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
        "image_url": image_urls.get(report.image_path),
        "latitude": report.latitude,
        "longitude": report.longitude,
        "description": report.description,
        "damage_category": report.damage_category,
        "confidence": report.confidence,
        "detections": to_detection_schemas(report.detections),
        "severity_label": report.severity_label,
        "severity_score": report.severity_score,
        "status": report.status,
        "cluster_id": report.cluster_id,
    }
