# RoadWatch contributor guidance

This repository contains an MVP for AI-powered road damage reporting. Keep work within the assigned component boundaries. Member 3 owns `infra/db`, `scripts` for data, and database documentation; changes to `services/api`, `apps/mobile`, `apps/dashboard`, and `ml` require their owner's review.

Use the signed OpenAPI contract and DB schema as authoritative when available. Keep SQL migrations additive and immutable after application. Never commit `.env`, passwords, access tokens, secret keys, real citizen identifiers, unblurred faces or license plates in demo data.

Keep report deletion/merging out of duplicate grouping. Clusters are only suggestions; preserve every submitted report. Use parameterized SQL and explicit GPS coordinate ordering. Ensure no backend service key is sent to web or mobile clients. Before merging, run `python -m pytest -q`, `python scripts/check_db.py` on a permitted test Supabase project, and describe API contract changes.
