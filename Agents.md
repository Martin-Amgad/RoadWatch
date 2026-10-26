# AGENTS.md

Instructions for AI coding agents and human contributors working on RoadWatch. Read this file fully before writing code.

## 1. Project summary
RoadWatch is an AI-powered road damage reporting system.
- Citizens use a Flutter app: photo, AI damage detection, preliminary severity, GPS, submit.
- Municipal staff use a React dashboard: severity-sorted reports, filters, potential duplicate groups, status updates.
- One shared FastAPI backend does validation, YOLOv8n inference, severity scoring, storage, and DBSCAN clustering.

Pipeline: photo -> detection -> severity -> location-tagged report -> duplicate grouping -> prioritized staff review -> status tracking.

## 2. Repository map
| Folder                            | Content                                           | Owner            |
| --------------------------------- | ------------------------------------------------- | ---------------- |
| `apps/mobile`                     | Flutter citizen app                               | M1               |
| `apps/dashboard`                  | React staff dashboard                             | M6               |
| `services/api`                    | FastAPI backend                                   | M2               |
| `infra/db/migrations`             | PostgreSQL/PostGIS migrations                     | M3               |
| `ml/damage_detection`             | Dataset prep, YOLOv8n training, `detect()` module | M4               |
| `ml/severity`                     | Severity rules config and `severity()`            | M5               |
| `ml/clustering`                   | DBSCAN `cluster()`                                | M5               |
| `scripts`                         | Seed data, cleanup scripts                        | M3               |
| `tests/unit`, `tests/integration` | Automated tests                                   | Component owners |
| `docs`                            | Contract, schema, vocabulary, decisions           | Everyone         |
| `data`                            | Dataset notes only. Raw data is never committed   | M4               |

Work only inside your component's folder unless the task says otherwise.

## 3. Tech stack
Flutter (Android demo), React, Python + FastAPI, Ultralytics YOLOv8n, scikit-learn DBSCAN, PostgreSQL + PostGIS on Supabase, Supabase Storage, GitHub. Hosting is decided in DEC-11 (`docs/decisions/decisions.md`).

## 4. Source of truth (read before coding)
1. `docs/api/contract.md` and `docs/api/openapi.json`: endpoints, JSON shapes, errors.
2. `docs/architecture/vocabulary.md`: exact strings for statuses, severity labels, damage categories, field names.
3. `docs/architecture/database-schema.md`: tables and columns.
4. `docs/decisions/decisions.md`: why things are the way they are.

Use the exact names and strings from these documents. If a document is silent or ambiguous, stop and ask the component owner. Do not guess.

## 5. Architecture rules (do not violate)
1. The backend is the single authority. Clients never compute severity or clusters and never send predictions.
2. Two-step flow. `POST /api/v1/analyze` returns detections, severity, and an `analysis_id`. `POST /api/v1/reports` takes `analysis_id`, latitude, longitude, and description, and reuses the stored analysis.
3. Analyses live in the `analyses` table with a temporary image under the `pending/` storage prefix. Items older than 24 hours are deleted by a cleanup script.
4. Images are never stored in database rows. The database stores storage paths only.
5. Submission fully succeeds or fails with a clear error. No partial reports.
6. The YOLO model is loaded once at startup, never per request.
7. Clustering only adds a `cluster_id`. Reports are never deleted or merged. Cluster IDs are regenerated values; no logic may depend on a specific ID persisting.
8. AI output is always labeled "preliminary" in the app and the dashboard.
9. No detection: the user may retake or submit anyway. The report has a null category, severity "None", and sorts last.
10. GPS is required. If location is denied or off, the app blocks submission with a message and a retry/settings button.
11. Staff endpoints require the shared staff API key in the `X-API-Key` header. The dashboard keeps the key in session memory only.
12. CORS allows only the dashboard origin.
13. All endpoints are under `/api/v1`.
14. Validate every input: image type and size, latitude in [-90, 90], longitude in [-180, 180], description length, valid status transitions.

## 6. Coding standards
- Clean code: descriptive names, one responsibility per function, small functions, no magic numbers (use named constants or config), no dead code, no commented-out code.
- Python: type hints, snake_case. Dart and JavaScript: follow the standard style of the language.
- Configuration and secrets come from environment variables. Never commit secrets. Keep `.env.example` current.
- Add no new dependencies without owner approval. Pin versions in `requirements.txt` or the lock file.
- Write tests for new logic and run them before finishing.
- Update the component README when behavior, setup, or interfaces change.

## 7. How to work on a task
1. Read the task text and the documents in section 4.
2. List the files you will change. Stay within the allowed folder.
3. Make the smallest change that meets the acceptance criteria.
4. Run tests and linters.
5. If you must change the contract, schema, or vocabulary, update the document in the same pull request and tell the owner.
6. Open a PR (see `CONTRIBUTING.md`). State what changed, how you tested it, and any open questions.

## 8. Scope guard
The project has 4 weeks. The MVP list in the spec (section 17.1) is the only scope.
1. Work only on tasks with an ID on the board.
2. An idea outside the task goes into an issue labeled `parked`. Do not build it.
3. No optional work before Milestone 4.
4. If your task grows beyond its "Done when", stop and tell the owner.

## 9. Do not
- Change the contract, schema, or vocabulary silently.
- Hardcode predictions, severity values, or fake reports in the real pipeline. The demo uses real inference and real persistence.
- Add anything outside the MVP list (spec section 17.1). Cut items: map view, MLflow, Hugging Face Hub, image-quality checks, own-report history (`reporter_ref`, `/reports/mine`), `staff_users` table.
- Add endpoints, fields, tables, dependencies, or screens that are not in the contract, schema, or task text. Open a `contract-change` issue instead (`CONTRIBUTING.md` section 11).
- Commit datasets, model weights, secrets, or `.env` files.
- Edit another member's component without asking its owner.