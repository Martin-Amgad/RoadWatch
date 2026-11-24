# Contract decisions to confirm with the RoadWatch team

These points are not fully fixed by the uploaded documents and should be agreed with M2/M4/M5 before production integration:

1. **Primary damage category vocabulary:** The documentation lists RDD2022 D00/D10/D20/D40. Confirm exact API names/case, multi-detection primary-category logic, and the no-detection representation.
2. **Severity score scale:** The documents specify levels Low/Medium/High and a deterministic score, but do not specify the numeric score range. `severity_score` therefore has no assumed 0–100 database check.
3. **Detection JSON shape:** Confirm `class_name`, `confidence`, bounding-box units and coordinate order, possibly image dimensions, and model version format.
4. **Cluster field name:** Proposal describes `cluster label`; comprehensive docs call it `cluster_id`. The SQL stores `cluster_label`. M2 may alias it to `cluster_id` in the REST response if that is the signed contract.
5. **Cluster noise/unprocessed semantics:** Proposed: `NULL` = not yet processed and `-1` = DBSCAN noise. M5 must confirm, and batches should include all report IDs after recomputation.
6. **Review statuses:** Proposed serialized values are `submitted`, `under_review`, `resolved`, matching the three business states in the documentation.
7. **Photo workflow:** `pending/` and `reports/` folders, Storage object types, signed URL expiration, max image size, and how backend compensates when Storage/DB steps fail.
8. **Coordinate source and demo location:** Member 6 must select a demo city; seeded coordinates are synthetic and configurable in `.env`.
9. **Final SQL scope:** Two tables and one analysis per submitted report are proposed based on the MVP. Any history, staff_users, or map views must not be added without scope approval.
10. **Deployment:** Agree on connection pooling, secret management, scheduled pending cleanup, and whether a separate dedicated DB role should be provisioned later.

Do not silently change the signed Day-3 schema and OpenAPI contract if they already exist. Open a contract-change issue with M2/M6 instead.
