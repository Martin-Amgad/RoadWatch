# Contributing to RoadWatch

## Responsibilities

- M1: Flutter mobile application.
- M2: FastAPI, validation, staff authentication, Storage upload orchestration, OpenAPI.
- M3: PostgreSQL/PostGIS, migrations, repository, storage bucket setup, seed data, persistence tests and cleanup.
- M4: Dataset, detector, inference/evaluation.
- M5: Severity, DBSCAN clustering and analytics tests.
- M6: Dashboard, deployment and end-to-end demo.

## Database change workflow

1. Confirm compatibility with the signed OpenAPI and schema vocabulary.
2. Add a new numbered SQL migration; never edit previously applied migrations.
3. Update Python repository functions, tests and `infra/db/README.md`.
4. Run `python -m pytest -q` and a smoke check on an approved Supabase test project.
5. Request review from M2 for data contract changes and M5 for cluster-label changes.
6. Do not add out-of-scope features before milestone sign-off.

## Security

Never commit the `.env` file or paste credentials into issues. Do not use a database superuser in client-side applications. Respect private image storage and responsible-AI disclaimers.
