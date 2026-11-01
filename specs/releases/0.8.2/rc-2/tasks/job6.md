# Job 6 — changelog (wave 5)

Waits on Job 5 so the CHANGELOG states what shipped. The CHANGELOG is a task, not the reconcile: the reconcile's commit shape carries `specs/memory/*`, `README.md` and `docs/*.md` (`dd-gitflow-default` §3a, row 9), and rc-1 did the same in its Job 8. R7: the header is re-dated to the clock date when written; the date is corrected at ship if the publish date differs.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | jr | AC10.1 | `CHANGELOG.md` | text only: the dated-header test exists (`tests/test_docs.py`, `_changelog`). Under the existing `## [0.8.2]` header (`:10`), re-dated to the clock date, rc-2 adds its entries to the groups. **Fixed**: `spark-pool-types-fail-or-corrupt` (its lane writes no CHANGELOG line). **Changed**: the measured public texts (speed adjectives replaced by measured facts, the README opening); `llms.txt` shipped in the wheel from `rand_engine/llms.txt`; the keywords and classifiers; the Spark pool and error-class statements of the docs. **Added**: the `llms.txt` and `Agent skill` Project-URLs; `context7.json`; the page descriptions. Existing rc-1 lines stay |

Done when: `verify:`; `tests/test_docs.py` passes.
