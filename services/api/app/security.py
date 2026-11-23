import hmac

from fastapi import Header, Request

from .constants import STAFF_API_KEY_HEADER
from .errors import ApiError, ErrorCode


def require_staff_key(
    request: Request,
    provided_key: str | None = Header(default=None, alias=STAFF_API_KEY_HEADER),
) -> None:
    expected_key: str = request.app.state.settings.staff_api_key
    if provided_key is None or not hmac.compare_digest(
        provided_key.encode(), expected_key.encode()
    ):
        raise ApiError(ErrorCode.UNAUTHORIZED, "Missing or invalid staff API key.")
