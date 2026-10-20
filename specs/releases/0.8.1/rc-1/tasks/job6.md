# Job 6 — version 0.8.1 and its changelog (wave 5, waits on Jobs 4 and 5)

Last job. No test of the literal version (it would mirror `pyproject.toml`); the changelog is prose.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | jr | AC6.1 | `pyproject.toml`, `tests/integrations/test_public_api.py` | version `0.8.1`; `poetry version -s` prints it; update the literal `"0.8.0"` at `:552` (the built-wheel assert) under the operator's version ruling |
| J6.T2 | jr | AC6.2 | `CHANGELOG.md` | new `## [0.8.1]` dated with the closure-commit date (`tests/test_docs.py:884-887` requires a dated header and is not narrowed; the promote re-dates it if publication slips) with the Changed and Removed lines of AC6.2 and nothing under Fixed; the 0.8.0 section untouched |
