from uuid import UUID

from services.api.app.constants import MAX_IMAGE_SIZE_BYTES
from tests.support.backend import Backend
from tests.support.builders import analyze_image, make_detection, make_image_bytes

ANALYZE_URL = "/api/v1/analyze"


def post_image(backend: Backend, content: bytes, filename: str = "photo.jpg"):
    return backend.client.post(
        ANALYZE_URL, files={"image": (filename, content, "image/jpeg")}
    )


def test_analyze_returns_detections_category_and_severity(backend: Backend) -> None:
    body = analyze_image(backend, [make_detection("pothole", 0.82)])

    assert UUID(body["analysis_id"])
    assert body["damage_category"] == "pothole"
    assert body["confidence"] == 0.82
    assert body["severity_label"] == "High"
    assert body["detections"] == [
        {"class_name": "pothole", "confidence": 0.82, "bbox": [10.0, 10.0, 40.0, 40.0]}
    ]


def test_analyze_stores_image_under_pending_prefix(backend: Backend) -> None:
    body = analyze_image(backend, [make_detection()])

    assert f"pending/{body['analysis_id']}.jpg" in backend.storage.objects


def test_analyze_without_detections_returns_none_severity(backend: Backend) -> None:
    body = analyze_image(backend, [])

    assert body["damage_category"] is None
    assert body["confidence"] == 0.0
    assert body["severity_label"] == "None"
    assert body["severity_score"] == 0.0
    assert body["detections"] == []


def test_analyze_accepts_png(backend: Backend) -> None:
    response = post_image(backend, make_image_bytes("PNG"), "photo.png")

    assert response.status_code == 200
    assert any(path.endswith(".png") for path in backend.storage.objects)


def test_analyze_rejects_oversized_upload(backend: Backend) -> None:
    response = post_image(backend, b"0" * (MAX_IMAGE_SIZE_BYTES + 1))

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "image_too_large"


def test_analyze_rejects_disallowed_format(backend: Backend) -> None:
    response = post_image(backend, make_image_bytes("GIF"), "photo.gif")

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "invalid_image_type"


def test_analyze_rejects_unreadable_image(backend: Backend) -> None:
    response = post_image(backend, b"not an image")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "unreadable_image"


def test_analyze_rejects_request_without_image(backend: Backend) -> None:
    response = backend.client.post(ANALYZE_URL)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_rejected_image_is_never_stored(backend: Backend) -> None:
    post_image(backend, b"not an image")

    assert backend.storage.objects == {}


def test_failed_upload_returns_internal_error_and_saves_nothing(
    backend: Backend,
) -> None:
    backend.storage.fail_on_upload = True

    response = post_image(backend, make_image_bytes())

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert backend.repository.analyses == {}


def test_failed_save_removes_the_uploaded_image(backend: Backend) -> None:
    backend.repository.fail_on_save_analysis = True

    response = post_image(backend, make_image_bytes())

    assert response.status_code == 500
    assert backend.storage.objects == {}
