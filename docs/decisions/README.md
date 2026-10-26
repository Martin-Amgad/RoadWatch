# Decision Log

Format: each entry records the context, the options proposed, the choice, the reason, and the consequences. Entries are only changed by adding a new entry that supersedes the old one.

Date of all entries: 2026-10-27. Decision owner: team leader.

| ID     | Topic                             | Spec ID | Status         | Choice                                               |
| ------ | --------------------------------- | ------- | -------------- | ---------------------------------------------------- |
| DEC-01 | Scope freeze                      | -       | Decided        | A: MVP only                                          |
| DEC-02 | Role assignment                   | -       | Partly decided | Flutter member M1, web dev member M6; rest open      |
| DEC-03 | API flow                          | D-4     | Decided        | B: two-step with server-side cache                   |
| DEC-04 | Analysis cache                    | -       | Decided        | A: DB table plus temp image storage                  |
| DEC-05 | No-detection behavior             | D-3     | Decided        | A: submit anyway, severity "None"                    |
| DEC-06 | Staff authentication              | D-5     | Decided        | A: shared API key (upgrade path to B)                |
| DEC-07 | Dashboard stack                   | D-2     | Decided        | B: separate static site, React                       |
| DEC-08 | GPS unavailable                   | D-8     | Decided        | A: block submission                                  |
| DEC-09 | Training compute                  | D-9     | Decided        | A: Google Colab                                      |
| DEC-10 | Training data scope               | -       | Parked         | A or B, chosen after M4 comparison                   |
| DEC-11 | Backend hosting                   | D-1     | Open           | Provisionally D: test Render and Hugging Face Spaces |
| -      | DBSCAN eps and min_samples        | D-6     | Deferred       | Week 3, needs test coordinates                       |
| -      | Latency target                    | D-7     | Deferred       | After the Week 2 benchmark                           |
| -      | Demo city and local test set size | D-10    | Deferred       | Week 1 kickoff                                       |

---

## DEC-01: Scope freeze

**Context:** 4 weeks remain, and the spec marks several items as optional.

**Options proposed**
- A. Cut all five optional items (Leaflet map, MLflow, Hugging Face Hub, image-quality check, own-report history M-8). MVP only.
- B. Cut all except one, kept as a stretch goal after the full MVP works.
- C. Keep a different set.

**Chosen: A.** MVP only.

**Reason:** Lowest risk for a 4-week schedule. No optional item may delay or destabilize an MVP component.

**Consequences:** Dashboard is a list/table with no map. No MLflow (a structured log or spreadsheet is used for training runs). The app has no "my reports" screen. Revisit only after Milestone 4.

---

## DEC-02: Role assignment

**Context:** Six members map to six roles: M1 Mobile, M2 Backend, M3 Database, M4 Computer Vision, M5 Severity + DBSCAN, M6 Dashboard + Deployment. Roles are divided by tech stack; backup pairs are 1↔6, 2↔3, 4↔5.

**Chosen (partly)**
- The member with Flutter background is M1.
- The member with web development background is M6.
- The other four members learn what their tasks need.
- Name-to-role matching for M2–M5 and the leader's own role are still to be chosen.

**Reason:** Stack ownership gives each component a single owner, so contracts work and people work in parallel. Cross-training happens through code review and backup pairs.

**Open:** names for M2–M5; leader's role (options discussed: M2, M6, M5, or coordination only).

---

## DEC-03: API flow (spec D-4)

**Context:** When does the citizen see the AI result, and how does the backend avoid trusting predictions sent by the client?

**Options proposed**
- A. Single call: `POST /reports` runs inference, stores, clusters, and returns the result. Result is seen only after submit.
- B. Two steps with server-side cache: `POST /analyze` returns detections and an `analysis_id`; `POST /reports` submits using that ID and reuses the cached result.
- C. Two steps, stateless: `/analyze` is a preview; `/reports` re-uploads the image and re-runs inference.

**Chosen: B.**

**Reason:** The citizen can preview the result and retake the photo before anything is stored, with one inference per report.

**Consequences:** `/analyze` and `/reports` are both in the contract. The backend must keep analysis state (see DEC-04). More states to test than a single call.

---

## DEC-04: Analysis cache mechanism

**Context:** DEC-03 requires the backend to remember an analysis between the two steps.

**Options proposed**
- A. Database table `analyses` plus temporary image under a `pending/` prefix in storage.
- B. In-memory dictionary with expiry.
- C. In-memory with fallback: `/reports` also accepts the image and re-runs inference if the analysis is missing.

**Chosen: A.**

**Reason:** Survives restarts and host sleep on free tiers, and avoids partial or inconsistent reports.

**Consequences:** Table `analyses` (analysis_id, temp image path, detections jsonb, severity label and score, created_at). A cleanup script deletes `pending/` items and rows older than 24 hours. Extra work for M2 and M3.

---

## DEC-05: No-detection behavior (spec D-3)

**Context:** The detector can return zero detections: blurry or non-road photos, or damage the model missed.

**Options proposed**
- A. Allow "Submit anyway" or "Retake". The report has null category and severity "None", sorts last, and is labeled "no AI detection".
- B. Block: only "Retake" is offered; no report is created.
- C. Allow submission with a manually chosen category.

**Chosen: A.**

**Reason:** Real damage the model misses is not lost, and staff make the final judgment. Matches the spec default. Option C was rejected as extra UI and a mix of human and AI categories.

**Consequences:** `damage_category` is nullable. The dashboard sorts severity "None" last and shows a label. Staff may see junk submissions at the bottom of the list.

---

## DEC-06: Staff authentication (spec D-5)

**Context:** Staff endpoints (list, detail, status update, clusters) must be restricted. Citizens stay anonymous.

**Options proposed**
- A. One shared staff API key in an environment variable, sent in a request header.
- B. Supabase Auth with pre-created accounts and tokens.
- C. Own login endpoint with hardcoded accounts and signed tokens.

**Chosen: A.**

**Reason:** About an hour of work and no extra service, which fits a 4-week schedule.

**Consequences:** No per-user identity, so there is no record of who changed a status. The key is held in browser session memory and never committed. **Upgrade path:** move to option B only if time remains after the MVP is stable.

---

## DEC-07: Dashboard frontend stack (spec D-2)

**Context:** The dashboard needs a severity-sorted list, filters, detail view, duplicate groups, and status updates.

**Options proposed**
- A. Plain HTML, CSS, and JavaScript served by the backend.
- B. A framework (React or Vue) as a separate static site.
- C. Flutter Web.

**Chosen: B, with React.**

**Reason:** Cleaner structure for list, detail, and filter state; suits the web developer on the team.

**Consequences:** M2 configures CORS to allow only the dashboard origin. M6 owns a second deployment (static host, to be chosen in Week 1) and a build step. The staff API key is entered on a login screen and kept in session memory.

---

## DEC-08: GPS unavailable fallback (spec D-8)

**Context:** Location permission may be denied, device location services may be off, or no fix may be available.

**Options proposed**
- A. Block submission with a clear message and a retry/settings button.
- B. Manual pin on a map.
- C. Allow submission without location.

**Chosen: A.**

**Reason:** A report without a location is not actionable. Option B contradicts DEC-01 (map cut). Option C requires null handling everywhere and excludes reports from clustering.

**Consequences:** `location` stays non-null. The app tests three cases: granted, denied, services off.

---

## DEC-09: Training compute (spec D-9)

**Context:** M4 fine-tunes YOLOv8n on RDD2022.

**Options proposed**
- A. Google Colab free tier.
- B. Kaggle Notebooks.
- C. A local GPU.
- D. A mix of Colab and Kaggle.

**Chosen: A.**

**Reason:** Easiest setup for the team.

**Consequences:** Sessions can disconnect, so M4 saves checkpoints to Google Drive every epoch. The free GPU is not guaranteed, so runs must stay short enough to survive cutoffs. Every run is logged in the training-run template.

---

## DEC-10: Training data scope

**Context:** RDD2022 has several country subsets. Full-dataset training is slow on Colab free tier, and public test labels may be missing, so the team creates its own splits.

**Options proposed**
- A. One country subset, chosen for similarity to the demo area and enough potholes.
- B. Two or three subsets merged, capped at about 5,000 images, balanced by class.
- C. Full RDD2022.

**Status: leaning A.** One subset by default. Switch to B only if T4.1 shows too few pothole images in every single subset. Option C is not recommended.

**Decision rule:** M4 reports class and pothole counts per subset within 48 hours (task T4.1). The choice is made after that comparison. If potholes are too rare in every single subset, choose B.

---

## DEC-11: Backend hosting (spec D-1)

**Context:** The backend loads YOLOv8n with PyTorch at startup and runs inference within requests. Free-tier RAM, cold starts, and timeouts are unverified.

**Options proposed**
- A. Render free web service (spec default).
- B. Hugging Face Spaces (Docker).
- C. Render with an ONNX-exported model.
- D. Test A and B in the first days, then choose by evidence.

**Status: open.** The Week 1 plan provisionally follows option D: M2 and M6 deploy a hello-world backend with the model on both hosts and record RAM, cold start, and inference time in `docs/decisions/hosting-test.md`. Option C is the fallback if only Render is acceptable. The demo fallback is a recorded screen capture; no Docker Compose setup is built (scope control).

**To close:** add a superseding entry with the chosen host and the test results.

## DEC-12: Scope confirmations

**Chosen:** keep the two-step flow (DEC-03, DEC-04) and the React dashboard (DEC-07). Drop `GET /clusters` and the Docker Compose fallback.

**Reason:** 4 weeks remain. Kept items are already designed and owned. Dropped items duplicate what other parts of the MVP already cover.

**Consequences:** cluster information is returned in the list and detail responses only. `contract.md` has no `/clusters` endpoint.
---

## Deferred decisions

| Spec ID | Decision                                       | When                       | Input needed                                                                             |
| ------- | ---------------------------------------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| D-6     | DBSCAN eps and min_samples                     | Week 3                     | Test coordinates, demo area scale, GPS accuracy; `min_samples = 2` is the starting point |
| D-7     | Latency target                                 | After the Week 2 benchmark | Measured inference and end-to-end submission times on the deployment host                |
| D-10    | Demo city and size of the local photo test set | Week 1 kickoff             | Team agreement; default target of 30 local photos                                        |