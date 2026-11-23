"""Adapters binding the API ports to the ML modules owned by M4 and M5.

Module paths and call shapes live only in this file. If an ML module changes
its signature, this is the single place to update.
"""

import importlib
import io
from collections.abc import Callable, Sequence

from PIL import Image

from ..constants import WARM_UP_IMAGE_SIZE_PX
from ..detections import detection_from_mapping, detections_to_json
from ..domain import Detection, SeverityLabel, SeverityResult

DETECT_MODULE = "ml.damage_detection.detect"
SEVERITY_MODULE = "ml.severity.severity"
CLUSTER_MODULE = "ml.clustering.cluster"

NOISE_LABEL_THRESHOLD = 0


def _load_function(module_name: str, function_name: str) -> Callable:
    return getattr(importlib.import_module(module_name), function_name)


class MlDetector:
    def __init__(self, model_version: str) -> None:
        self.model_version = model_version
        self._detect = _load_function(DETECT_MODULE, "detect")

    def warm_up(self) -> None:
        blank = Image.new("RGB", (WARM_UP_IMAGE_SIZE_PX, WARM_UP_IMAGE_SIZE_PX))
        buffer = io.BytesIO()
        blank.save(buffer, format="PNG")
        self._detect(buffer.getvalue())

    def detect(self, image_bytes: bytes) -> Sequence[Detection]:
        return tuple(detection_from_mapping(item) for item in self._detect(image_bytes))


class MlSeverityScorer:
    def __init__(self) -> None:
        self._severity = _load_function(SEVERITY_MODULE, "severity")

    def score(
        self, detections: Sequence[Detection], image_width: int, image_height: int
    ) -> SeverityResult:
        result = self._severity(
            detections_to_json(detections), image_width, image_height
        )
        return SeverityResult(
            label=SeverityLabel(result["label"]), score=float(result["score"])
        )


class MlClusterer:
    def __init__(self) -> None:
        self._cluster = _load_function(CLUSTER_MODULE, "cluster")

    def cluster(self, coordinates: Sequence[tuple[float, float]]) -> list[int | None]:
        if not coordinates:
            return []
        labels = self._cluster(list(coordinates))
        return [
            None if label < NOISE_LABEL_THRESHOLD else int(label) for label in labels
        ]
