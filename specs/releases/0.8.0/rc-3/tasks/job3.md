# Job 3 — Onboarding and agent discovery

**Wave:** 3
**Waits on:** Job 2
**W:** `tests/test_docs.py`, `docs/getting-started.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `llms.txt`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | sr | AC3.4–AC3.5, AC4.1–AC4.4 | `tests/test_docs.py` | RED contracts for five scaffold commands/files/prerequisites/outcomes, use-case routing and useful agent destinations, derived from `CASES` and package resources. |
| J3.T2 | jr | AC3.4–AC3.5, AC4.1–AC4.4 | `docs/getting-started.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `llms.txt` | Complete onboarding and agent discovery so J3.T1 becomes green: each scaffold has command, filename, prerequisite and outcome; use cases route to runnable guides; agent links target rendered pages or direct cases. |

The existing case and CLI contracts remain the E2E evidence. This task does not add
an exporter, raw-Markdown expansion, workflow or additional docs build.
