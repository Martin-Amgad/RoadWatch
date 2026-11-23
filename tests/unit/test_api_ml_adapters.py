import sys
from types import SimpleNamespace

import pytest

from services.api.app.adapters import ml
from services.api.app.domain import Detection, SeverityLabel
from tests.support.builders import make_detection

PNG_SIGNATURE = b"\x89PNG"


def install_module(monkeypatch: pytest.MonkeyPatch, name: str, **attributes) -> None:
    monkeypatch.setitem(sys.modules, name, SimpleNamespace(**attributes))


def test_detector_converts_mappings_to_detections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = [{"class_name": "pothole", "confidence": 0.9, "bbox": [1, 2, 3, 4]}]
    install_module(monkeypatch, ml.DETECT_MODULE, detect=lambda image_bytes: raw)

    detections = ml.MlDetector("v1").detect(b"image")

    assert detections == (Detection("pothole", 0.9, (1.0, 2.0, 3.0, 4.0)),)


def test_detector_warm_up_runs_detection_on_a_png(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[bytes] = []

    def record_call(image_bytes: bytes) -> list:
        received.append(image_bytes)
        return []

    install_module(monkeypatch, ml.DETECT_MODULE, detect=record_call)

    detector = ml.MlDetector("v1")
    detector.warm_up()

    assert detector.model_version == "v1"
    assert len(received) == 1
    assert received[0].startswith(PNG_SIGNATURE)


def test_severity_scorer_passes_json_detections_and_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received: list[tuple] = []

    def severity(detections: list, image_width: int, image_height: int) -> dict:
        received.append((detections, image_width, image_height))
        return {"label": "Medium", "score": 0.41}

    install_module(monkeypatch, ml.SEVERITY_MODULE, severity=severity)

    result = ml.MlSeverityScorer().score([make_detection("pothole", 0.8)], 640, 480)

    assert result.label == SeverityLabel.MEDIUM
    assert result.score == 0.41
    assert received == [
        (
            [
                {
                    "class_name": "pothole",
                    "confidence": 0.8,
                    "bbox": [10.0, 10.0, 40.0, 40.0],
                }
            ],
            640,
            480,
        )
    ]


def test_clusterer_maps_negative_labels_to_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_module(
        monkeypatch, ml.CLUSTER_MODULE, cluster=lambda coordinates: [0, -1, 0]
    )

    labels = ml.MlClusterer().cluster([(30.0, 31.0), (31.0, 32.0), (30.0, 31.0)])

    assert labels == [0, None, 0]


def test_clusterer_skips_the_module_when_there_are_no_coordinates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(coordinates: list) -> list:
        raise AssertionError("cluster must not be called")

    install_module(monkeypatch, ml.CLUSTER_MODULE, cluster=fail_if_called)

    assert ml.MlClusterer().cluster([]) == []
