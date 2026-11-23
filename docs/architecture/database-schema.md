# Database Schema (DRAFT by M2 to unblock the backend; M3 owns and finalizes in T3.2)

Reflects exactly what `services/api` reads and writes. M3 may change names, but any change must reach `services/api/app/adapters/postgres.py` in the same PR.

Not included on purpose: `staff_users`, `reporter_ref` (cut in `AGENTS.md`).

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE analyses (
    id              uuid PRIMARY KEY,
    created_at      timestamptz      NOT NULL DEFAULT now(),
    image_path      text             NOT NULL,
    image_width     integer          NOT NULL CHECK (image_width > 0),
    image_height    integer          NOT NULL CHECK (image_height > 0),
    detections      jsonb            NOT NULL DEFAULT '[]'::jsonb,
    damage_category text,
    confidence      double precision NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    severity_label  text             NOT NULL CHECK (severity_label IN ('Low', 'Medium', 'High', 'None')),
    severity_score  double precision NOT NULL DEFAULT 0
);
CREATE INDEX analyses_created_at_idx ON analyses (created_at);

CREATE TABLE reports (
    id              uuid PRIMARY KEY,
    created_at      timestamptz           NOT NULL DEFAULT now(),
    updated_at      timestamptz           NOT NULL DEFAULT now(),
    image_path      text                  NOT NULL,
    location        geography(Point, 4326) NOT NULL,
    description     text,
    damage_category text,
    confidence      double precision      NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    detections      jsonb                 NOT NULL DEFAULT '[]'::jsonb,
    severity_label  text                  NOT NULL CHECK (severity_label IN ('Low', 'Medium', 'High', 'None')),
    severity_score  double precision      NOT NULL DEFAULT 0,
    status          text                  NOT NULL DEFAULT 'Submitted'
                    CHECK (status IN ('Submitted', 'Under Review', 'Resolved')),
    cluster_id      integer
);
CREATE INDEX reports_location_idx        ON reports USING gist (location);
CREATE INDEX reports_severity_score_idx  ON reports (severity_score DESC, created_at DESC);
CREATE INDEX reports_status_idx          ON reports (status);
CREATE INDEX reports_damage_category_idx ON reports (damage_category);
CREATE INDEX reports_cluster_id_idx      ON reports (cluster_id);

ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports  ENABLE ROW LEVEL SECURITY;
```

## Notes
- Row level security is enabled with no policies, so Supabase's public API cannot read these tables. The backend connects with the database connection string (role that bypasses RLS).
- PostGIS points are `(longitude, latitude)`. The backend writes `ST_MakePoint(longitude, latitude)` and reads `ST_X` as longitude, `ST_Y` as latitude.
- `image_path` holds a storage path (`pending/<analysis_id>.<ext>` or `reports/<report_id>.<ext>`), never image bytes. The storage bucket must be private; staff see signed URLs.
- `cluster_id` is a regenerated value. Nothing may rely on it persisting.
- Cleanup rule (M3 script): delete `analyses` rows older than 24 hours and their `pending/` objects.

## Data-access functions used by the API
| Function | Used by |
| --- | --- |
| `save_analysis(analysis)` | `POST /analyze` |
| `get_analysis(analysis_id)` | `POST /reports` |
| `create_report(report, consumed_analysis_id)` (insert report and delete analysis, one transaction) | `POST /reports` |
| `list_reports(query)` (filters, fixed order, limit, offset, total) | `GET /reports` |
| `get_report(report_id)` | detail, status update |
| `list_cluster_mates(cluster_id, excluding_report_id)` | detail |
| `update_status(report_id, status)` | `PATCH status` |
| `get_all_report_coordinates()` | clustering |
| `write_cluster_labels({report_id: cluster_id or None})` | clustering |
