# Prompt Template for Coding Agents

Use this template every time you give a task to an AI coding agent (Claude Code, Copilot, Cursor, etc.). Precise prompts prevent invented names, wrong formats, and changes in other members' code.

## 1. Rules for using it
- One task ID per prompt. Split anything larger.
- Always point the agent to `AGENTS.md` and the documents it must read. Never paste outdated copies of the contract or schema; reference the files.
- List the files the agent may change. Everything else is read-only.
- State acceptance criteria as checks you can verify, not as wishes.
- Review the diff yourself before committing. You are accountable for the code.
- If the agent proposes changing the contract, schema, or vocabulary, stop and follow section 11 of `CONTRIBUTING.md`.

## 2. Template (copy, fill, send)

# Task [ID]: [short title]

## Context
Component: [mobile | dashboard | api | db | detection | severity | clustering]
Owner: [member role]
Read first: AGENTS.md, [docs/api/contract.md], [docs/architecture/vocabulary.md], [docs/architecture/database-schema.md], [other files]
Existing code to build on: [paths, or "none, new file"]

## Task
[2-5 sentences describing exactly what to build or change.]

## Files you may create or change
- [path]
- [path]
Do not touch any other file.

## Interfaces (exact)
Inputs: [names, types, formats]
Outputs: [names, types, formats]
Errors: [which errors and what response]

## Constraints
- Follow the architecture rules in AGENTS.md.
- Use exact names and strings from vocabulary.md and the contract.
- No new dependencies. [Or: allowed dependency: X version Y]
- [Other constraints specific to this task]

## Acceptance criteria
- [ ] [Verifiable check 1]
- [ ] [Verifiable check 2]
- [ ] [Edge cases handled: list them]

## Tests
Write: [test file path and the cases to cover]
Run: [exact command]

## Out of scope
- [things the agent must not do]

## When done, report
- Files changed (list)
- Commands run and their results
- Assumptions you made
- Anything unclear that needs the owner's decision

## 3. Filled example (task T5.2, severity function)

# Task T5.2: severity() function with unit tests

## Context
Component: severity
Owner: M5
Read first: AGENTS.md, docs/architecture/vocabulary.md, ml/severity/README.md (rules)
Existing code to build on: ml/severity/rules.yaml (category weights and thresholds)

## Task
Implement a pure function that converts a list of detections and the image size into one severity label and a numeric score. Use the rules in rules.yaml: score = category_weight * area_fraction_factor * confidence per detection, aggregated as documented in the README. No I/O, no database, no network.

## Files you may create or change
- ml/severity/severity.py
- tests/unit/test_severity.py
Do not touch any other file.

## Interfaces (exact)
Inputs: detections: list of {class_name: str, confidence: float, bbox: [x_min, y_min, x_max, y_max] in pixels}; image_width: int; image_height: int
Outputs: {label: "Low" | "Medium" | "High" | "None", score: float}
Errors: raise ValueError for non-positive image size, confidence outside [0, 1], or a bbox outside the image.

## Constraints
- Thresholds and weights are read from rules.yaml, never hardcoded.
- Labels use exactly the strings in vocabulary.md.
- Empty detections return label "None" and score 0.0.
- Type hints on every function. Clear names, functions under 30 lines.
- No new dependencies beyond PyYAML.

## Acceptance criteria
- [ ] Empty list returns "None"
- [ ] Score exactly at each threshold maps to the higher label
- [ ] Multiple detections are aggregated as documented
- [ ] Invalid inputs raise ValueError
- [ ] All tests pass

## Tests
Write: tests/unit/test_severity.py covering zero detections, a single detection at each label, boundary values at each threshold, multiple detections, invalid inputs.
Run: pytest tests/unit/test_severity.py

## Out of scope
- Changing rules.yaml values
- Calling the function from the backend

## When done, report
- Files changed, commands run and results, assumptions, open questions



## 4. Quick checks before sending a prompt
- [ ] One task, one component
- [ ] Allowed files listed
- [ ] Exact input and output formats written out
- [ ] Acceptance criteria are checkable
- [ ] Tests and the command to run them are named
- [ ] Out-of-scope list present

## 5. Quick checks after the agent finishes
- [ ] Only the allowed files changed (`git status`, `git diff --stat`)
- [ ] Names match the contract and vocabulary exactly
- [ ] No hardcoded values, secrets, or invented fields
- [ ] Tests pass locally and cover the edge cases
- [ ] Nothing outside the MVP was added
- [ ] README updated if setup or behavior changed