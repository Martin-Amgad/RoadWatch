from services.api.app.detections import (
    detections_from_json,
    detections_to_json,
    select_primary_detection,
)
from tests.support.builders import make_detection


def test_no_detections_has_no_primary() -> None:
    assert select_primary_detection([]) is None


def test_pothole_outranks_more_confident_crack() -> None:
    pothole = make_detection("pothole", 0.4)
    crack = make_detection("longitudinal_crack", 0.95)

    assert select_primary_detection([crack, pothole]) == pothole


def test_same_class_prefers_higher_confidence() -> None:
    weaker = make_detection("pothole", 0.5)
    stronger = make_detection("pothole", 0.9)

    assert select_primary_detection([weaker, stronger]) == stronger


def test_unknown_class_ranks_after_known_classes() -> None:
    unknown = make_detection("debris", 0.99)
    known = make_detection("transverse_crack", 0.2)

    assert select_primary_detection([unknown, known]) == known


def test_json_round_trip_preserves_detections() -> None:
    detections = (
        make_detection("pothole", 0.82),
        make_detection("alligator_crack", 0.6),
    )

    assert detections_from_json(detections_to_json(detections)) == detections
