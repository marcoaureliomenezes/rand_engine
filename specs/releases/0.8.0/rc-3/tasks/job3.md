# Job 3 — Onboarding and agent discovery

**Wave:** 3
**Waits on:** Job 2
**W:** `tests/test_docs.py`, `docs/getting-started.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `llms.txt`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC3.4–AC3.5, AC4.1–AC4.4 | `tests/test_docs.py`, `docs/getting-started.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `llms.txt` | Complete onboarding and agent discovery: each scaffold has command, filename, prerequisite and outcome; use cases route to runnable guides; agent links target rendered pages or direct cases; remove only the remaining green xfails. |

The existing case and CLI contracts remain the E2E evidence. This task does not add
an exporter, raw-Markdown expansion, workflow or additional docs build.

