# RoadWatch API (M2)

FastAPI backend: validation, detection, severity, storage, clustering, staff endpoints.
Contract: `docs/api/contract.md`. Schema: `docs/architecture/database-schema.md`.

## Layout
| Path | Role |
| --- | --- |
| `app/main.py` | App factory. Services are built and the model is warmed up once at startup |
| `app/routes/` | HTTP layer only: parse, call a service, build the response |
| `app/services/` | Orchestration: analysis, report creation, status, clustering |
| `app/ports.py` | Interfaces the services depend on |
| `app/adapters/` | Real implementations: `ml.py` (M4/M5 modules), `storage.py` (Supabase), `postgres.py` |
| `app/errors.py` | Error codes, HTTP statuses, handlers |
| `app/wiring.py` | Production dependency wiring |

## Setup
From the repository root (the `ml` package must be importable):
```
pip install -r services/api/requirements-dev.txt
cp services/api/.env.example services/api/.env   # fill in values, never commit
```
Variables: `DATABASE_URL` (Supabase pooler string), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET` (private bucket), `STAFF_API_KEY`, `DASHBOARD_ORIGIN`, `MODEL_VERSION` (shown in `/health`).

## Run
```
PYTHONPATH=. uvicorn services.api.app.main:create_production_app --factory --host 0.0.0.0 --port 8000
```
Interactive docs: `/docs`.

## Test
```
pytest
```
Tests use in-memory fakes for detection, severity, clustering, storage, and the database. No network.

## Regenerate `openapi.json`
```
python -m services.api.app.export_openapi docs/api/openapi.json
```

## ML module expectations
All bindings are in `app/adapters/ml.py`. Change only that file if a signature differs.
| Module | Call | Returns |
| --- | --- | --- |
| `ml.damage_detection.detect` | `detect(image_bytes)` | list of `{class_name, confidence, bbox}` |
| `ml.severity.severity` | `severity(detections, image_width, image_height)` | `{label, score}` |
| `ml.clustering.cluster` | `cluster(coordinates)`, coordinates are `(latitude, longitude)` pairs | one integer label per pair, negative means unclustered |

`detect` must load its model once (at import or first call). The API calls it once at startup with a blank image to force that load.

## Not verified against live services
`app/adapters/postgres.py` and `app/adapters/storage.py` are covered only by request-shape tests (storage) or not at all (Postgres). Run the Supabase checklist before relying on them:
1. Apply the schema, create a private bucket.
2. `POST /analyze` with a photo: object appears under `pending/`, row in `analyses`.
3. `POST /reports`: object moves to `reports/`, row in `reports`, analysis row gone.
4. `GET /reports` with `X-API-Key`: `image_url` opens the photo.
