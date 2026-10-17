# Job 5 — Public contracts and guides

**Wave:** 3
**Waits on:** Job 1, Job 2, Job 3, Job 4
**W:** `tests/test_docs.py`, `rand_engine/main/data_generator.py`,
`rand_engine/main/spark_generator.py`, `rand_engine/file_handlers/writer.py`,
`rand_engine/file_handlers/_writer_batch.py`, `docs/1_DATA_GENERATOR.md`,
`docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`,
`docs/5_RECIPES.md`, `docs/explanation.md`, `docs/reference.md`, `mkdocs.yml`,
`llms.txt`, `skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC5.1–AC5.2 | `tests/test_docs.py` | RED executable-documentation and semantic-inventory tests derived from code authorities for born-before, Spark parity/seed boundary, SQLite builder and refusals, Arrow fallback, rendered routes and llms/skill consumers. |
| J5.T2 | jr | AC5.1–AC5.2 | `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/reference.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md` | Update public docstrings and human/agent guidance to the accepted implementation, with synthetic runnable examples under 10^4 rows and existing rendered destinations. |

`J5.T2` is fully specified by the final code and J5.T1 assertions; it may not edit
tests or invent a docs export/build pipeline. AC5.3 is closure evidence, not a
source-artifact task.
