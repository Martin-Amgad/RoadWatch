from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..app_services import AppServices, get_services
from ..constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ..domain import ReportQuery, ReportStatus
from ..responses import (
    to_created_response,
    to_report_detail_response,
    to_report_response,
)
from ..schemas import (
    ErrorResponse,
    ReportCreatedResponse,
    ReportCreateRequest,
    ReportDetailResponse,
    ReportListResponse,
    ReportResponse,
    StatusUpdateRequest,
)
from ..security import require_staff_key

router = APIRouter(tags=["reports"])

STAFF_ERRORS = {401: {"model": ErrorResponse}}


@router.post(
    "/reports",
    response_model=ReportCreatedResponse,
    status_code=201,
    responses={
        404: {"model": ErrorResponse},
        410: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_report(
    request: ReportCreateRequest,
    services: AppServices = Depends(get_services),
) -> ReportCreatedResponse:
    report = services.report_service.create_report(
        analysis_id=request.analysis_id,
        latitude=request.latitude,
        longitude=request.longitude,
        description=request.description,
    )
    return to_created_response(report)


@router.get(
    "/reports",
    response_model=ReportListResponse,
    dependencies=[Depends(require_staff_key)],
    responses=STAFF_ERRORS,
)
def list_reports(
    category: str | None = Query(default=None),
    report_status: ReportStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    offset: int = Query(default=0, ge=0),
    services: AppServices = Depends(get_services),
) -> ReportListResponse:
    query = ReportQuery(
        category=category, status=report_status, limit=limit, offset=offset
    )
    page = services.report_service.list_reports(query)
    image_urls = services.report_service.image_urls(
        [report.image_path for report in page.items]
    )
    return ReportListResponse(
        items=[to_report_response(report, image_urls) for report in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get(
    "/reports/{report_id}",
    response_model=ReportDetailResponse,
    dependencies=[Depends(require_staff_key)],
    responses={**STAFF_ERRORS, 404: {"model": ErrorResponse}},
)
def get_report(
    report_id: UUID,
    services: AppServices = Depends(get_services),
) -> ReportDetailResponse:
    detail = services.report_service.get_report_detail(report_id)
    paths = [
        detail.report.image_path,
        *(mate.image_path for mate in detail.cluster_mates),
    ]
    image_urls = services.report_service.image_urls(paths)
    return to_report_detail_response(detail.report, detail.cluster_mates, image_urls)


@router.patch(
    "/reports/{report_id}/status",
    response_model=ReportResponse,
    dependencies=[Depends(require_staff_key)],
    responses={
        **STAFF_ERRORS,
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def update_report_status(
    report_id: UUID,
    request: StatusUpdateRequest,
    services: AppServices = Depends(get_services),
) -> ReportResponse:
    report = services.report_service.update_status(report_id, request.status)
    image_urls = services.report_service.image_urls([report.image_path])
    return to_report_response(report, image_urls)
