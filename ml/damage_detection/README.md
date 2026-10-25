# Road-damage detection

**Planned model:** YOLOv8n, initialized from pretrained weights and fine-tuned on a selected public road-damage dataset.

## Expected responsibilities
- Document dataset source, license, class mapping, version, and train/validation/test splits.
- Keep training configuration and evaluation results reproducible.
- Provide an inference interface that accepts an image and returns detections (class, confidence, bounding box).
- Document supported image formats and behavior when no damage is detected.

Do not commit datasets or large model weights to Git. This directory is a placeholder; no model or dataset is included.
