import logging
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    INVALID_IMAGE_TYPE = "invalid_image_type"
    IMAGE_TOO_LARGE = "image_too_large"
    UNREADABLE_IMAGE = "unreadable_image"
    INVALID_COORDINATES = "invalid_coordinates"
    DESCRIPTION_TOO_LONG = "description_too_long"
    INVALID_REQUEST = "invalid_request"
    ANALYSIS_NOT_FOUND = "analysis_not_found"
    ANALYSIS_EXPIRED = "analysis_expired"
    INVALID_STATUS_TRANSITION = "invalid_status_transition"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"


HTTP_STATUS_BY_CODE: dict[ErrorCode, int] = {
    ErrorCode.INVALID_IMAGE_TYPE: 415,
    ErrorCode.IMAGE_TOO_LARGE: 413,
    ErrorCode.UNREADABLE_IMAGE: 422,
    ErrorCode.INVALID_COORDINATES: 422,
    ErrorCode.DESCRIPTION_TOO_LONG: 422,
    ErrorCode.INVALID_REQUEST: 422,
    ErrorCode.ANALYSIS_NOT_FOUND: 404,
    ErrorCode.ANALYSIS_EXPIRED: 410,
    ErrorCode.INVALID_STATUS_TRANSITION: 409,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL_ERROR: 500,
}

COORDINATE_FIELDS = ("latitude", "longitude")


class ApiError(Exception):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = HTTP_STATUS_BY_CODE[code]


def error_response(code: ErrorCode, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code.value, "message": message}},
    )


def code_for_validation_error(error: dict) -> ErrorCode:
    field = error["loc"][-1]
    if field in COORDINATE_FIELDS:
        return ErrorCode.INVALID_COORDINATES
    if field == "description" and error["type"] == "string_too_long":
        return ErrorCode.DESCRIPTION_TOO_LONG
    return ErrorCode.INVALID_REQUEST


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, error: ApiError) -> JSONResponse:
        return error_response(error.code, error.message, error.status_code)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, error: RequestValidationError
    ) -> JSONResponse:
        first_error = error.errors()[0]
        code = code_for_validation_error(first_error)
        field = first_error["loc"][-1]
        message = f"Invalid value for '{field}': {first_error['msg']}"
        return error_response(code, message, HTTP_STATUS_BY_CODE[code])

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        _: Request, error: StarletteHTTPException
    ) -> JSONResponse:
        code = (
            ErrorCode.NOT_FOUND
            if error.status_code == 404
            else ErrorCode.INVALID_REQUEST
        )
        return error_response(code, str(error.detail), error.status_code)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled error", exc_info=error)
        return error_response(
            ErrorCode.INTERNAL_ERROR,
            "Unexpected server error.",
            HTTP_STATUS_BY_CODE[ErrorCode.INTERNAL_ERROR],
        )
