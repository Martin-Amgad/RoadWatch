import math
from uuid import UUID

VALID_SEVERITIES = frozenset({'none', 'low', 'medium', 'high'})
VALID_STATUSES = frozenset({'submitted', 'under_review', 'resolved'})


def validate_coordinates(latitude, longitude):
    for name, value, lower, upper in (
        ('latitude', latitude, -90.0, 90.0),
        ('longitude', longitude, -180.0, 180.0),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f'{name} must be numeric')
        if not math.isfinite(value) or not lower <= value <= upper:
            raise ValueError(f'{name} must be between {lower:g} and {upper:g}')


def validate_severity(severity):
    if severity not in VALID_SEVERITIES:
        raise ValueError('severity must be none, low, medium, or high')


def validate_status(status):
    if status not in VALID_STATUSES:
        raise ValueError('status must be submitted, under_review, or resolved')


def validate_uuid(value):
    try:
        return UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError('invalid report UUID') from exc


def validate_limit_offset(limit, offset):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError('limit must be an integer between 1 and 500')
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError('offset must be a nonnegative integer')


def validate_radius(radius_m):
    if isinstance(radius_m, bool) or not isinstance(radius_m, (int, float)):
        raise ValueError('radius_m must be numeric')
    if not math.isfinite(radius_m) or not 0 < radius_m <= 50000:
        raise ValueError('radius_m must be greater than zero and at most 50000')
