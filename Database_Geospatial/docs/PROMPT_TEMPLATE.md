# Prompt template for RoadWatch development tasks

**Role:** You are implementing RoadWatch, an AI-powered road damage reporting MVP.

**Component owner:** [M1/M2/M3/M4/M5/M6]

**Current task:** [describe narrowly]

**Inputs and contracts:** [file paths or signed OpenAPI/schema version]

**Scope boundaries:** Do not change code outside the component without its owner's approval. Do not add optional map view, report history, complex RBAC, automatic deletion/merging of duplicate reports, or other parked features.

**Acceptance criteria:** [explicit test cases and expected behavior]

**Security:** Use server-side credentials only, parameterized SQL, private image storage, validate GPS bounds, keep all reports even when clustered.

**Output required:** Exact changed files, tests run, any pending decisions, and compatibility notes for the module owner.
