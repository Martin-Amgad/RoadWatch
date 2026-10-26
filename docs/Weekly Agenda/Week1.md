# Week 1: Requirements and Foundations

Goal (Milestone 1): signed contracts, stub endpoints reachable from the app and the dashboard, dataset ready, hosting decided with evidence.

Checkpoints: Day 3 contract/schema/vocabulary sign-off. Day 7 Milestone 1 review.

Project length: 4 weeks. Where the spec (`README.md`) and `docs/decisions/decisions.md` disagree, the decision log wins.

## Team rules
- One branch per task: `feature/<task-id>-short-name`. One PR, reviewed by one other member within 24 hours.
- No secrets in git. Keep `.env.example` current.
- A task is done only when its "Done when" is true, the PR is merged, and the component README is updated.
- Blocked for more than 2 hours: post in the team chat.
- Do not hardcode category names, status strings, or field names before the Day 3 sign-off. Use `vocabulary.md`.

## Start on Day 1 (no dependencies)
L1, L2, L3, T1.1, T2.1, T2.2, T3.1, T4.1, T5.3, T6.2

## Leader
| ID  | Task                                                                                                                                                                                                                                                                                                            | Done when                                               | Depends on                   |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------- |
| L1  | Kickoff: each member claims one role (M1-M6) in the team chat by end of Day 1, one owner per role. Leader assigns unclaimed roles on Day 2. Leader role is coordination only unless a role stays unclaimed. Choose demo city and local photo target (default 30). Set up the task board (one issue per task ID) | Roles table in root README; all issues assigned         | none                         |
| L2  | Write `docs/decisions/decisions.md` with the 11 decisions made so far. DEC-02, DEC-10, and DEC-11 are marked not final                                                                                                                                                                                          | Merged                                                  | none                         |
| L3  | Write `AGENTS.md`, `CONTRIBUTING.md`, `docs/prompt-template.md`, `docs/architecture/vocabulary.md`. Add the "partly superseded" note to the top of the spec                                                                                                                                                     | Merged                                                  | M4 class list for vocabulary |
| L4  | Run the Day 3 sign-off and the Day 7 Milestone 1 review                                                                                                                                                                                                                                                         | Contract, schema, vocabulary approved; checklist ticked | T2.1, T3.2, T3.3, T4.1       |

## M1 Mobile (Flutter) - `apps/mobile`
| ID   | Task                                                                                                                                                                          | Done when                                                     | Depends on |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ---------- |
| T1.1 | Project scaffold and static screens: capture/gallery, result (category, confidence, severity, "preliminary" notice), details (optional description), confirmation (report ID) | Navigable end to end with fake data, on a real Android device | none       |
| T1.2 | Location permission handling: granted, denied, services off. Denied and off block submission with a message and a retry/settings button                                       | All 3 cases manually tested                                   | T1.1       |
| T1.3 | API client with configurable base URL calling stub `/analyze` and `/reports`; document the debug APK build in the README                                                      | Stub response shown in the app; a teammate installs the APK   | T1.1, T2.3 |

## M2 Backend - `services/api`
| ID   | Task                                                                                                                                                                                                                                            | Done when                              | Depends on            |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | --------------------- |
| T2.1 | Draft `docs/api/contract.md`: endpoints, request/response JSON examples, auth header, validation rules. Set the limits: max image size, allowed image types, max description length. One error body shape using the codes in `vocabulary.md` §8 | Ready for Day 3 sign-off               | none                  |
| T2.2 | Hosting feasibility test with M6: backend with `yolov8n.pt` loaded at startup, deployed on Render and Hugging Face Spaces                                                                                                                       | Results handed to M6 for T6.1          | none                  |
| T2.3 | Stub endpoints returning contract-shaped data, with validation (file type, size, lat/lon, description length), staff API key check, CORS limited to the dashboard origin, `/health`                                                             | curl calls return contract-shaped JSON | T2.1, signed contract |
| T2.4 | Export `openapi.json` to `docs/api/`                                                                                                                                                                                                            | Committed                              | T2.3                  |

## M3 Database - `infra/db`
| ID   | Task                                                                                                                                                                                                                                                                    | Done when                             | Depends on          |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------- |
| T3.1 | Set up Supabase (PostGIS, storage bucket with a `pending/` prefix); document free-tier limits (DB size, storage, project pausing) in `docs/architecture/infra-limits.md`                                                                                                | Test image uploads; limits documented | none                |
| T3.2 | Draft `docs/architecture/database-schema.md`: tables `reports` and `analyses`, columns, indexes, cleanup rule (delete `pending/` items older than 24h). No `staff_users` table, no `reporter_ref` column                                                                | Ready for Day 3 sign-off              | T2.1                |
| T3.3 | Define data-access function signatures: save analysis, get analysis, create report, list reports (filters, sort), get report, update status, `get_all_report_coordinates()`, `write_cluster_labels(labels)`. M2 calls `cluster()`; M3 only reads and writes. M2 reviews | Signatures in the schema doc          | T3.2                |
| T3.4 | Migrations in `infra/db/migrations`, including spatial index and indexes on severity_score, status, damage_category                                                                                                                                                     | Run from scratch against Supabase     | T3.2, signed schema |
| T3.5 | Seed script in `scripts/`: about 20 reports with varied locations, including 2 close groups                                                                                                                                                                             | Rows visible in Supabase              | T3.4                |

## M4 Computer Vision - `ml/damage_detection`, `data`
| ID   | Task                                                                                                                                                                                   | Done when                                                                                                        | Depends on |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | ---------- |
| T4.1 | Verify RDD2022 license and annotation format; report class list and image/class counts per country subset (especially pothole). Deadline: 48 hours                                     | Findings in `ml/damage_detection/README.md` and posted to the team; triggers the DEC-10 choice and vocabulary §3 | none       |
| T4.2 | Convert annotations to YOLO format, remove corrupt images, create train/val/test splits, write `data.yaml`. Raw data stays out of git                                                  | Splits verified and documented                                                                                   | T4.1       |
| T4.3 | Colab smoke run: YOLOv8n, few epochs, checkpoints to Drive every epoch, logged in the training-run template (model, image size, epochs, batch, augmentation, dataset version, metrics) | Checkpoint and log saved                                                                                         | T4.2       |
| T4.4 | `detect(image_bytes)` returning a list of {class_name, confidence, bbox} per `vocabulary.md` §5 (pretrained weights are fine for now)                                                  | Callable function with a sample test                                                                             | T4.1       |

## M5 Severity + DBSCAN - `ml/severity`, `ml/clustering`
| ID   | Task                                                                                                                                                                                              | Done when                           | Depends on      |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | --------------- |
| T5.1 | `ml/severity/rules.yaml` and README: category weights, area thresholds, aggregation across detections, zero detections = None                                                                     | Rules documented                    | T4.1 class list |
| T5.2 | `severity(detections, image_size)` returning {label, score}, with pytest tests in `tests/unit` (boundaries, zero, multiple detections)                                                            | Tests pass                          | T5.1            |
| T5.3 | `cluster(coordinates)`: DBSCAN with haversine metric, configurable eps in meters; hand-labeled coordinate test sets (tight group, two separated groups, isolated point, near-eps edge) with tests | Tests pass                          | none            |
| T5.4 | Check duplicates and leakage between dataset subsets and splits with M4; write the local photo collection plan (who, where, how many; blur faces and plates) in `data/README.md`                  | Leakage check recorded; plan merged | T4.2            |

## M6 Dashboard + Deployment - `apps/dashboard`
| ID   | Task                                                                                                                                                                                                            | Done when                                          | Depends on |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------- |
| T6.1 | Record hosting results (RAM, cold start, inference time) in `docs/decisions/hosting-test.md`, recommend a backend host, choose the static host for the dashboard. Leader closes DEC-11 with a superseding entry | Table and recommendation merged; DEC-11 superseded | T2.2       |
| T6.2 | React project scaffold and login screen: staff enters the API key, kept in session memory only, sent in the `X-API-Key` header                                                                                  | Header sent on every request                       | none       |
| T6.3 | Report list on stub data: severity descending then newest, filters by category and status                                                                                                                       | Matches stub data                                  | T6.2, T2.3 |
| T6.4 | Detail page skeleton: photo, fields, status control                                                                                                                                                             | Opens from the list                                | T6.3       |

## Milestone 1 checklist
- [ ] Contract, schema, vocabulary signed off and committed, with `openapi.json`
- [ ] App and dashboard both read stub endpoints
- [ ] Dataset classes and splits verified
- [ ] Hosting results documented, a host recommended, DEC-11 closed
- [ ] Severity and clustering unit tests pass
- [ ] Supabase schema, bucket, and seed data live
- [ ] Colab smoke run completed
- [ ] All six roles have a named owner