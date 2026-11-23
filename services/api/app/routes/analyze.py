from fastapi import APIRouter, Depends, File, UploadFile

from ..app_services import AppServices, get_services
from ..image_validation import read_upload_within_limit, validate_image
from ..responses import to_analysis_response
from ..schemas import AnalysisResponse, ErrorResponse

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def analyze_image(
    image: UploadFile = File(...),
    services: AppServices = Depends(get_services),
) -> AnalysisResponse:
    content = read_upload_within_limit(image)
    validated_image = validate_image(content)
    analysis = services.analysis_service.analyze(validated_image)
    return to_analysis_response(analysis)
