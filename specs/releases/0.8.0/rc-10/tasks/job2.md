# Job 2 — Close the Faker preview-install guidance defect

**Wave:** 1
**Waits on:** —
**W:** `tests/test_docs.py`, `rand_engine/cases/faker.py.txt`,
`docs/tutorials/faker.md`, `specs/bugs/BUGS.jsonl`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1 | `tests/test_docs.py` | RED first for `preview-faker-install-guidance`. Harden the existing preview-preparation contract so it scans every copied public case resource as well as prepared Markdown, llms and skill text. It must reject every exposed own-project ordinary installation and accept only the one reviewed preview SHA route; parent Faker resources make it fail with match count two before the source correction. Preserve the existing source-immutability, raw-resource set, Agent and preview assertions. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_docs.py` and record the focused RED result. |
| J2.T2 | jr | AC2.2–AC2.3 | `rand_engine/cases/faker.py.txt`, `docs/tutorials/faker.md` | Replace only the two canonical Faker-case installation comments with concise directions to the existing live Getting started authority. Correct the tutorial statement that the included file carries its install command, routing installation through its generated preview command/Getting started authority. Do not change runnable example behavior, CLI case selection, documentation preparation or include/package bytes; the tutorial remains a verbatim include of the canonical resource. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_docs.py tests/test_9_cli.py` and show J2.T1 GREEN. |
| J2.T3 | sr | AC2.4 | `specs/bugs/BUGS.jsonl` | After J2.T1 and J2.T2 are merged into this job tree and reviewed, resolve `preview-faker-install-guidance` only through `bugs.py resolve`, using the actual 40-character correction SHA and the RED/GREEN evidence. Do not alter immutable report fields or archive the release record. Run `bugs.py check --specs <job-tree>/specs`. |

`preview-faker-install-guidance` is a confirmed MEDIUM bug caused by `J6.T8`.
Its required REBUILD is confined to the comments/guidance and their existing
oracle; it does not authorize a runtime rewrite. J2.T3 is a canonical ledger
transition, not evidence that public deployment has already been observed.
