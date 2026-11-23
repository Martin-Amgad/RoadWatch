from collections.abc import Mapping, Sequence
from typing import Any

from .constants import DAMAGE_CATEGORY_PRIORITY
from .domain import Detection


def select_primary_detection(detections: Sequence[Detection]) -> Detection | None:
    if not detections:
        return None
    return min(detections, key=_priority_key)


def _priority_key(detection: Detection) -> tuple[int, float]:
    unknown_rank = len(DAMAGE_CATEGORY_PRIORITY)
    rank = (
        DAMAGE_CATEGORY_PRIORITY.index(detection.class_name)
        if detection.class_name in DAMAGE_CATEGORY_PRIORITY
        else unknown_rank
    )
    return rank, -detection.confidence


def detections_to_json(detections: Sequence[Detection]) -> list[dict[str, Any]]:
    return [
        {
            "class_name": detection.class_name,
            "confidence": detection.confidence,
            "bbox": list(detection.bbox),
        }
        for detection in detections
    ]


def detections_from_json(items: Sequence[Mapping[str, Any]]) -> tuple[Detection, ...]:
    return tuple(detection_from_mapping(item) for item in items)


def detection_from_mapping(item: Mapping[str, Any]) -> Detection:
    x_min, y_min, x_max, y_max = (float(value) for value in item["bbox"])
    return Detection(
        class_name=str(item["class_name"]),
        confidence=float(item["confidence"]),
        bbox=(x_min, y_min, x_max, y_max),
    )
