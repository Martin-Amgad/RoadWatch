# Shared Vocabulary

Single source of truth for every fixed string, field name, and format used across the app, dashboard, backend, database, and ML modules. Use these exactly: same spelling, same case, same spacing. Changes follow section 11 of `CONTRIBUTING.md`.

Legend: **FIXED** = agreed. **PROPOSED** = needs confirmation at the Day 3 sign-off. **PROVISIONAL** = waits for a dependency.

## 1. Report status (FIXED)
| Value          | Meaning                            |
| -------------- | ---------------------------------- |
| `Submitted`    | Report received, not yet looked at |
| `Under Review` | Staff are reviewing it             |
| `Resolved`     | Repair done or case closed         |

Exact strings, capital letters, and a single space in `Under Review`. The default for a new report is `Submitted`.

**Allowed transitions (PROPOSED):** `Submitted` -> `Under Review` -> `Resolved`, forward only, one step at a time. Anything else returns `invalid_status_transition`.

## 2. Severity (FIXED labels, PROPOSED sort rule)
| Label    | Meaning                                   |
| -------- | ----------------------------------------- |
| `Low`    | Preliminary low severity                  |
| `Medium` | Preliminary medium severity               |
| `High`   | Preliminary high severity                 |
| `None`   | No supported damage detected (see DEC-05) |

- `severity_score` is a float, higher means more severe. A report with label `None` has `severity_score = 0.0`.
- Dashboard sort (PROPOSED): `severity_score` descending, then `created_at` descending. Because `None` has score 0.0, it sorts last.
- Thresholds and weights live in `ml/severity/rules.yaml`, never in client code.

## 3. Damage categories (PROVISIONAL)
Fixed after M4 completes T4.1. Candidate list based on the standard RDD2022 classes, to be confirmed:

| API string           | Meaning                         | Source code (RDD2022) |
| -------------------- | ------------------------------- | --------------------- |
| `longitudinal_crack` | Crack along the road direction  | D00                   |
| `transverse_crack`   | Crack across the road direction | D10                   |
| `alligator_crack`    | Interconnected crack pattern    | D20                   |
| `pothole`            | Pothole                         | D40                   |

Rules:
- API strings are lowercase snake_case. Display names are made by the clients (e.g., "Pothole").
- `damage_category` is the primary (highest-priority) detected class, or `null` when nothing was detected.
- The final list, the class order in `data.yaml`, and the priority order for choosing the primary class are set by M4 and M5 and recorded here.

## 4. Field names (PROPOSED)
All JSON fields and database columns use snake_case.

| Field                      | Type            | Notes                                                                   |
| -------------------------- | --------------- | ----------------------------------------------------------------------- |
| `report_id`                | string (UUID)   | Report identifier                                                       |
| `analysis_id`              | string (UUID)   | Returned by `/analyze`, used by `/reports`                              |
| `created_at`, `updated_at` | string          | ISO 8601, UTC, ending in `Z`, e.g. `2026-11-02T14:30:00Z`               |
| `latitude`, `longitude`    | number          | Decimal degrees, WGS84. Latitude in [-90, 90], longitude in [-180, 180] |
| `description`              | string or null  | Optional, max length set in the contract                                |
| `damage_category`          | string or null  | See section 3                                                           |
| `confidence`               | number          | 0.0 to 1.0, confidence of the primary detection                         |
| `detections`               | array           | See section 5                                                           |
| `severity_label`           | string          | See section 2                                                           |
| `severity_score`           | number          | See section 2                                                           |
| `status`                   | string          | See section 1                                                           |
| `cluster_id`               | integer or null | See section 6                                                           |
| `image_url`                | string          | Reference to the stored image (path or signed URL)                      |

Differences from the spec's illustrative response (which uses `severity`): this vocabulary uses `severity_label` and `severity_score` everywhere, matching the database columns. The contract must follow this list.

Coordinate warning: PostGIS points are written in longitude, latitude order. JSON always uses the named fields `latitude` and `longitude`, never an unnamed array.

## 5. Detection object (PROPOSED)
```json
{
  "class_name": "pothole",
  "confidence": 0.82,
  "bbox": [x_min, y_min, x_max, y_max]
}
```
- `class_name` is a category string from section 3.
- `bbox` is in pixels relative to the original image (not resized), with the origin at the top-left corner.
- M4's `detect()` returns this exact shape. M5's `severity()` consumes it together with the original image width and height in pixels.

## 6. Clusters
- `cluster_id` is an integer or `null`. `null` means the report is not part of a potential duplicate group.
- Cluster IDs are regenerated every time clustering runs. Nothing may rely on a particular ID persisting.
- Clustering never deletes or merges reports.

## 7. Identifiers
- `report_id` and `analysis_id` are UUID version 4, lowercase, with hyphens.
- Storage paths: pending images under `pending/<analysis_id>.<ext>`, final images under `reports/<report_id>.<ext>`. **PROPOSED**; M3 confirms.

## 8. Error codes (PROPOSED, owner M2)
Every error response uses the contract's error body and one of these `code` values.

| Code                        | When                                                   |
| --------------------------- | ------------------------------------------------------ |
| `invalid_image_type`        | File type is not allowed                               |
| `image_too_large`           | File exceeds the size limit                            |
| `unreadable_image`          | File is corrupt or cannot be decoded                   |
| `invalid_coordinates`       | Latitude or longitude out of range                     |
| `description_too_long`      | Description exceeds the limit                          |
| `analysis_not_found`        | Unknown `analysis_id`                                  |
| `analysis_expired`          | `analysis_id` older than the cleanup window (24 hours) |
| `invalid_status_transition` | Status change not allowed                              |
| `unauthorized`              | Missing or wrong staff API key                         |
| `not_found`                 | Report does not exist                                  |
| `internal_error`            | Unexpected server error                                |

Limits (maximum image size, allowed types, description length) are set by M2 in the contract and not repeated here.

## 9. Fixed user-facing wording
Use these texts so the app and dashboard say the same thing.

| Where                               | Text                                                                             |
| ----------------------------------- | -------------------------------------------------------------------------------- |
| AI result label (app and dashboard) | "Preliminary, image-based indicator. Not a professional engineering assessment." |
| No detection                        | "No supported road damage detected." Buttons: "Retake" and "Submit anyway"       |
| No-detection badge (dashboard)      | "No AI detection"                                                                |
| Duplicate group label (dashboard)   | "Potential duplicate"                                                            |
| Location blocked (app)              | "Location is required to submit a report." Buttons: "Retry" and "Open settings"  |

## 10. Pipeline terms
| Term                | Definition                                                                      |
| ------------------- | ------------------------------------------------------------------------------- |
| Analysis            | The result of running detection and severity on one image, stored by `/analyze` |
| Report              | A submitted record built from an analysis plus location and description         |
| Detection           | One bounding box with a class and a confidence                                  |
| Primary detection   | The detection used for `damage_category` and `confidence`                       |
| Potential duplicate | Reports sharing a `cluster_id`; a suggestion for staff, not a fact              |
| Staff               | Municipal users of the dashboard, authenticated with the shared API key         |