from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from services.api.app.constants import ANALYSIS_TTL, MAX_DESCRIPTION_LENGTH
from services.api.app.domain import Analysis
from tests.support.backend import Backend
from tests.support.builders import (
    CAIRO_LATITUDE,
    CAIRO_LONGITUDE,
    analyze_and_submit,
    analyze_image,
    make_detection,
    submit_report,
)

REPORTS_URL = "/api/v1/reports"
NEARBY_OFFSET_DEGREES = 0.00001
FAR_LATITUDE = 30.2
FAR_LONGITUDE = 31.5


def list_reports(backend: Backend, **params) -> dict:
    response = backend.client.get(
        REPORTS_URL, params=params, headers=backend.staff_headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def get_report(backend: Backend, report_id: str) -> dict:
    response = backend.client.get(
        f"{REPORTS_URL}/{report_id}", headers=backend.staff_headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def patch_status(backend: Backend, report_id: str, status: str):
    return backend.client.patch(
        f"{REPORTS_URL}/{report_id}/status",
        json={"status": status},
        headers=backend.staff_headers,
    )


def test_submit_returns_created_report_with_analysis_results(backend: Backend) -> None:
    created = analyze_and_submit(backend, [make_detection("pothole", 0.82)])

    assert UUID(created["report_id"])
    assert created["status"] == "Submitted"
    assert created["damage_category"] == "pothole"
    assert created["confidence"] == 0.82
    assert created["severity_label"] == "High"
    assert created["created_at"].endswith("Z")


def test_submit_moves_image_from_pending_to_reports(backend: Backend) -> None:
    created = analyze_and_submit(backend, [make_detection()])

    assert list(backend.storage.objects) == [f"reports/{created['report_id']}.jpg"]


def test_submitted_report_is_visible_to_staff_with_image_url(backend: Backend) -> None:
    created = analyze_and_submit(backend, [make_detection()], description="Deep hole")

    report = get_report(backend, created["report_id"])

    assert report["latitude"] == CAIRO_LATITUDE
    assert report["longitude"] == CAIRO_LONGITUDE
    assert report["description"] == "Deep hole"
    assert report["image_url"].startswith("https://storage.test/reports/")


def test_blank_description_is_stored_as_null(backend: Backend) -> None:
    created = analyze_and_submit(backend, [make_detection()], description="   ")

    assert get_report(backend, created["report_id"])["description"] is None


def test_analysis_can_only_be_submitted_once(backend: Backend) -> None:
    analysis = analyze_image(backend, [make_detection()])
    submit_report(backend, analysis["analysis_id"])

    second = submit_report(backend, analysis["analysis_id"])

    assert second.status_code == 404
    assert second.json()["error"]["code"] == "analysis_not_found"


def test_unknown_analysis_is_not_found(backend: Backend) -> None:
    response = submit_report(backend, str(uuid4()))

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "analysis_not_found"


def test_expired_analysis_is_rejected(backend: Backend) -> None:
    analysis = analyze_image(backend, [make_detection()])
    analysis_id = UUID(analysis["analysis_id"])
    stored = backend.repository.analyses[analysis_id]
    too_old = datetime.now(UTC) - ANALYSIS_TTL - timedelta(minutes=1)
    backend.repository.analyses[analysis_id] = Analysis(
        **{**vars(stored), "created_at": too_old}
    )

    response = submit_report(backend, analysis["analysis_id"])

    assert response.status_code == 410
    assert response.json()["error"]["code"] == "analysis_expired"


def test_out_of_range_coordinates_are_rejected(backend: Backend) -> None:
    analysis = analyze_image(backend, [make_detection()])

    for latitude, longitude in [(91, 31.0), (-91, 31.0), (30.0, 181), (30.0, -181)]:
        response = submit_report(backend, analysis["analysis_id"], latitude, longitude)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_coordinates"


def test_too_long_description_is_rejected(backend: Backend) -> None:
    analysis = analyze_image(backend, [make_detection()])

    response = submit_report(
        backend, analysis["analysis_id"], description="x" * (MAX_DESCRIPTION_LENGTH + 1)
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "description_too_long"


def test_missing_analysis_id_is_an_invalid_request(backend: Backend) -> None:
    response = backend.client.post(
        REPORTS_URL, json={"latitude": 30.0, "longitude": 31.0}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_nearby_reports_share_a_cluster_and_originals_are_kept(
    backend: Backend,
) -> None:
    first = analyze_and_submit(backend, [make_detection()])
    second = analyze_and_submit(
        backend,
        [make_detection()],
        latitude=CAIRO_LATITUDE + NEARBY_OFFSET_DEGREES,
        longitude=CAIRO_LONGITUDE + NEARBY_OFFSET_DEGREES,
    )
    far = analyze_and_submit(
        backend, [make_detection()], latitude=FAR_LATITUDE, longitude=FAR_LONGITUDE
    )

    first_detail = get_report(backend, first["report_id"])
    assert second["cluster_id"] is not None
    assert first_detail["cluster_id"] == second["cluster_id"]
    assert [mate["report_id"] for mate in first_detail["cluster_mates"]] == [
        second["report_id"]
    ]
    assert far["cluster_id"] is None
    assert get_report(backend, far["report_id"])["cluster_mates"] == []
    assert list_reports(backend)["total"] == 3


def test_failed_clustering_still_keeps_the_report(backend: Backend) -> None:
    backend.clusterer.should_fail = True

    created = analyze_and_submit(backend, [make_detection()])

    assert created["cluster_id"] is None
    assert list_reports(backend)["total"] == 1


def test_failed_insert_leaves_no_report_and_restores_the_pending_image(
    backend: Backend,
) -> None:
    analysis = analyze_image(backend, [make_detection()])
    backend.repository.fail_on_create_report = True

    failed = submit_report(backend, analysis["analysis_id"])

    assert failed.status_code == 500
    assert backend.repository.reports == {}
    assert list(backend.storage.objects) == [f"pending/{analysis['analysis_id']}.jpg"]

    backend.repository.fail_on_create_report = False
    assert submit_report(backend, analysis["analysis_id"]).status_code == 201


def test_list_orders_by_severity_then_puts_no_detection_last(backend: Backend) -> None:
    analyze_and_submit(backend, [make_detection("pothole", 0.5)])
    analyze_and_submit(backend, [])
    analyze_and_submit(backend, [make_detection("pothole", 0.9)])

    scores = [item["severity_score"] for item in list_reports(backend)["items"]]

    assert scores == [0.9, 0.5, 0.0]


def test_equal_severity_lists_newest_first(backend: Backend) -> None:
    older = analyze_and_submit(backend, [make_detection("pothole", 0.7)])
    newer = analyze_and_submit(backend, [make_detection("pothole", 0.7)])

    ids = [item["report_id"] for item in list_reports(backend)["items"]]

    assert ids == [newer["report_id"], older["report_id"]]


def test_list_filters_by_category_and_status(backend: Backend) -> None:
    pothole = analyze_and_submit(backend, [make_detection("pothole", 0.8)])
    analyze_and_submit(backend, [make_detection("transverse_crack", 0.6)])
    patch_status(backend, pothole["report_id"], "Under Review")

    by_category = list_reports(backend, category="transverse_crack")
    by_status = list_reports(backend, status="Under Review")
    both = list_reports(backend, category="transverse_crack", status="Under Review")

    assert by_category["total"] == 1
    assert [item["report_id"] for item in by_status["items"]] == [pothole["report_id"]]
    assert both["total"] == 0


def test_list_paginates_and_reports_the_total(backend: Backend) -> None:
    for confidence in (0.9, 0.8, 0.7):
        analyze_and_submit(backend, [make_detection("pothole", confidence)])

    page = list_reports(backend, limit=2, offset=1)

    assert page["total"] == 3
    assert [item["severity_score"] for item in page["items"]] == [0.8, 0.7]


def test_list_rejects_invalid_query_values(backend: Backend) -> None:
    for params in ({"limit": 0}, {"limit": 1000}, {"offset": -1}, {"status": "Done"}):
        response = backend.client.get(
            REPORTS_URL, params=params, headers=backend.staff_headers
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "invalid_request"


def test_status_moves_forward_one_step_at_a_time_and_persists(backend: Backend) -> None:
    report_id = analyze_and_submit(backend, [make_detection()])["report_id"]

    assert (
        patch_status(backend, report_id, "Under Review").json()["status"]
        == "Under Review"
    )
    assert patch_status(backend, report_id, "Resolved").json()["status"] == "Resolved"
    assert get_report(backend, report_id)["status"] == "Resolved"


def test_invalid_status_transitions_are_rejected(backend: Backend) -> None:
    report_id = analyze_and_submit(backend, [make_detection()])["report_id"]

    skipped = patch_status(backend, report_id, "Resolved")
    unchanged = patch_status(backend, report_id, "Submitted")

    for response in (skipped, unchanged):
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "invalid_status_transition"
    assert get_report(backend, report_id)["status"] == "Submitted"


def test_unknown_status_value_is_an_invalid_request(backend: Backend) -> None:
    report_id = analyze_and_submit(backend, [make_detection()])["report_id"]

    response = patch_status(backend, report_id, "Done")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_unknown_report_is_not_found(backend: Backend) -> None:
    missing_id = str(uuid4())

    detail = backend.client.get(
        f"{REPORTS_URL}/{missing_id}", headers=backend.staff_headers
    )
    update = patch_status(backend, missing_id, "Under Review")

    for response in (detail, update):
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"
