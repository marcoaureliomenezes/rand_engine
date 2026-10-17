---
slug: QUALITY
title: Quality Assurance
tldr: QA principles, test architecture and the gates every change passes.
summary: Principles change only with an accepted ADR; Test architecture and Gates state how rand-engine is verified — a light numbered pytest suite with executable docs and docstrings, a docstring lint in the verify line, CI-only stress and same-runner benchmarks, and the GitHub Actions matrix, security, docs and publish workflows.
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

- One pytest suite under `tests/`: numbered files `test_<n>_<area>.py` ordered by layer — 0 core methods, 1 validators, 2 `DataGenerator`, 3 Spark (including partition-independent keys) and advanced specs, 4 example specs and the `RandSpecs` builders, 5 file and SQLite batch/stream writers, 6 lossless Arrow-or-pandas `stream_dict` records, 7 templates, 8 PK/FK consistency, 9 the get-started CLI and its scaffolds — plus the public-import and wheel contract, benchmark-script contract and executable documentation contract (Markdown pages, the agent skill, README landing rules, public docstrings and their examples).
- CLI scaffolds execute in-process in a temporary directory, sharing the suite's Spark session; one runs as a plain-python subprocess.
- Specs under test live as fixtures in `tests/fixtures/f<n>_*.py`; `conftest.py` loads the Spark fixtures as a plugin.
- Spark tests start a local `SparkSession` and skip when PySpark is absent or on Windows with Python 3.12+.
- The default selector excludes `stress`; default tests generate at most 10^4 rows, while large-volume tests and benchmarks run in the CI benchmark job.
- Writer and documentation tests write through pytest temporary paths.
- Local runs keep caches out of the repo: `PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider`.

## Gates

- Push to any branch but `master`/`development` with no open PR: the pytest matrix (Ubuntu, Windows, macOS × Python 3.10–3.13) with coverage reported.
- PR to `development`: source must not be `master`; the matrix with `--cov-fail-under=60`; Bandit, Semgrep, Safety and Trivy run advisory (they never fail the job); CodeQL analyzes.
- PR to `master`: source must be `development`; the matrix with coverage.
- PR to `master` or `development`: the benchmark workflow runs stress tests and a same-runner A/B speed comparison, publishes its summary/comment/artifact and fails a comparable row above the base ratio, a distribution method above its sibling or a modifier above its overhead limit.
- Merge to `development`: tests (Ubuntu, Python 3.10–3.13), build with the next `rcN` version, `twine check`, a wheel install smoke, the RC tag, PyPI publish.
- Merge to `master`: tests (Ubuntu, Python 3.10–3.13), build of the `pyproject.toml` version (no RC suffix), the tag, PyPI publish, a GitHub release.
- The repo `verify:` line (the local job gate) runs `ruff check --select D` (numpy convention) on the six public-surface modules before the suite. No type checker is configured, and CI runs no lint.
- Inside every pytest run: an `inspect` check that each public callable of `DataGenerator`, `SparkGenerator`, `RandSpecs` and the writer objects carries a numpydoc docstring (it covers the `_`-prefixed writer modules ruff skips), and the doctest examples of those modules. A full suite run takes 45–93 s on each Ubuntu and macOS leg of Tests on Push run 38973485937.
- Docs workflow, on PRs to `development` and `master` and pushes to `feature/**` and `master`: the strict Zensical build, aborting on a broken internal link (1.13 s in Docs run 38973485919); on `master` it deploys the site to GitHub Pages.

<!-- dadaia:fixed slop-tests -->
### Slop — tests (fixed)
- A test follows the root `AGENTS.md` map §1 test basics; an own module is tested through its interface.
- A test name states current behavior; a tombstone is a test of an absence (removal: root map §1).
- Detection: `dd-code-review` SLOP.md S3.
<!-- /dadaia:fixed slop-tests -->
