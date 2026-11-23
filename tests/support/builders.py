import io
from collections.abc import Sequence

from PIL import Image

from services.api.app.domain import Detection
from tests.support.backend import Backend

DEFAULT_BBOX = (10.0, 10.0, 40.0, 40.0)
CAIRO_LATITUDE = 30.0444
CAIRO_LONGITUDE = 31.2357


def make_image_bytes(
    image_format: str = "JPEG", size: tuple[int, int] = (64, 48)
) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color=(120, 120, 120)).save(buffer, format=image_format)
    return buffer.getvalue()


def make_detection(class_name: str = "pothole", confidence: float = 0.82) -> Detection:
    return Detection(class_name=class_name, confidence=confidence, bbox=DEFAULT_BBOX)


def analyze_image(backend: Backend, detections: Sequence[Detection] = ()) -> dict:
    backend.detector.detections = detections
    response = backend.client.post(
        "/api/v1/analyze",
        files={"image": ("photo.jpg", make_image_bytes("JPEG"), "image/jpeg")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def submit_report(
    backend: Backend,
    analysis_id: str,
    latitude: float = CAIRO_LATITUDE,
    longitude: float = CAIRO_LONGITUDE,
    description: str | None = None,
):
    return backend.client.post(
        "/api/v1/reports",
        json={
            "analysis_id": analysis_id,
            "latitude": latitude,
            "longitude": longitude,
            "description": description,
        },
    )


def analyze_and_submit(
    backend: Backend,
    detections: Sequence[Detection] = (),
    latitude: float = CAIRO_LATITUDE,
    longitude: float = CAIRO_LONGITUDE,
    description: str | None = None,
) -> dict:
    analysis = analyze_image(backend, detections)
    response = submit_report(
        backend, analysis["analysis_id"], latitude, longitude, description
    )
    assert response.status_code == 201, response.text
    return response.json()
