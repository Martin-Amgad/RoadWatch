import pytest

from infra.db.validation import (
    validate_coordinates,
    validate_limit_offset,
    validate_radius,
    validate_severity,
    validate_status,
    validate_uuid,
)


def test_valid_coordinates():
    validate_coordinates(30.0444, 31.2357)
    validate_coordinates(-90, 180)


@pytest.mark.parametrize('lat,lon', [
    (91, 10), (-91, 10), (12, 181), (12, -181),
    (float('nan'), 5), (float('inf'), 5), ('30', 31), (True, 10),
])
def test_invalid_coordinates(lat, lon):
    with pytest.raises(ValueError):
        validate_coordinates(lat, lon)


@pytest.mark.parametrize('severity', ['high', 'medium', 'low', 'none'])
def test_valid_severities(severity):
    validate_severity(severity)


def test_invalid_severity():
    with pytest.raises(ValueError):
        validate_severity('critical')


@pytest.mark.parametrize('status', ['submitted', 'under_review', 'resolved'])
def test_valid_statuses(status):
    validate_status(status)


def test_invalid_status():
    with pytest.raises(ValueError):
        validate_status('deleted')


def test_limit_offset():
    validate_limit_offset(100, 0)
    with pytest.raises(ValueError):
        validate_limit_offset(0, 0)
    with pytest.raises(ValueError):
        validate_limit_offset(100, -1)


def test_radius():
    validate_radius(100)
    with pytest.raises(ValueError):
        validate_radius(0)
    with pytest.raises(ValueError):
        validate_radius(float('nan'))


def test_uuid():
    assert str(validate_uuid('f07c24bf-7498-49a8-9172-900c6ff92110')) == 'f07c24bf-7498-49a8-9172-900c6ff92110'
    with pytest.raises(ValueError):
        validate_uuid('not-a-uuid')
