# API Contract (v1, DRAFT for Day 3 sign-off)

Owner: M2. Machine-readable copy: `docs/api/openapi.json` (generated from the code; this file explains intent).
Names and strings follow `docs/architecture/vocabulary.md`. Items marked **PROPOSED** need sign-off; items that change the vocabulary are listed in section 8.

Base path: `/api/v1`. JSON fields are snake_case. Timestamps are ISO 8601 UTC, e.g. `2026-11-02T14:30:00Z`.

## 1. Authentication
| Endpoint group | Auth |
| --- | --- |
| `POST /analyze`, `POST /reports`, `GET /health` | Public |
| `GET /reports`, `GET /reports/{report_id}`, `PATCH /reports/{report_id}/status` | Header `X-API-Key: <shared staff key>` |

Missing or wrong key: `401`, code `unauthorized`. CORS allows only the dashboard origin (`DASHBOARD_ORIGIN`), methods `GET`, `POST`, `PATCH`, headers `X-API-Key`, `Content-Type`.

## 2. Limits (PROPOSED)
| Limit | Value |
| --- | --- |
| Max image size | 10 MiB (10,485,760 bytes) |
| Allowed image types | JPEG, PNG. Decided from the file content, not the `Content-Type` header (mobile clients often send `application/octet-stream`) |
| Max description length | 500 characters. Blank descriptions are stored as `null` |
| Analysis lifetime | 24 hours |
| List page size | default 50, maximum 200 |

## 3. Error body (PROPOSED)
Every error uses this shape.
```json
{ "error": { "code": "invalid_coordinates", "message": "Invalid value for 'latitude': ..." } }
```
| Code | HTTP | When |
| --- | --- | --- |
| `invalid_image_type` | 415 | Image decoded but is not JPEG or PNG |
| `image_too_large` | 413 | Upload exceeds the size limit |
| `unreadable_image` | 422 | Not an image, corrupt, or truncated |
| `invalid_coordinates` | 422 | Latitude or longitude missing, non-numeric, or out of range |
| `description_too_long` | 422 | Description over the limit |
| `invalid_request` | 422 | Any other malformed request (missing field, bad UUID, bad query value, unknown status). **New code, see section 8** |
| `analysis_not_found` | 404 | Unknown `analysis_id`, or already used by a report |
| `analysis_expired` | 410 | `analysis_id` older than 24 hours |
| `invalid_status_transition` | 409 | Status change not allowed |
| `unauthorized` | 401 | Missing or wrong staff key |
| `not_found` | 404 | Report or route does not exist |
| `internal_error` | 500 | Unexpected failure. No partial report is left behind |

## 4. Endpoints

### 4.1 `GET /api/v1/health`
`200`
```json
{ "status": "ok", "model_version": "yolov8n-rdd2022-r1" }
```

### 4.2 `POST /api/v1/analyze`
Multipart form, one file field named `image`. Runs detection and severity, stores the image under `pending/`, saves an analysis.

`200`
```json
{
  "analysis_id": "6f1c0c1e-3b0a-4a56-9c64-0d5a2c6a7e11",
  "damage_category": "pothole",
  "confidence": 0.82,
  "detections": [
    { "class_name": "pothole", "confidence": 0.82, "bbox": [120.0, 340.5, 410.0, 590.0] }
  ],
  "severity_label": "High",
  "severity_score": 0.74
}
```
No detection: `damage_category` is `null`, `confidence` is `0.0`, `detections` is `[]`, `severity_label` is `"None"`, `severity_score` is `0.0`.
Errors: `image_too_large`, `invalid_image_type`, `unreadable_image`, `invalid_request` (no `image` part).

### 4.3 `POST /api/v1/reports`
JSON body. Reuses the stored analysis. The client never sends predictions.
```json
{
  "analysis_id": "6f1c0c1e-3b0a-4a56-9c64-0d5a2c6a7e11",
  "latitude": 30.0444,
  "longitude": 31.2357,
  "description": "Deep hole near the bus stop"
}
```
`201`
```json
{
  "report_id": "b2c1d4a0-8f55-4a0e-9a63-2f1f4e9d7c10",
  "created_at": "2026-11-23T20:15:00Z",
  "damage_category": "pothole",
  "confidence": 0.82,
  "severity_label": "High",
  "severity_score": 0.74,
  "status": "Submitted",
  "cluster_id": 3
}
```
Behavior:
1. Analysis must exist and be younger than 24 hours.
2. The image moves from `pending/<analysis_id>.<ext>` to `reports/<report_id>.<ext>`.
3. The report is inserted and the analysis is deleted in one database transaction. If the insert fails, the image is moved back to `pending/` and the analysis stays usable. **PROPOSED:** an analysis is single use.
4. All clusters are recomputed. **PROPOSED:** if clustering fails, the report is kept, `cluster_id` is `null`, and the error is logged. Clustering is not part of "fully succeeds or fails".

Errors: `analysis_not_found`, `analysis_expired`, `invalid_coordinates`, `description_too_long`, `invalid_request`.

### 4.4 `GET /api/v1/reports` (staff)
Query parameters, all optional: `category` (a `damage_category` string), `status` (one of the three statuses), `limit` (1 to 200, default 50), `offset` (default 0).
Order is fixed: `severity_score` descending, then `created_at` descending. Reports with severity `None` therefore sort last.

`200`
```json
{
  "items": [
    {
      "report_id": "b2c1d4a0-8f55-4a0e-9a63-2f1f4e9d7c10",
      "created_at": "2026-11-23T20:15:00Z",
      "updated_at": "2026-11-23T20:15:00Z",
      "image_url": "https://<project>.supabase.co/storage/v1/object/sign/...",
      "latitude": 30.0444,
      "longitude": 31.2357,
      "description": "Deep hole near the bus stop",
      "damage_category": "pothole",
      "confidence": 0.82,
      "detections": [
        { "class_name": "pothole", "confidence": 0.82, "bbox": [120.0, 340.5, 410.0, 590.0] }
      ],
      "severity_label": "High",
      "severity_score": 0.74,
      "status": "Submitted",
      "cluster_id": 3
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```
`image_url` is a signed URL valid for 1 hour, or `null` if the image cannot be resolved. The database stores only the storage path.

### 4.5 `GET /api/v1/reports/{report_id}` (staff)
Same fields as one list item, plus `cluster_mates`: the other reports with the same `cluster_id` (same item shape, empty when `cluster_id` is `null`). The dashboard labels them "Potential duplicate".
Errors: `not_found`.

### 4.6 `PATCH /api/v1/reports/{report_id}/status` (staff)
```json
{ "status": "Under Review" }
```
`200` returns one report item. Allowed: `Submitted` to `Under Review` to `Resolved`, forward only, one step at a time.
Errors: `invalid_status_transition`, `not_found`, `invalid_request` (unknown status string).

## 5. Pipeline
`POST /analyze` (image to analysis) then `POST /reports` (analysis plus location to report) then staff `GET /reports`. Detection, severity, and clustering run only in the backend.

## 6. Primary detection (PROPOSED)
`damage_category` and `confidence` come from one primary detection: highest class priority first (`pothole`, `alligator_crack`, `transverse_crack`, `longitudinal_crack`), then highest confidence within the class. M4 and M5 may change the order; it is one constant in the backend.

## 7. Not in this contract
`GET /clusters`, `GET /reports/mine`, `reporter_ref`, `staff_users`, rate limiting.

## 8. Changes this draft needs elsewhere
| Document | Change |
| --- | --- |
| `vocabulary.md` §8 | Add error code `invalid_request` |
| `vocabulary.md` §8 | Add the HTTP status per code (table in section 3) |
| Week 1 T3.3 | `create_report(report, consumed_analysis_id)` instead of `create_report(report)`, so the insert and the analysis delete share one transaction. `write_cluster_labels` takes a mapping `{report_id: cluster_id or None}` |
