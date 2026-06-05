# PLAN: v0.6.4 - Dependabot vulnerability zero-tolerance hotfix

**Status:** Aprovado
**Release ID:** v0.6.4
**Owner:** product-engineer
**Created:** 2026-06-05

## Strategy

1. Reserve the dependency hotfix task in `TASKS.md`.
2. Update dependency constraints:
   - `requirements.txt`: `poetry==2.3.4`, `pytest==9.0.3`.
   - `requirements.txt`: `pyarrow==23.0.1`, `duckdb==1.4.2`.
   - `pyproject.toml`: test dependency `pytest = "^9.0.3"` plus runtime
     dependencies `pyarrow = "^23.0.1"` and `duckdb = "^1.4.2"`.
   - `poetry.lock`: regenerate or update through Poetry so the lock reflects
     patched pytest, pyarrow, and DuckDB versions.
3. Validate:
   - Dependabot alert query before and after push.
   - `poetry check`.
   - Full pytest suite with repo cache disabled.
   - Package build/install smoke.
   - `pip-audit -r requirements.txt` reports no known vulnerabilities.
4. Run QA, code review, and security review on the implementation commit.
5. Push and publish stable `0.6.4` only after all reviewers approve.

## Risk Controls

- No production behavior changes are expected.
- No dependency downgrade is allowed.
- No advisory/security scan may be treated as informational for this release.
- Generated cache/artifact directories must stay out of the repo tree.
