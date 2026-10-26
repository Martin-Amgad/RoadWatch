# Contributing to RoadWatch

How the team works with Git, pull requests, and code. Read `AGENTS.md` first for the architecture rules.

## 1. Workflow overview
1. Pick a task from the board. Every task has an ID (e.g., `T2.3`).
2. Create a branch from the latest `main`.
3. Commit small, focused changes.
4. Open a pull request (PR).
5. One other member reviews and approves.
6. The author squash-merges into `main` and deletes the branch.

Nobody pushes directly to `main`.

## 2. Branches
Format: `<type>/<task-id>-<short-name>`

| Type      | Use                           |
| --------- | ----------------------------- |
| `feature` | New functionality             |
| `fix`     | Bug fix                       |
| `docs`    | Documentation only            |
| `chore`   | Tooling, config, dependencies |

Examples: `feature/T2.3-stub-endpoints`, `docs/L3-vocabulary`, `fix/T1.2-permission-crash`.

Rules:
- Lowercase, hyphens only, no spaces.
- One branch per task. Keep branches short-lived (target: merged within 2 days).
- Pull `main` into your branch at least daily to avoid large conflicts.

## 3. Commits
Format: `<type>(<scope>): <summary in imperative mood>`

Scopes: `mobile`, `dashboard`, `api`, `db`, `detection`, `severity`, `clustering`, `docs`, `infra`.

Examples:
- `feat(api): add validation for image size and type`
- `fix(mobile): handle denied location permission`
- `docs(decisions): add DEC-11 hosting test results`
- `test(severity): cover zero-detection case`

Rules:
- Summary under 72 characters, no trailing period.
- One logical change per commit.
- Never commit secrets, `.env` files, datasets, or model weights.

## 4. Pull requests
Title: `[T2.3] Stub endpoints with validation`

Every PR description contains:
- **What changed** (2-5 lines)
- **Task ID** and link to the issue
- **How it was tested** (commands run, devices used, screenshots for UI)
- **Contract, schema, or vocabulary changes** (yes/no; if yes, the doc is updated in this PR)
- **Open questions** (if any)

Rules:
- Keep PRs small (target under 400 changed lines). Split big work.
- Reviewer responds within 24 hours. Author responds to comments within 24 hours.
- The author never approves their own PR.
- Resolve all comments before merging.
- If a PR touches another member's component, that member must be the reviewer.

## 5. Review checklist
The reviewer confirms:
- [ ] Meets the task's "Done when" condition
- [ ] Uses exact names and strings from `docs/architecture/vocabulary.md` and the API contract
- [ ] Follows the architecture rules in `AGENTS.md`
- [ ] Names are clear, functions are small, no dead or commented-out code
- [ ] Tests added or updated and passing
- [ ] Inputs validated; errors handled with a clear response
- [ ] No secrets, hardcoded URLs, or magic numbers
- [ ] Component README updated if behavior, setup, or interfaces changed

## 6. Definition of Done
A task is done only when:
1. It is implemented and meets its acceptance criteria.
2. Tests are written and pass.
3. Another member has reviewed and approved the PR.
4. The component README and any affected docs are updated.
5. It is merged to `main`.
6. The issue is moved to Done.

## 7. Clean code conventions
**Naming**
- Names describe purpose: `calculate_severity_score`, not `calc` or `process2`.
- Functions are verbs, classes and types are nouns, booleans read as questions (`is_valid_image`, `has_detections`).
- No abbreviations except common ones (`id`, `url`, `gps`).
- Constants are named and upper-case (`MAX_IMAGE_SIZE_BYTES`), never bare numbers.

**Structure**
- One responsibility per function. If you need "and" to describe it, split it.
- Prefer functions under about 30 lines.
- Pure logic (severity, clustering) has no I/O so it is easy to test.
- Remove unused code instead of commenting it out.

**Language style**
| Component        | Style                                                                                 |
| ---------------- | ------------------------------------------------------------------------------------- |
| Python           | PEP 8, type hints, snake_case; format with `black`, lint with `ruff`                  |
| Dart             | `dart format`, `flutter analyze` clean                                                |
| JavaScript/React | ESLint and Prettier; components in PascalCase, functions in camelCase                 |
| SQL              | snake_case tables and columns; migrations are numbered and never edited after merging |

**JSON and API fields** use snake_case exactly as written in the contract.

## 8. Testing
- Python: `pytest`. Unit tests in `tests/unit`, integration tests in `tests/integration`.
- Tests use fixed inputs and assert specific outputs, including boundary and empty cases.
- Mobile and dashboard: follow the manual checklists in the component README until automated tests exist.
- Run tests before opening a PR. Never merge failing tests.

## 9. Configuration and secrets
- All secrets and URLs live in environment variables.
- Each component keeps an `.env.example` listing the variable names (never values).
- If a secret is committed by mistake, tell the leader immediately; the secret must be rotated, since deleting the commit is not enough.

## 10. Dependencies
- Ask the component owner before adding a dependency.
- Pin exact versions (`requirements.txt`, `pubspec.lock`, `package-lock.json`).

## 11. Contract, schema, and vocabulary changes
These are shared agreements. A new endpoint, field, table, dependency, or screen also counts as a change. After Day 3 sign-off:
1. Open an issue labeled `contract-change` describing the change and why.
2. Get approval from the leader and the affected owners.
3. Update the document and the code in the same PR.
4. Record significant changes in `docs/decisions/decisions.md`.

## 12. Communication
- Daily 15-minute standup: done, next, blocked.
- Blocked for more than 2 hours: post in the team chat right away.
- Questions about a component go to its owner (see the repository map in `AGENTS.md`).
- Decisions are written in the decision log, not only in chat.

## 13. Issue labels
`mobile`, `dashboard`, `api`, `db`, `ml`, `severity`, `clustering`, `infra`, `docs`, `contract-change`, `blocked`, `bug`, `parked`.

## 14. Scope control
- `parked` issues are not worked on until Milestone 4 is met.
- Any PR adding something not in a task or the contract is rejected by the reviewer.
- At the end of Weeks 2 and 3 the leader runs a scope check. If a milestone is more than 2 days late, cut in this order:
  1. Docker Compose fallback
  2. `GET /clusters` endpoint (cluster info stays in list and detail responses)
  3. Pagination and filters beyond category and status
  4. Local photo set from 30 to 15
  5. Dashboard detail polish (list plus status update only)
  6. Second training iteration