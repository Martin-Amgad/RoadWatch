from datetime import timedelta

API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
STAFF_API_KEY_HEADER = "X-API-Key"

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_DESCRIPTION_LENGTH = 500

ALLOWED_IMAGE_FORMATS: dict[str, tuple[str, str]] = {
    "JPEG": ("image/jpeg", "jpg"),
    "PNG": ("image/png", "png"),
}

ANALYSIS_TTL = timedelta(hours=24)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

SIGNED_URL_TTL_SECONDS = 3600
PENDING_PREFIX = "pending"
REPORTS_PREFIX = "reports"

DAMAGE_CATEGORY_PRIORITY: tuple[str, ...] = (
    "pothole",
    "alligator_crack",
    "transverse_crack",
    "longitudinal_crack",
)

WARM_UP_IMAGE_SIZE_PX = 64
