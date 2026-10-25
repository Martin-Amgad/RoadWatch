# API service

**Planned stack:** Python + FastAPI.

## Responsibilities
- Validate uploaded images, metadata, and coordinate ranges.
- Expose documented endpoints for health checks, image analysis, report creation, report listing/filtering, report details, and status updates.
- Invoke the detection and severity modules.
- Persist report records and image references.
- Update geographic cluster assignments when reports arrive.
- Enforce authorization for staff-only status changes.
- Return clear errors without leaving partially saved reports.

## Initial API contract to discuss
- `GET /health`
- `POST /analyze` (or agree on a single-call submission design)
- `POST /reports`
- `GET /reports`
- `GET /reports/{report_id}`
- `PATCH /reports/{report_id}/status`

These are planning suggestions, not implemented endpoints. The team must agree on request/response schemas before integration.
