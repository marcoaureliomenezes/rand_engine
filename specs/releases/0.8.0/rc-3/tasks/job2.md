# Job 2 — Human API, method and builder reference

**Wave:** 2
**Waits on:** Job 1
**W:** `tests/test_docs.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/5_RECIPES.md`, `docs/reference.md`, `mkdocs.yml`, `skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC1.1–AC1.5, AC2.1–AC2.4, AC3.1–AC3.3, AC4.3 | `tests/test_docs.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/5_RECIPES.md`, `docs/reference.md`, `mkdocs.yml`, `skills/rand-engine/SKILL.md` | Implement the RED semantic contracts: add returned-writer/error/builder destinations through existing pages and navigation; document code-backed method domains, Spark partitions, writer boundaries, builders and factories; remove only the xfails made green. |

`docs/3_WRITING_FILES.md` is the returned-writer surface. `docs/reference.md`
retains exactly its three `rand_engine.__all__` directives. Examples use the
existing docs harness, temporary output and no more than 10^4 rows.

