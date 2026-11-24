# Handoff: Member 3 → Member 2 (FastAPI)

## Connection contract

Install `requirements.txt` and provide the server-only `DATABASE_URL`/`DB_SSLMODE`. Import:

```python
from infra.db.repository import RoadWatchRepository

repo = RoadWatchRepository()
```

The `RoadWatchRepository` class supports these methods:

| Method | Input | Returns |
|---|---|---|
| `insert_report` | Keyword args incl. `image_path`, `latitude`, `longitude`, `detections`, `model_version`, `category`, `severity`, `severity_score` | Persisted report dictionary |
| `get_report` | `report_id` UUID | Report + detection JSON or `None` |
| `get_reports` | Optional `status`, `category`, `cluster_label`, `limit`, `offset` | List sorted by severity and recent time |
| `update_status` | `report_id`, one of `submitted`/`under_review`/`resolved` | Updated dictionary or `None` |
| `bulk_update_clusters` | `[(report_id, label), ...]`; label `int` or `None` | Updated row count |
| `get_nearby_reports` | `latitude`, `longitude`, `radius_m`, `limit` | Nearby reports with `distance_m` |
| `get_cluster_groups` | none | Cluster candidates with ≥2 reports |

`insert_report` inserts both `reports` and `analyses` within one PostgreSQL transaction. Call it only after the final image exists under `reports/` in private Supabase Storage. Model inference (`detect`), severity computation, `cluster_reports` and endpoint routing remain owned by M2/M4/M5.

## Recommended request sequence

1. `POST /analyze`: validate image and location; upload to `pending/`; run `detect()` and `compute_severity()`; respond with preliminary results. No final DB report yet.
2. `POST /reports`: validate the signed request; move/confirm the image at `reports/{uuid}.jpg` (or another agreed path); call `repo.insert_report(...)` with AI results; return report ID.
3. Run M5 `cluster_reports` over the full report coordinate set; then call `repo.bulk_update_clusters(...)`. If clustering fails, preserve the report and retry instead of deleting it.
4. `GET /reports`: delegate to `repo.get_reports` for server-side severity ordering and filters.
5. `PATCH` report status: delegate to `repo.update_status` after server-side staff authorization.

For a private bucket, return an authorized short-lived signed image URL or proxy authorized images through FastAPI; storing a public URL in `reports.image_path` is not intended.

## Invariants

- M1 and M6 never receive DB credentials or Storage secret keys.
- `cluster_label` values are recomputed labels, not permanent references. `NULL` means not assigned; `-1` can represent noise.
- Validation enforces [-90,90] latitude and [-180,180] longitude; `ST_MakePoint` takes (longitude, latitude).
- All queries use bound parameters, not user-controlled SQL interpolation.
- Do not expose the `get_reports` data layer directly without authorization checks in FastAPI.
- A private Storage upload and PostgreSQL insert are separate systems, requiring explicit compensating cleanup on errors.

## Contract sign-off

See `docs/DECISIONS_TO_CONFIRM.md`. The PDF and proposal specify function families but not full payload and score contracts. Confirm those before locking fields or routes.
