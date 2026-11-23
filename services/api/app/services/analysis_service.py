import logging
from uuid import uuid4

from ..constants import PENDING_PREFIX
from ..detections import select_primary_detection
from ..domain import Analysis, NewAnalysis
from ..image_validation import ValidatedImage
from ..ports import AnalysisRepository, Detector, ObjectStorage, SeverityScorer

logger = logging.getLogger(__name__)

NO_DETECTION_CONFIDENCE = 0.0


class AnalysisService:
    def __init__(
        self,
        detector: Detector,
        severity_scorer: SeverityScorer,
        storage: ObjectStorage,
        analyses: AnalysisRepository,
    ) -> None:
        self._detector = detector
        self._severity_scorer = severity_scorer
        self._storage = storage
        self._analyses = analyses

    def analyze(self, image: ValidatedImage) -> Analysis:
        detections = self._detector.detect(image.content)
        severity = self._severity_scorer.score(detections, image.width, image.height)
        primary = select_primary_detection(detections)

        analysis_id = uuid4()
        pending_path = f"{PENDING_PREFIX}/{analysis_id}.{image.extension}"
        new_analysis = NewAnalysis(
            id=analysis_id,
            image_path=pending_path,
            image_width=image.width,
            image_height=image.height,
            detections=tuple(detections),
            damage_category=primary.class_name if primary else None,
            confidence=primary.confidence if primary else NO_DETECTION_CONFIDENCE,
            severity=severity,
        )

        self._storage.upload(pending_path, image.content, image.content_type)
        try:
            return self._analyses.save_analysis(new_analysis)
        except Exception:
            self._discard_pending_image(pending_path)
            raise

    def _discard_pending_image(self, pending_path: str) -> None:
        try:
            self._storage.delete(pending_path)
        except Exception:
            logger.exception("Could not remove orphaned pending image %s", pending_path)
