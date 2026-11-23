from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi import Request

from .ports import Detector
from .services.analysis_service import AnalysisService
from .services.report_service import ReportService


def _do_nothing() -> None:
    return None


@dataclass(frozen=True)
class AppServices:
    analysis_service: AnalysisService
    report_service: ReportService
    detector: Detector
    shutdown: Callable[[], None] = field(default=_do_nothing)


def get_services(request: Request) -> AppServices:
    return request.app.state.services
