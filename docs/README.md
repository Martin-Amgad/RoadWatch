**Project Specification (v1.0)** Team size: 6 members | Duration: 6 weeks | Estimated difficulty: 7/10

**How to use this document.** This is the primary reference for the RoadWatch team. Requirements are labeled **[MVP]** (mandatory), **[Optional]** (only after the MVP is stable), or **[Assumption] / [Decision needed]** (to be confirmed by the team in Week 1). Where this document says "preliminary," the output is an aid for human reviewers, not an authoritative assessment.

> **Status: partly superseded.** Where this spec and `docs/decisions/decisions.md`
> disagree, the decision log wins. If `vocabulary.md` disagrees, `vocabulary.md` wins on names and strings.
>
> | Spec says                                    | Now                                                      | Source           |
> | -------------------------------------------- | -------------------------------------------------------- | ---------------- |
> | 6 weeks                                      | 4 weeks                                                  | DEC-01           |
> | D-4 default: single-call                     | Two-step: `/analyze` then `/reports`, with analysis cache | DEC-03, DEC-04   |
> | D-2 dashboard served with backend            | Separate React static site                               | DEC-07           |
> | D-5 Supabase Auth or shared key              | Shared API key in `X-API-Key`                            | DEC-06           |
> | D-6 DBSCAN params set in Week 4              | Set in Week 3                                            | decisions.md     |
> | `severity` field in example response         | `severity_label` and `severity_score`                    | vocabulary.md §4 |
> | `staff_users` table                          | Dropped (no per-user identity)                           | DEC-06           |
> | `reporter_ref`, `GET /reports/mine`, M-8     | Dropped                                                  | DEC-01           |
> | D-7 Leaflet map, MLflow, HF Hub, image-quality check | Cut                                              | DEC-01           |
> | D-8 GPS fallback                             | Block submission                                         | DEC-08           |
> 
---

## 1. Project Overview

RoadWatch is an AI-powered system that lets citizens report road damage (potholes and cracks) from a smartphone, and helps municipal staff review, prioritize, and track those reports.

The system has two interfaces connected to one shared backend:

| Interface           | Users           | Purpose                                                                                                                                                        |
| ------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Flutter mobile app  | Citizens        | Photograph road damage, receive an AI-generated damage category and preliminary severity, attach GPS location and an optional description, and submit a report |
| Web admin dashboard | Municipal staff | View reports in severity order, filter them, inspect potential duplicates, and update report status                                                            |

The core value of RoadWatch is the end-to-end pipeline: photo → AI detection → severity estimate → location-tagged report → duplicate grouping → prioritized staff review → status tracking.

---

## 2. Problem Statement and Target Users

### 2.1 Problem

Road damage is often reported slowly, inconsistently, and without structured data. Municipal authorities struggle to:

- Identify what kind of damage exists and where.
- Judge which reports are most urgent.
- Recognize that several reports may refer to the same road issue.
- Track whether and when repairs happen.

### 2.2 Target Users

| User            | Needs                                                                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Citizen         | A fast way to report damage with a photo and location, immediate feedback, and confirmation that the report was received                        |
| Municipal staff | A clear, severity-ordered list of reports with photos, locations, and statuses; visibility into likely duplicates; the ability to update status |

---

## 3. Objectives and Scope

### 3.1 Objectives

1. Deliver a working, deployed, end-to-end application (mobile app + backend + dashboard) using real model inference and real persistence.
2. Fine-tune and evaluate a YOLOv8n road damage detector using public data.
3. Provide a transparent, documented, preliminary severity-scoring mechanism.
4. Group geographically close reports as potential duplicates using DBSCAN, without deleting or merging originals.
5. Provide basic report lifecycle management (Submitted → Under Review → Resolved).
6. Evaluate the model, clustering, API, and full workflow with documented tests.

### 3.2 In Scope [MVP]

- Flutter app: camera/gallery capture, GPS, optional description, AI result display, report submission.
- FastAPI backend: validation, inference, severity scoring, storage, clustering, dashboard endpoints.
- PostgreSQL/PostGIS database (Supabase) and object storage for images.
- Simple web dashboard: severity-sorted list, filters, report detail, duplicate groups, status updates.
- Evaluation, integration testing, and deployment.

### 3.3 Out of Scope (unless promoted from Optional)

- Image-similarity-based duplicate detection.
- Video-frame analysis.
- Repair-cost estimation.
- Push notifications.
- Complex administration features (user management UI, analytics suites).
- Asynchronous job queues (introduce only if synchronous inference proves unworkable).
- Attention-based NLP models (no meaningful text-based feature is required).

### 3.4 Assumptions

- [Assumption] The demonstration targets a single city or small geographic area (to be named in Week 1), which determines the DBSCAN distance threshold and local test data collection.
- [Assumption] Free-tier hosting is used; limits must be verified in Week 1.
- [Assumption] Staff authentication uses a minimal mechanism (see Section 11.4).

---

## 4. Functional Requirements

### 4.1 Citizen Mobile Application (Flutter)

| ID  | Requirement                                                                                                                                                                   | Priority                                                                           |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| M-1 | Capture a photo with the device camera                                                                                                                                        | MVP                                                                                |
| M-2 | Select an existing image from the gallery                                                                                                                                     | MVP                                                                                |
| M-3 | Request and handle location permission (granted, denied, services off) and obtain GPS coordinates                                                                             | MVP                                                                                |
| M-4 | Send the image to the backend for analysis and display the predicted damage category(ies), confidence, and preliminary severity                                               | MVP                                                                                |
| M-5 | Allow an optional text description                                                                                                                                            | MVP                                                                                |
| M-6 | Submit the report and display a success or failure confirmation                                                                                                               | MVP                                                                                |
| M-7 | Handle errors gracefully: failed upload, unreadable image, no network, no supported damage detected (user may retake the photo or choose to submit anyway — see decision D-3) | MVP                                                                                |
| M-8 | Display the user's previously submitted reports and their statuses                                                                                                            | Optional (low-cost if a device local list of report IDs is used; see Section 11.4) |
| M-9 | Display a clear notice that AI results are preliminary                                                                                                                        | MVP                                                                                |

### 4.2 Web Admin Dashboard

| ID  | Requirement                                                                                                                         | Priority |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | -------- |
| D-1 | Retrieve and list reports from the backend                                                                                          | MVP      |
| D-2 | Default sort: highest severity first (ties broken by newest submission)                                                             | MVP      |
| D-3 | Per report, show: photo, damage category, severity, GPS coordinates, description, submission date, status                           | MVP      |
| D-4 | Filter by damage category and by status                                                                                             | MVP      |
| D-5 | Update status: Submitted, Under Review, Resolved                                                                                    | MVP      |
| D-6 | Show potential duplicate groups: reports in the same cluster are visibly grouped or labeled, with originals individually accessible | MVP      |
| D-7 | Interactive map (Leaflet + OpenStreetMap) with report markers and cluster highlighting                                              | Optional |

A simple list or table is sufficient for the MVP. The dashboard prioritizes clarity over features.

### 4.3 Duplicate Report Management

- [MVP] Identify reports from nearby locations and assign them a shared cluster identifier.
- [MVP] Present grouped reports to staff as potential duplicates.
- [MVP] Never automatically delete or permanently merge reports; originals and their descriptions are preserved.
- [MVP] Update cluster assignments when new reports arrive.

Limitation: Geographic proximity alone does not establish that two reports describe the same physical damage. Clusters are suggestions for human review.

---

## 5. Non-Functional Requirements

| Category        | Requirement                                                                                                                                                                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reliability     | Submission either fully succeeds (image stored, record saved) or fails with a clear error; no partial reports left in an inconsistent state                                                                                |
| Performance     | Measure and report inference latency and end-to-end submission time. [Decision needed] A latency target should be set only after benchmarking in Week 2; no target is assumed in advance                                   |
| Usability       | The citizen flow should require few steps (capture → review result → submit); the dashboard should be understandable without training                                                                                      |
| Security        | Validate all inputs (file type, size, coordinate ranges); restrict status updates to authorized staff; keep secrets out of version control; use HTTPS in deployment                                                        |
| Privacy         | Blur faces and license plates in locally collected photographs used in documentation or demonstration. [Decision needed] Whether to blur citizen-submitted images server side (stretch) or show a privacy notice (minimum) |
| Maintainability | Versioned API contract, documented schema, per-component README, consistent label and status vocabulary                                                                                                                    |
| Reproducibility | Training configuration, dataset version, and results are recorded so the chosen model can be reproduced                                                                                                                    |
| Responsible AI  | AI output is always labeled preliminary; staff retain final judgment on severity and duplicates                                                                                                                            |

---

## 6. User Workflows

### 6.1 Citizen Report Workflow

1. **Capture:** The citizen takes a photo or selects one from the gallery.
2. **Analyze:** The app sends the image to the backend (/analyze). The backend validates the file, runs YOLOv8n inference, and computes preliminary severity.
3. **Review:** The app displays the detected category, confidence, and severity (labeled preliminary). If nothing is detected, the app explains this and offers retake or submit-anyway (per D-3).
4. **Add details:** The app attaches GPS coordinates and accepts an optional description.
5. **Submit:** The app sends the report (/reports). The backend stores the image in object storage and the record in PostgreSQL/PostGIS, then updates clustering.
6. **Confirm:** The app shows a confirmation with a report ID.

**Design note:** To keep a single source of truth and avoid trusting client-supplied predictions, the backend should either (a) re-run inference at submission time, or (b) cache analysis results server-side keyed by an analysis ID returned from /analyze. [Decision needed in Week 1] Option (b) is recommended to avoid double inference cost. Alternatively, a single-call design (POST /reports runs inference and returns the result in the response) is simpler; the team should choose one and document it.

### 6.2 Staff Review Workflow

1. Staff open the dashboard and sign in.
2. The dashboard lists reports in severity order.
3. Staff filter by category or status as needed.
4. Staff open a report to view the photo, details, and any potential duplicates in the same cluster.
5. Staff update the status (Submitted → Under Review → Resolved).

---

## 7. AI/ML Components and Evaluation

### 7.1 Road Damage Detection [MVP]

- **Model:** YOLOv8n (Ultralytics), initialized from pretrained weights and fine-tuned on a road damage dataset (transfer learning).
- **Classes:** Those supported by the selected training data (e.g., longitudinal cracks, transverse cracks, alligator cracks, potholes). The final class list is fixed in Week 1 after dataset inspection.
- **Input:** An RGB image (JPEG/PNG).
- **Output:** A list of detections, each with class label, confidence, and bounding box.

### 7.2 Severity Estimation [MVP]

A lightweight, rule-based score computed from model outputs.

**Inputs:**
- Predicted damage category.
- Bounding-box area as a fraction of image area.
- Detection confidence.
- Optional additional visual measurements, if feasible.

**Output:** One severity label per report: Low, Medium, or High, and optionally a numeric score used for sorting within a level.

**Requirements:**
- Scoring rules must be written down (category weights, area thresholds, aggregation across multiple detections, handling of zero detections) in a short document or config file and kept in version control.
- [Assumption] Category weights and area thresholds are initial team judgments, not engineering standards. They may be tuned by inspecting dataset examples, but must not be presented as validated against professional assessments.
- The mobile app and dashboard must label severity as a preliminary, image-based indicator, not a professional engineering assessment.
- A report with no detection has severity "Unknown/None" ([Decision needed], see D-3) and sorts last.

Example structure (illustrative only; thresholds to be set by the team):

```
score = category_weight[category] * area_fraction_factor * confidence
severity = "High" if score >= T_high else "Medium" if score >= T_medium else "Low"
```

### 7.3 Image Validation

- [MVP, minimum] Handle failed uploads, unreadable or corrupt images, unsupported formats, oversized files, and cases where the detector finds no supported damage.
- [Optional] A pretrained classifier or lightweight heuristic (e.g., blur or darkness checks, non-road image rejection). Do not delay the MVP for this feature.

### 7.4 Geographic Clustering (DBSCAN) [MVP]

- **Algorithm:** DBSCAN (scikit-learn) on report coordinates.
- **Distance:** Use the haversine metric (coordinates in radians) so eps can be expressed in meters (eps = meters / 6,371,000).
- **Parameters:** eps and min_samples are configurable. [Decision needed] Initial values should be chosen in Week 4 based on the demonstration's geographic scale and GPS accuracy; min_samples = 2 is a reasonable starting point for pairs of reports. Parameters are documented and justified using test coordinates.
- **Output:** A cluster_id per report (or none for noise/unclustered reports).
- **Update strategy:** After each new report, recompute clusters. At the expected demonstration scale (tens to hundreds of reports), a full recompute is acceptable. [Assumption] Large-scale incremental clustering is out of scope.
- **Stability note:** Because DBSCAN labels are not stable between runs, cluster identifiers should be treated as regenerated values; reports should not depend on a specific label persisting.
- **Constraint:** Reports are never deleted or merged; clustering only adds a grouping label.

**Limitation:** DBSCAN captures proximity, not semantic similarity. Nearby reports may describe different damage, and the same damage may be reported from points farther apart than eps because of GPS inaccuracy. Staff make the final determination.

[Optional] Image-similarity-based duplicate detection is outside MVP scope.

### 7.5 Model Evaluation

**Detector (on a held-out test split not used for training or model selection):**
- mAP@0.5 (overall).
- Per-class precision and recall.
- Inference time per image (state hardware and image size used; also measure on the deployment environment).

**Clustering:**
- Representative coordinate test sets with manually labeled expected groups (e.g., a tight group of reports, two groups separated by a gap, isolated reports, edge cases near eps).
- Tests with nearby and geographically distant reports verify that groups form and separate as expected.
- Qualitative review of failure cases (e.g., GPS drift).

**Severity:**
- Unit tests with fixed inputs verifying the documented rules (boundary cases, zero detections, multiple detections).
- Manual review of a sample of outputs for plausibility. No accuracy metric is claimed, since no ground truth severity labels are assumed.

**End-to-end:**
- Run the full workflow on locally collected photographs that were not used in training or model selection.
- Report results honestly, including failures. No performance targets are assumed in advance.

---

## 8. Dataset and Data Preparation

### 8.1 Data Sources

| Source                                           | Role                                    | Notes                                                                                                                                                                                                   |
| ------------------------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RDD2022                                          | Primary training and evaluation data    | Verify the license, class definitions, country subsets used, and annotation format. Note that RDD2022 test set labels may not be public for all subsets, so the team should plan its own held-out split |
| Roboflow Universe road damage / pothole datasets | Optional supplementary data             | Only after license, class-mapping, and quality checks; watch for overlap with RDD2022                                                                                                                   |
| Locally collected photographs                    | Local validation and demonstration only | Never used for training or model selection; faces and plates blurred where appropriate                                                                                                                  |

### 8.2 Preparation Steps (required before training)

1. Inspect available classes and annotation formats.
2. Convert annotations to YOLO format (class, normalized x-center, y-center, width, height).
3. Remove corrupted or unusable images and invalid annotations.
4. Analyze class distribution and note imbalance.
5. Check for duplicates and overlap, especially across merged datasets, to avoid train/test leakage.
6. Create train/validation/test splits (the test set is touched only for final evaluation).
7. Define a unified class mapping if multiple sources are used.
8. Store the data configuration (data.yaml) and dataset version/source notes in version control (not the raw data).

### 8.3 Local Photograph Collection

- [Assumption] A modest set of photographs is collected by team members in the demonstration area (target quantity to be set by the team in Week 1).
- Photographs must be kept entirely separate from training data.
- Blur faces and license plates before sharing in reports or presentations.

### 8.4 Compute

[Decision needed] Training resources (e.g., Google Colab, Kaggle, or local GPU) must be confirmed in Week 1. If resources are limited, use a manageable subset of the dataset and smaller image size, and document this.

---

## 9. Technology Stack

| Layer               | Technology                                                                                                                                   | Status                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Mobile app          | Flutter                                                                                                                                      | Essential                                                                                            |
| Backend API         | Python, FastAPI                                                                                                                              | Essential                                                                                            |
| Computer vision     | Ultralytics YOLOv8 (YOLOv8n)                                                                                                                 | Essential                                                                                            |
| Clustering          | scikit-learn DBSCAN                                                                                                                          | Essential                                                                                            |
| Database            | PostgreSQL + PostGIS (Supabase)                                                                                                              | Essential                                                                                            |
| Image storage       | Supabase Storage (or equivalent object storage)                                                                                              | Essential                                                                                            |
| Dashboard frontend  | [Decision needed] Lightweight web UI (e.g., plain HTML/JS, or a simple framework the team already knows), served by or alongside the backend | Essential                                                                                            |
| Map (optional)      | Leaflet + OpenStreetMap                                                                                                                      | Optional                                                                                             |
| Experiment tracking | MLflow                                                                                                                                       | Optional (recommended for training; local logging is acceptable)                                     |
| Model hosting       | Hugging Face Hub                                                                                                                             | Optional (only if deployment needs it; otherwise ship weights with the backend or in object storage) |
| Deployment          | Render or equivalent                                                                                                                         | Essential (one host chosen by end of Week 1 after checks)                                            |
| Version control     | Git + GitHub (branch/PR workflow)                                                                                                            | Essential                                                                                            |

**Essential vs. optional:** The MVP must work without MLflow, Hugging Face Hub, and Leaflet. If these are used, they must not become blocking dependencies.

---

## 10. System Architecture and Data Flow

### 10.1 Components

```
┌──────────────┐         ┌──────────────────────────────────────────┐
│ Flutter      │──HTTPS─▶│ FastAPI Backend                          │
│ App          │         │ • request validation                     │
└──────────────┘         │ • YOLOv8n inference                      │
                         │ • severity scoring                       │
┌──────────────┐         │ • DBSCAN clustering                      │
│ Web Dashboard│──HTTPS─▶│ • staff auth, status updates             │
└──────────────┘         └───────────┬───────────────┬──────────────┘
                                     │               │
                         ┌───────────▼──────┐  ┌─────▼────────────┐
                         │ PostgreSQL +     │  │ Object storage   │
                         │ PostGIS          │  │ (report photos)  │
                         │ (metadata,       │  │                  │
                         │ image refs)      │  │                  │
                         └──────────────────┘  └──────────────────┘
```

### 10.2 Report Submission Flow

1. Flutter sends the image (and later, coordinates and description) to FastAPI.
2. FastAPI validates the request and image.
3. FastAPI runs YOLOv8n inference and severity scoring.
4. FastAPI uploads the image to object storage and receives its URL/path.
5. FastAPI inserts the report record (including the image reference, predictions, severity, and location) into PostgreSQL/PostGIS.
6. FastAPI recomputes/updates DBSCAN cluster assignments.
7. FastAPI returns the report ID and result to the app.
8. The report becomes visible on the dashboard.

### 10.3 Duplicate Detection Flow

New report stored → DBSCAN recomputed over existing reports → cluster_id values updated → dashboard queries return cluster information.

### 10.4 Dashboard Flow

Dashboard → FastAPI endpoints → database queries (severity-ordered, filtered) → rendered list, with duplicate groupings.

### 10.5 Design Principles

- **Synchronous processing:** Inference, scoring, and clustering run within the request. No message queue or worker infrastructure in the MVP. Revisit only if benchmarking shows the request time is unacceptable on the chosen host.
- **Images are never stored in database rows.** Images live in object storage; the database stores references (URL or storage path) only.
- **Backend as the single authority:** The backend validates input, coordinates inference, stores data, and returns consistent results to both interfaces. Clients do not compute severity or clusters.
- **Model loaded once at startup, not per request.**
- **Early feasibility check:** In Week 1–2, benchmark model memory use and inference latency on the intended host before committing to it.

---

## 11. Database and API Requirements

### 11.1 Database Schema (initial proposal, to be finalized in Week 1)

**reports**

| Column                 | Type                   | Notes                                                |
| ---------------------- | ---------------------- | ---------------------------------------------------- |
| id                     | UUID (PK)              | Report identifier                                    |
| created_at             | timestamptz            | Submission time                                      |
| updated_at             | timestamptz            | Last status change                                   |
| image_url / image_path | text                   | Reference to object storage                          |
| location               | geography(Point, 4326) | PostGIS point; also store lat/lon accessible for API |
| description            | text, nullable         | Optional citizen text                                |
| damage_category        | text                   | Primary (highest-priority) detected class, or null   |
| confidence             | float                  | Confidence of the primary detection                  |
| detections             | jsonb                  | Full detection list (class, confidence, bbox)        |
| severity_label         | text                   | Low / Medium / High / None                           |
| severity_score         | float                  | Used for sorting                                     |
| status                 | text                   | Submitted / Under Review / Resolved                  |
| cluster_id             | integer, nullable      | DBSCAN label (null = unclustered)                    |
| reporter_ref           | text, nullable         | Anonymous device ID, if M-8 is implemented           |

**staff_users (minimal; or use Supabase Auth instead)**

| Column          | Type |
| --------------- | ---- |
| id, email, role | —    |

**Indexes:** spatial index on location; indexes on severity_score, status, damage_category.

**Shared vocabulary (fixed in Week 1):**
- Status: Submitted, Under Review, Resolved.
- Severity: Low, Medium, High (and None for no detection).
- Damage categories: fixed list from the trained model's classes.

### 11.2 API Endpoints (initial contract; finalize in Week 1)

| Method | Endpoint                    | Purpose                                                                     | Auth                   |
| ------ | --------------------------- | --------------------------------------------------------------------------- | ---------------------- |
| POST   | /api/v1/analyze             | Upload image → detections, severity (optional step; see design note in 6.1) | Public                 |
| POST   | /api/v1/reports             | Submit report (image, lat, lon, description) → report ID and result         | Public                 |
| GET    | /api/v1/reports             | List reports; query params: sort, category, status, pagination              | Staff                  |
| GET    | /api/v1/reports/{id}        | Report detail including cluster mates                                       | Staff                  |
| PATCH  | /api/v1/reports/{id}/status | Update status                                                               | Staff                  |
| GET    | /api/v1/clusters            | Cluster groupings (or included in list response)                            | Staff                  |
| GET    | /api/v1/health              | Health check (for deployment and testing)                                   | Public                 |
| GET    | /api/v1/reports/mine        | Citizen's own reports by reporter_ref                                       | Public (optional, M-8) |

**Contract requirements:**
- Document with FastAPI's auto-generated OpenAPI spec; commit an exported copy in Week 1.
- Define request/response JSON examples, error format (consistent status codes and error body), and field names before implementation.
- Validate: image type and size limit, latitude in [-90, 90], longitude in [-180, 180], description length cap, valid status transitions.
- Consider API versioning (/api/v1) from the start.

**Example submission response (illustrative):**

```json
{
  "report_id": "uuid",
  "damage_category": "pothole",
  "confidence": 0.82,
  "severity": "High",
  "status": "Submitted",
  "cluster_id": 3
}
```

### 11.3 Public Endpoint Abuse Protection

- [MVP, minimal] Enforce file-size and type limits.
- [Optional] Basic rate limiting.

### 11.4 Authentication [Decision needed]

- **Staff:** The status-update and listing endpoints must be restricted. The simplest acceptable option is a single shared staff credential or API key, or Supabase Auth with a few pre-created accounts. Full role-based access control is [Optional].
- **Citizens:** The MVP does not require citizen accounts; submissions are anonymous. If M-8 is implemented, use an anonymous device identifier stored locally.

---

## 12. Team Responsibilities

Each member owns one primary workstream and is accountable for its deliverables. Integration, testing, and documentation are shared.

| #   | Role                             | Primary ownership (accountable for)                                                                                                                                                      | Key deliverables                                                      |
| --- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Mobile Application               | Flutter UI, camera/gallery, GPS permissions, API client, result and confirmation screens, error handling                                                                                 | Working app consuming the API; M-1 to M-9                             |
| 2   | Backend and Security             | FastAPI service structure, endpoints, request validation, authentication, image-storage integration, orchestration of inference → severity → storage → clustering, OpenAPI documentation | Stable, documented API; D-1 to D-5 server support                     |
| 3   | Database and Geospatial Data     | PostgreSQL/PostGIS schema and migrations, indexes, spatial queries, Supabase setup, data access layer, seed/test data                                                                    | Schema, queries, and data access used by the backend                  |
| 4   | Computer Vision                  | Dataset preparation, annotation conversion, YOLOv8n training, experiment records, detector evaluation, inference module (a function/class the backend calls), latency benchmarking       | Trained weights, evaluation report, detect(image) → detections module |
| 5   | Severity and Duplicate Detection | Severity-scoring module and documented rules, DBSCAN module (cluster(reports) → labels), parameter selection, component-level unit tests                                                 | Pure Python modules with tests, consumed by the backend               |
| 6   | Admin Dashboard and Deployment   | Dashboard UI (list, filters, detail, duplicates, status update), deployment pipeline, environment configuration, coordination of end-to-end testing                                      | Deployed dashboard and backend; integration test checklist            |

### 12.1 Interfaces Between Owners

| Boundary                   | Contract                                                                                                              |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Member 4 → Member 2        | Inference module: input image bytes/array → list of {class, confidence, bbox}                                         |
| Member 5 → Member 2        | Severity function: detections + image size → {label, score}; clustering function: report coordinates → cluster labels |
| Member 3 → Member 2        | Data-access functions for insert, query, filter, update, and cluster-label write back                                 |
| Member 2 → Members 1 and 6 | OpenAPI contract                                                                                                      |

### 12.2 Shared Responsibilities

- **Week 1 agreement (all members):** API request/response formats, database fields, report statuses, severity labels, damage categories, and coding conventions.
- **Integration:** Member 6 coordinates the schedule; every member resolves integration issues involving their own component.
- **Testing and documentation:** Each member writes tests and a short README for their component; all members participate in end-to-end testing and the final demonstration.
- **Backup coverage (suggested pairing):** 1↔6 (front-end work), 2↔3 (backend/data), 4↔5 (ML/Python modules), so that a delayed or unavailable member does not block the project.
- **Local data collection:** Shared across all members.
- **Code review:** Pull requests are reviewed by at least one other member.

---

## 13. Six-Week Development Roadmap

**Principle:** A minimal working vertical slice (even with a placeholder model) exists by the end of Week 2; every real component is integrated by the end of Week 3; Weeks 5–6 are reserved for evaluation, deployment hardening, and the demo, not new features.

### Week 1 — Requirements and Foundations

**Tasks**
- All: finalize MVP scope, API contract, DB schema, shared vocabulary, and git workflow.
- All: resolve [Decision needed] items (Section 16.3); pick hosting, dashboard stack, and auth approach.
- M4: acquire and inspect RDD2022; confirm classes, license, and training compute; convert annotations; create splits.
- M3: set up Supabase project, create schema and storage bucket.
- M2: scaffold FastAPI project with health endpoint and stub endpoints returning contract-shaped data.
- M1/M6: basic app and dashboard skeletons reading stub data.
- M6/M2: check deployment feasibility (memory, cold start, free-tier limits) with a hello-world backend.
- M5: draft severity rules and DBSCAN interface with sample data.

**Milestone 1 (measurable):** Signed-off API contract and schema committed; dataset prepared with verified annotations and splits; stub endpoint reachable from both the app and the dashboard.

### Week 2 — Baseline Model and Reporting Pipeline

**Tasks**
- M4: train the YOLOv8n baseline; record the configuration and metrics; benchmark inference time; deliver an inference module (even if the baseline is weak).
- M2/M3: implement report submission with image upload to storage and record insertion.
- M1: camera, gallery, GPS permission, and form working; submits to the real API.
- M6: dashboard list pulling real stored reports.
- M5: implement severity module and DBSCAN module with unit tests (not yet integrated).

**Milestone 2:** A photo and location submitted from the app are stored in the database and storage, and appear in the dashboard (detection may still be stubbed).

### Week 3 — End-to-End AI Integration

**Tasks**
- M2/M4: integrate the detector into the backend; return categories and confidence.
- M2/M5: integrate severity scoring and store results.
- M1: display detection results and preliminary-severity notice.
- M6: dashboard shows category, severity, and photo from real data.
- M4: improve model if needed (keep experiments bounded).
- M1/M6/M2: first end-to-end run with real inference.

**Milestone 3:** A citizen submits a photo and the report appears on the dashboard with real model-generated category and severity. Feature freeze for the core pipeline — later weeks refine rather than add.

### Week 4 — Severity Ordering, Duplicates, and Status Management

**Tasks**
- M5/M2/M3: integrate DBSCAN; store cluster_id; tune eps/min_samples using test coordinates.
- M6/M2: implement severity sorting, filters, status updates, and duplicate-group display.
- M2: add authentication to staff endpoints.
- M1/M2: strengthen error handling and image validation; handle no-detection cases.
- [Optional] Map view or image-quality check only if all MVP items above are stable.

**Milestone 4:** Staff can sort, filter, update status, and see potential duplicate groups; the full MVP feature set is present (possibly rough).

### Week 5 — Evaluation and Deployment

**Tasks**
- M4: final detector evaluation on the held-out test set (mAP@0.5, per-class precision and recall, inference time).
- M5: finalize clustering and severity tests; document rules and parameters.
- M6/M2: deploy backend and dashboard; configure environment variables and secrets; build the mobile app against the deployed API.
- All: run the integration test checklist on the deployed system; test with local photographs.
- All: triage and fix major defects.

**Milestone 5:** Deployed, publicly reachable system passing the core integration checklist; evaluation numbers recorded.

### Week 6 — Validation and Final Presentation

**Tasks**
- All: fix remaining defects; no new features.
- All: complete usability testing and a full demonstration rehearsal on the deployed environment (twice or more).
- M4/M5: document model performance, limitations, and severity rules.
- M2/M6: ensure demonstration data and a fallback plan (e.g., pre-validated photos, recorded backup demo).
- All: final documentation, architecture description, and presentation.

**Milestone 6:** Stable, documented system with a repeatable demonstration verified in the deployment environment.

**Schedule buffer:** The team should treat late Week 5 and early Week 6 as contingency time. If the model underperforms, document the results honestly rather than delaying integration.

---

## 14. Testing and Acceptance Criteria

### 14.1 Test Levels

| Level       | Scope                                                                                      | Owner                | Method                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------ | -------------------- | --------------------------------------------------------------------------------------------- |
| Unit        | Severity rules, DBSCAN function, annotation conversion, input validators                   | M5, M4, M2           | Automated tests (e.g., pytest) with fixed inputs                                              |
| Model       | Detector metrics, inference time                                                           | M4                   | Held-out test set evaluation                                                                  |
| Clustering  | Grouping and separation behavior                                                           | M5                   | Hand-labeled coordinate sets (close group, separated groups, isolated points, boundary cases) |
| API         | Endpoint behavior, validation, error responses, auth                                       | M2                   | Automated tests / OpenAPI-based tests against a test database                                 |
| Persistence | Data survives restarts; image reference resolves; filters and sorts return correct results | M3                   | Insert/query tests; backend restart test                                                      |
| Mobile      | Permissions, capture flows, error states                                                   | M1                   | Manual test checklist on at least two devices/OS versions if available                        |
| Dashboard   | Sort order, filters, status updates, duplicate display                                     | M6                   | Manual checklist against seeded data                                                          |
| End-to-end  | Full workflow on deployed system                                                           | All (M6 coordinates) | Scripted scenario with local photographs                                                      |

### 14.2 Acceptance Criteria — the MVP is complete when all are true

**Citizen app**
- A report can be created from a camera photo and from a gallery image.
- GPS coordinates are attached; permission denial is handled with a clear message and a defined fallback.
- Predicted category and preliminary severity are displayed and labeled as preliminary.
- Failed upload, unreadable image, no network, and no-detection cases each show a clear, non-crashing response.
- Submission returns a confirmation.

**Backend and data**
- Real YOLOv8n inference (not hardcoded values) produces the stored category/detections.
- The report, detections, severity, status, and location persist in PostgreSQL/PostGIS after a backend restart.
- The image is stored in object storage and the database holds a working reference to it.
- Invalid input (bad file type, oversized file, out-of-range coordinates) is rejected with a defined error.
- Staff-only endpoints reject unauthenticated requests.

**Severity and duplicates**
- Severity rules are documented and their unit tests pass.
- Reports from nearby coordinates receive the same cluster_id; reports from distant coordinates do not (verified on documented test sets).
- No report is deleted or merged by clustering; originals remain individually viewable.
- Clusters update when new reports arrive.

**Dashboard**
- Reports display in severity order (highest first).
- Filtering by category and by status works.
- Each report shows photo, category, severity, location, description, date, and status.
- Staff can update status, and the change persists.
- Potential duplicate groups are visible and labeled as potential.

**Evaluation**
- Detector evaluated on a held-out test set; mAP@0.5, per-class precision/recall, and inference time are recorded and reported honestly. (No minimum threshold is assumed; results and limitations are documented.)
- The full workflow is run on locally collected photographs not used in training; outcomes, including failures, are documented.

**Deployment**
- Backend, database, storage, and dashboard are deployed and reachable.
- The mobile app, built against the deployed backend, completes the full demonstration scenario at least twice consecutively without code changes.

### 14.3 Definition of Done (per feature)

Implemented, reviewed by another member, tested, documented in the component README, and merged to the main branch.

---

## 15. Deployment and MLOps

### 15.1 Deployment

- **Backend:** FastAPI deployed to Render or an equivalent host. [Decision needed in Week 1] Verify free tier RAM, CPU, cold-start behavior, request timeout, and whether the YOLOv8n model (and its PyTorch dependencies) fits. If not, choose an alternative host or export the model to a lighter runtime (e.g., ONNX), but only if required.
- **Database and storage:** Supabase (PostgreSQL/PostGIS, storage bucket). Verify free-tier limits (database size, storage, pausing of inactive projects).
- **Dashboard:** Served by the backend or hosted as a static site, per the Week 1 decision.
- **Mobile app:** Built as an installable debug/release APK (Android) or on a demo device; an app-store release is out of scope. [Assumption] Android is the demonstration platform; iOS only if a device and developer account are available.
- **Configuration:** Secrets and URLs in environment variables; never committed. Provide a .env.example.
- **Pre-demo check:** Wake/warm the backend before the demonstration to avoid cold-start delays.

### 15.2 MLOps (kept lightweight)

The team prioritizes reproducibility and a working inference pipeline over MLOps infrastructure.

**Required [MVP]**
- Record, for every training run: model variant, image size, epochs, batch size, augmentation settings, dataset version/split, and evaluation metrics.
- Save the best weights and the final model's configuration and evaluation results in the repository documentation (weights in storage or releases if large).
- Pin dependency versions (requirements.txt).
- Training scripts or notebooks committed so the chosen model can be reproduced.

**Optional**
- **MLflow:** Use to track a manageable set of experiments (a few runs). A local MLflow instance or a structured log/spreadsheet is an acceptable substitute. MLflow is not deployed as a production service.
- **Hugging Face Hub:** Host the final model artifact only if the deployment approach requires downloading weights at startup. Otherwise, include the weights in the backend deployment package or storage bucket.
- **Model versioning:** The deployed backend reports the model version (e.g., via the health endpoint) so test results can be tied to a specific model.

---

## 16. Risks, Limitations, and Mitigations

### 16.1 Risks

| Risk                                                                                        | Likelihood / impact | Mitigation                                                                                                                                                            |
| ------------------------------------------------------------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Training or inference constraints (limited compute, memory, slow inference on free hosting) | Medium / High       | Use YOLOv8n; use a dataset subset and smaller image size if needed; benchmark inference and memory in Weeks 1–2; fall back to ONNX or an alternative host if required |
| Weak detector accuracy                                                                      | Medium / Medium     | Bounded experimentation; focus on a working pipeline; report limitations honestly; keep the integration independent of model quality                                  |
| Limited local labeled data                                                                  | High / Low          | Train on public data; use local photos only for independent validation and demonstration                                                                              |
| Dataset license or compatibility problems                                                   | Medium / Medium     | Check licenses before use; document sources; prefer RDD2022 as the primary source; make supplementary data optional                                                   |
| Class imbalance or label inconsistency across datasets                                      | Medium / Medium     | Analyze distributions early; unify class mapping; avoid merging datasets without checks                                                                               |
| Severity subjectivity                                                                       | High / Medium       | Transparent, documented rules; label as preliminary; staff retain final judgment                                                                                      |
| False duplicate grouping or missed duplicates                                               | High / Low          | Treat clusters as suggestions; preserve originals; tune eps with test coordinates; account for GPS inaccuracy                                                         |
| GPS inaccuracy or denied permission                                                         | Medium / Medium     | Show accuracy-aware messaging; define the fallback (e.g., block submission or allow manual pin — [Decision needed])                                                   |
| Two-interface development overload                                                          | Medium / High       | Minimal dashboard; agree on the API contract in Week 1; use stub endpoints early                                                                                      |
| Integration delays                                                                          | Medium / High       | Vertical slice by end of Week 2; full integration by Week 3; feature freeze after Week 4                                                                              |
| Free-tier limits or outages (Supabase pausing, Render sleep, rate limits)                   | Medium / Medium     | Verify limits in Week 1; keep a local fallback environment (e.g., Docker Compose) for the demonstration; record a backup demo video                                   |
| Privacy of captured images (faces, plates)                                                  | Medium / Low        | Privacy notice in the app; blur local images used in documentation; do not publish citizen images                                                                     |
| Public endpoint abuse                                                                       | Low / Low           | File-size/type limits; optional rate limiting                                                                                                                         |
| Team member unavailability                                                                  | Medium / High       | Backup pairings (Section 12.2); clear interfaces; documentation per component                                                                                         |

### 16.2 Limitations (to be stated in the final documentation)

- Photograph-based severity is a preliminary indicator, not a professional engineering assessment.
- Camera angle, distance, lighting, and lack of scale references affect bounding-box measurements.
- Geographic proximity does not prove that two reports describe the same damage. Clusters are candidate groups for human review.
- The detector is limited to the categories in its training data and to conditions resembling that data; performance on local roads may differ.
- GPS accuracy varies, especially in dense urban areas.
- The system does not verify the authenticity of citizen reports.

### 16.3 External Dependencies

| Dependency                             | Essential? | Notes                                                                                                                 |
| -------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------- |
| Supabase (PostgreSQL/PostGIS, storage) | Essential  | Free-tier limits and project pausing must be checked                                                                  |
| Hosting (Render or alternative)        | Essential  | RAM/CPU/timeouts affect inference                                                                                     |
| RDD2022 dataset                        | Essential  | License and annotation checks required                                                                                |
| Ultralytics YOLOv8                     | Essential  | Check license terms (Ultralytics uses AGPL-3.0 with an enterprise option) and state them in the project documentation |
| OpenStreetMap tiles (map view)         | Optional   | Observe the tile usage policy                                                                                         |
| MLflow                                 | Optional   | Local usage is sufficient                                                                                             |
| Hugging Face Hub                       | Optional   | Only if needed for model hosting                                                                                      |
| Roboflow Universe datasets             | Optional   | License and quality checks required                                                                                   |

### 16.4 Unresolved Decisions (resolve in Week 1 unless noted)

| ID   | Decision                                                                           | Default if undecided                                                  |
| ---- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| D-1  | Hosting provider after feasibility check                                           | Render, or the alternative that meets memory requirements             |
| D-2  | Dashboard frontend stack                                                           | Simple HTML/JS served with the backend                                |
| D-3  | Behavior when no damage is detected (block, or allow submission as "Unclassified") | Allow submission with severity "None" and a warning; staff can review |
| D-4  | /analyze + /reports two-step flow vs. single-call submission                       | Single-call, unless the two-step preview is needed for the UX         |
| D-5  | Staff authentication mechanism                                                     | Supabase Auth with pre-created accounts, or a shared key              |
| D-6  | DBSCAN eps and min_samples                                                         | Set in Week 4 from test data                                          |
| D-7  | Latency target                                                                     | Set in Week 2 after benchmarking                                      |
| D-8  | GPS-unavailable fallback                                                           | Block submission, or manual pin if time permits                       |
| D-9  | Training compute environment                                                       | Google Colab or Kaggle                                                |
| D-10 | Demonstration city/area and size of local test set                                 | Chosen in Week 1                                                      |

---

## 17. MVP and Optional Extensions

### 17.1 Required MVP

- Flutter app with camera/gallery access, GPS-tagged reporting, optional description, and display of AI results.
- FastAPI backend with request validation and staff authentication.
- YOLOv8n fine-tuned detector with real inference in the pipeline.
- Documented, preliminary severity scoring.
- PostgreSQL/PostGIS persistence and object storage for images with references in the database.
- Web dashboard with severity-ordered list, filters by category and status, report detail, duplicate groups, and status updates.
- DBSCAN geographic grouping of potential duplicates (originals preserved).
- Model evaluation, integration testing, and deployment.

### 17.2 Optional Extensions (priority order; start only after the MVP works reliably)

1. Interactive Leaflet map with markers and cluster overlays.
2. User's own-report history in the app (if not already done as M-8).
3. Image-quality and non-road image classification.
4. Role-based staff access beyond the minimal authentication.
5. Status-change notifications.
6. Video-frame analysis.
7. Repair-cost estimation (stretch only; requires additional data and assumptions that detection alone does not provide).

**Rule:** No optional extension may delay or destabilize an MVP component. Optional work begins only after Milestone 4 criteria are met and is dropped if it risks the Week 5 deployment.

---

## 18. Final Deliverables and Demonstration

### 18.1 Deliverables

1. Working Flutter mobile application (installable build).
2. Deployed FastAPI backend with OpenAPI documentation.
3. Deployed web dashboard.
4. PostgreSQL/PostGIS database with schema and storage bucket.
5. Trained YOLOv8n weights, training configuration, and evaluation report.
6. Severity-scoring rules document and DBSCAN configuration/justification.
7. Test documentation (unit, API, integration, and end-to-end results).
8. Source code repository with READMEs and setup instructions.
9. Final documentation: architecture, model performance, limitations, and team contributions.
10. Final presentation and demonstration.

### 18.2 Demonstration Script

The demonstration must use real model inference and real backend persistence (no hardcoded predictions or mock reports).

1. A citizen photographs a pothole or selects a road-damage image.
2. The app obtains the GPS location and accepts an optional description.
3. The backend processes the image and the app displays the predicted category and preliminary severity.
4. The citizen submits the report and receives confirmation.
5. The report appears on the dashboard with its photograph, location, category, severity, and status.
6. The dashboard displays reports in severity order.
7. Several nearby reports (submitted live or previously created through the real pipeline) appear grouped as potential duplicates.
8. Staff update a report's status and the change is visible after refresh.

**Demonstration safeguards:** Rehearse on the deployed environment; warm up the backend beforehand; prepare pre-selected photos and locations; keep a backup screen recording.

---

## 19. Curriculum Alignment

| Course topic                         | How RoadWatch applies it                                                                                      |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Python Programming                   | FastAPI backend, inference module, severity and clustering modules, tests                                     |
| Data Preprocessing and Visualization | Dataset inspection, annotation conversion, cleaning, class-distribution analysis, plots of evaluation results |
| Machine Learning                     | DBSCAN clustering, parameter selection, and evaluation methods                                                |
| Deep Learning                        | YOLOv8n transfer learning and fine-tuning                                                                     |
| Computer Vision                      | Object detection, bounding-box-based severity measurements, image validation                                  |
| MLOps                                | Experiment tracking, model versioning, reproducible training, deployment                                      |
| Software Development                 | Mobile development, API design, database design, testing, version control, and deployment                     |
| Responsible AI                       | Image privacy, communication of uncertainty, human review of severity and duplicate suggestions               |

No attention-based NLP model is included, since the central problem is visual. NLP is added only if a meaningful text-based feature can be implemented without compromising the MVP.

---

## 20. Originality and Project Value

RoadWatch is an end-to-end civic technology system rather than a standalone object detection demo. It connects computer vision to location-aware reporting, flags potential duplicates, supports severity-based prioritization, and tracks report status through a staff workflow.

Its value comes from the integration of these components into a usable citizen-to-authority workflow, built within realistic student constraints and with honest communication of the AI's limitations.

