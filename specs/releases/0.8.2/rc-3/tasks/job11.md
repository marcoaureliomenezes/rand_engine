# Job 11 — changelog (wave 6)

Waits on the feature-doc bug lanes (it states what shipped). Runs beside Job 10 (disjoint `W:`). Conditional: with no bug lane, the task is **cancelled** with that reason; the eval ships nothing in the wheel (the rc-1 FR8 precedent).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J11.T1 | jr | AC18.3 | `CHANGELOG.md` | text only: the dated-header test exists (`tests/test_docs.py`). Under the existing `## [0.8.2]` header, add one line per shipped feature-doc fix, from the resolved bug records (`bugs.py status`), under `### Fixed` or `### Changed` as the fix is. Existing lines stay |

Done when: `verify:`; `tests/test_docs.py` passes.
