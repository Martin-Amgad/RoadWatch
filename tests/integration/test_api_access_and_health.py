from uuid import uuid4

import pytest

from tests.support.backend import DASHBOARD_ORIGIN, Backend
from tests.support.builders import analyze_and_submit, make_detection

STAFF_ENDPOINTS = [
    ("GET", "/api/v1/reports"),
    ("GET", f"/api/v1/reports/{uuid4()}"),
    ("PATCH", f"/api/v1/reports/{uuid4()}/status"),
]


@pytest.mark.parametrize(("method", "url"), STAFF_ENDPOINTS)
def test_staff_endpoints_reject_missing_key(
    backend: Backend, method: str, url: str
) -> None:
    response = backend.client.request(method, url, json={"status": "Under Review"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


@pytest.mark.parametrize(("method", "url"), STAFF_ENDPOINTS)
def test_staff_endpoints_reject_wrong_key(
    backend: Backend, method: str, url: str
) -> None:
    response = backend.client.request(
        method, url, json={"status": "Under Review"}, headers={"X-API-Key": "wrong"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_citizen_endpoints_need_no_key(backend: Backend) -> None:
    created = analyze_and_submit(backend, [make_detection()])

    assert created["report_id"]


def test_health_reports_model_version_and_warm_up_ran(backend: Backend) -> None:
    response = backend.client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_version": "test-model-1"}
    assert backend.detector.was_warmed_up


def test_cors_allows_only_the_dashboard_origin(backend: Backend) -> None:
    preflight_headers = {
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-API-Key",
    }

    allowed = backend.client.options(
        "/api/v1/reports", headers={"Origin": DASHBOARD_ORIGIN, **preflight_headers}
    )
    denied = backend.client.options(
        "/api/v1/reports", headers={"Origin": "https://evil.test", **preflight_headers}
    )

    assert allowed.headers["access-control-allow-origin"] == DASHBOARD_ORIGIN
    assert "access-control-allow-origin" not in denied.headers


def test_unknown_route_uses_the_error_body(backend: Backend) -> None:
    response = backend.client.get("/api/v1/nope")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
