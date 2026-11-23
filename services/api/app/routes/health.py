from fastapi import APIRouter, Depends

from ..app_services import AppServices, get_services
from ..schemas import HealthResponse

router = APIRouter(tags=["health"])

HEALTHY_STATUS = "ok"


@router.get("/health", response_model=HealthResponse)
def check_health(services: AppServices = Depends(get_services)) -> HealthResponse:
    return HealthResponse(
        status=HEALTHY_STATUS, model_version=services.detector.model_version
    )
