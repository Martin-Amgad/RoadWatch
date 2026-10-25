# RoadWatch — AI-Powered Road Damage Reporting

RoadWatch is a student team project that helps citizens report road damage and helps municipal staff review, prioritize, and track reports.

A citizen submits a road-damage photo with its location and an optional description. The system uses a YOLOv8n-based detector to suggest a damage category, calculates a **preliminary** severity label, and stores the report. A staff dashboard lists reports by severity, surfaces geographically nearby reports as **potential duplicates**, and lets authorized staff update report status.

> **Important:** AI severity is only a preliminary, image-based indicator—not a professional engineering assessment. Geographic proximity does not prove that two reports describe the same damage. Staff make the final decisions. The system must not automatically delete or merge original reports.

## Project status

This repository currently contains a **starter structure and documentation placeholders**, not a working application. Components will be implemented incrementally during the six-week project.

## Main interfaces

- **Citizen mobile app (Flutter):** capture/select a photo, review the AI result, attach GPS coordinates and an optional description, submit a report, and view submission confirmation/status.
- **Staff web dashboard:** view reports in severity order, filter by category/status, inspect report details and potential duplicate groups, and update status.

## Planned technology

| Component | Planned technology |
|---|---|
| Mobile app | Flutter |
| API/backend | Python + FastAPI |
| Road-damage detection | YOLOv8n (Ultralytics), fine-tuned on a selected public dataset |
| Preliminary severity | Documented rule-based score |
| Potential duplicate grouping | DBSCAN over geographic coordinates using the haversine metric |
| Database | PostgreSQL + PostGIS (planned through Supabase) |
| Image storage | Object storage |
| Dashboard | Web framework to be selected by the team |

The dashboard framework, hosting, authentication approach, and some API details should be confirmed by the team before implementation. Treat this table as the current plan, not proof that the services have been configured.

## MVP scope

1. Submit a photo from the mobile app.
2. Validate the image and run road-damage inference.
3. Display the predicted category, confidence, and preliminary severity; handle cases where no supported damage is detected.
4. Attach GPS coordinates and an optional description.
5. Persist the image and report record and return a report ID.
6. List reports in the dashboard, highest severity first; filter by category and status.
7. Show report details and potential duplicate groups without deleting or merging originals.
8. Let authorized staff move a report through `Submitted`, `Under Review`, and `Resolved`.
9. Add unit/integration tests and document model evaluation, limitations, and setup.

Optional features—such as an interactive map—should come after the MVP is stable.

## Repository layout

```text
roadwatch/
├── apps/
│   ├── mobile/                 # Flutter citizen app
│   └── dashboard/              # Municipal staff web dashboard
├── services/
│   └── api/                    # FastAPI routes, schemas, services and config
├── ml/
│   ├── damage_detection/       # Dataset notes, training and inference code
│   ├── severity/               # Rule-based severity estimation
│   └── clustering/             # Geographic DBSCAN grouping
├── data/
│   └── README.md               # Dataset instructions; do not commit datasets
├── docs/
│   ├── architecture/           # Architecture and workflow notes
│   ├── api/                    # API contract and examples
│   └── decisions/              # Decisions and assumptions
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/                    # Reproducible helper scripts
├── infra/                      # Deployment/configuration templates
├── .github/workflows/          # CI workflows (to be added)
├── .gitignore
└── README.md
```

Each component directory contains a short `README.md` explaining its intended responsibility and what should eventually live there.

## Report lifecycle

`Submitted` → `Under Review` → `Resolved`

## Responsible data and AI practices

- Use only fabricated or approved public examples in demos and documentation.
- Do not commit credentials, API keys, private user data, or large datasets/model weights.
- Check the dataset license and document its source and version before use.
- Blur faces and license plates in locally collected demo/documentation photos.
- Validate uploaded file types, sizes, and coordinate ranges.
- Keep model outputs labeled as preliminary and preserve staff oversight.
- Treat DBSCAN clusters as suggestions for review, not definitive duplicate detection.

## Getting started

This starter repository does not yet contain runnable application code.

1. Clone the repository.
2. Read the component READMEs and the project specification.
3. Agree on the API contract, report schema, shared labels, and dashboard stack.
4. Implement one small end-to-end flow using stub data before integrating the trained model.
5. Add setup instructions and tests as each component becomes runnable.

## Team workflow

- Work on focused branches and open pull requests.
- Ask at least one teammate to review each pull request.
- Keep API contracts and shared labels documented and version-controlled.
- Record dataset versions, training configuration, and evaluation results.
- Update this README when the project structure or implementation status changes.

## License

No license has been selected yet. Add a license only after the team agrees on how the project may be reused.
