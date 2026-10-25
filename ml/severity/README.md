# Preliminary severity estimation

Implement a lightweight, documented rule-based score using agreed inputs such as predicted damage category, bounding-box area fraction, and confidence.

The module should return a label (`Low`, `Medium`, `High`, or an agreed unknown/no-detection value) and optionally a numeric score for sorting. Thresholds are initial team choices unless validated against suitable expert assessments.

**User-facing limitation:** severity is a preliminary image-based indicator, not a professional engineering assessment. Add tests for thresholds, multiple detections, and no detections.
