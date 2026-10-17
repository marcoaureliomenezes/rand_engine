# Job 2 — Human API, method and builder reference

**Wave:** 2
**Waits on:** Job 1
**W:** `tests/test_docs.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/5_RECIPES.md`, `skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC1.4, AC2.1–AC2.3, AC3.1–AC3.3, AC4.3 | `tests/test_docs.py` | RED contracts derived from `METHOD_CATALOG`, live Spark validation and builder/factory classes; retain executable-documentation ownership in the current harness. |
| J2.T2 | jr | AC1.4, AC2.1–AC2.3, AC3.1–AC3.3, AC4.3 | `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/5_RECIPES.md`, `skills/rand-engine/SKILL.md` | Document the code-backed domains, Spark partitions, builders and factory inventory so J2.T1 becomes green. |

`docs/3_WRITING_FILES.md` is the returned-writer surface from Job 1;
`docs/reference.md` retains exactly its three `rand_engine.__all__` directives.
Examples use the existing docs harness, temporary output and no more than 10^4 rows.

