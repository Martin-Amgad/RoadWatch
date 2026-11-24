# Database module

## Scope

This module provides PostgreSQL + PostGIS persistent storage for the RoadWatch MVP. It is designed to be integrated with the FastAPI service in `services/api`, not accessed by clients directly.

## Tables

`public.reports`: UUID primary key, object Storage image path, latitude/longitude, generated geography point (EPSG:4326), optional description, damage category, severity and severity rank, report status, nullable integer cluster label, created timestamp.

`public.analyses`: UUID primary key, unique foreign key `report_id -> reports.id` (one-to-one), detection array as JSONB, model version, created timestamp.

`public.schema_migrations`: applied SQL migration filenames, SHA-256 hashes and timestamps.

## Units and conventions

- Latitude then longitude when passing location to Python functions.
- Longitude then latitude when calling `ST_MakePoint(x, y)`.
- `get_nearby_reports(..., radius_m=...)` uses meters via PostGIS `geography`.
- `severity` accepts `high`, `medium`, `low`, `none`; sorting is based on generated `severity_rank`, newest reports first within a level.
- `status` accepts `submitted`, `under_review`, `resolved`.
- `cluster_label IS NULL`: not processed or no stored result.
- `cluster_label = -1`: DBSCAN noise if M5 uses the standard convention.
- `cluster_label >= 0`: candidate cluster. Labels are not permanent IDs across DBSCAN recomputations.
- Reports with no detections should keep `detections=[]`, `category=NULL`, `severity='none'` unless the signed API contract specifies another representation.
- DBSCAN only marks likely duplicates; no report may be removed or auto-merged.

## Repository API

```python
from infra.db.repository import RoadWatchRepository

repo = RoadWatchRepository()

report = repo.insert_report(
    image_path='reports/example-photo.jpg',
    latitude=30.0444,
    longitude=31.2357,
    category='D40',
    severity='high',
    detections=[{'class_name': 'D40', 'confidence': 0.94, 'bbox': [0.2, 0.2, 0.6, 0.7]}],
    model_version='yolov8n-rdd2022-v1',
)

by_id = repo.get_report(report['id'])
prioritized = repo.get_reports(status='submitted', limit=50, offset=0)
nearby = repo.get_nearby_reports(30.0444, 31.2357, radius_m=100)
updated = repo.update_status(report['id'], 'under_review')
updated_count = repo.bulk_update_clusters([(report['id'], 2)])
clusters = repo.get_cluster_groups()
```

This is an illustration of function usage; the image path must correspond to a real Supabase Storage object for display. There is no automatic object upload inside this repository.

## Data safety

SQL insert of `reports` and `analyses` is transactional. Supabase Storage is not in that PostgreSQL transaction. Member 2 must implement failure compensation: if a Storage upload/move succeeds but the database transaction fails, delete or schedule cleanup of that image. If Storage fails, never commit the report.

PostgreSQL direct credentials and Storage secret keys must only be present on the backend. RLS is enabled and direct `anon`/`authenticated` table access is revoked. Do not disable it just to make the mobile app work.

## Migrations

Run `python scripts/apply_migrations.py`. Applied files are checksummed and should never be edited in place. Add a new numbered migration if the signed contract changes. Existing Supabase projects with other PostGIS schema locations must be reconciled by the team before running this migration.
