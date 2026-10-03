---
slug: QUALITY
title: Quality Assurance
tldr: QA principles, test architecture and the gates every change passes.
summary: Principles change only with an accepted ADR; Test architecture and Gates state how rand-engine is verified — one numbered pytest suite and the GitHub Actions matrix, security and publish workflows.
tags:
  - quality-assurance
  - testing
  - anti-slop
---

## Principles

- TDD: every new behaviour is born with a test that fails first; a bug fix reproduces the
  defect in a test before the fix.
- Reviews judge the artifact by its SPEC; an absent history is no ground for rejection.

## Test architecture

- One pytest suite under `tests/`: numbered files `test_<n>_<area>.py` ordered by layer — 0 core methods, 1 validators, 2 `DataGenerator`, 3 Spark and advanced specs, 4 example specs, 5 batch and stream writers, 6 `stream_dict`, 7 templates, 8 PK/FK consistency — plus `tests/integrations/` (SQLite, DuckDB, checkpoint cleanup, public API).
- Specs under test live as fixtures in `tests/fixtures/f<n>_*.py`; `conftest.py` loads the Spark fixtures as a plugin.
- Spark tests start a local `SparkSession` and skip when PySpark is absent or on Windows with Python 3.12+.
- No marker separates sizes; every test runs in one selection.
- Writer tests write files under the git-ignored `test_outputs/` at the repo root.
- Local runs keep caches out of the repo: `PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider`.

## Gates

- Push to any branch but `master`/`development` with no open PR: the pytest matrix (Ubuntu, Windows, macOS × Python 3.10-3.12) with coverage reported.
- PR to `development`: source must not be `master`; the matrix with `--cov-fail-under=60`; Bandit, Semgrep, Safety and Trivy run advisory (they never fail the job); CodeQL analyzes.
- PR to `master`: source must be `development`; the matrix with coverage.
- Merge to `development`: tests (Ubuntu, Python 3.10-3.12), build with the next `rcN` version, `twine check`, a wheel install smoke, the RC tag, PyPI publish.
- Merge to `master`: tests, build of the `pyproject.toml` version (no RC suffix), the tag, PyPI publish, a GitHub release.
- No lint or type checker is configured.

<!-- dadaia:fixed slop-tests -->
### Slop — tests (fixed)
- A test is born with `Intent:`, fails for a real regression and asserts a value that comes from outside the code under test.
- A mock exists only at the system boundary (network, clock, randomness); an own module is tested through its interface.
- A test name states current behavior; a tombstone (a test of an absence) and an expired SCAFFOLD die at closure.
- Pruning is a `dd-code-reviewer` verdict executed by `dd-software-engineer`; a deletion cites its criterion and its replacement `file:line`.
- Detection: `dd-code-review` SLOP.md S3.
<!-- /dadaia:fixed slop-tests -->
