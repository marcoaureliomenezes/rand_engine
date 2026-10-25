---
slug: QUALITY
title: Quality Assurance
tldr: QA principles, test architecture and the gates every change passes.
summary: Principles change only with an accepted ADR; Test architecture and Gates state how rand-engine is verified — a light numbered pytest suite with executable docs and docstrings, a docstring lint in the verify line, CI-only stress and same-runner benchmarks, a non-gating cross-library observation, and the GitHub Actions matrix, security, isolated docs and publish workflows.
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

- One pytest suite under `tests/`: numbered files `test_<n>_<area>.py` ordered by layer — 0 core methods, 1 validators, 2 `DataGenerator`, 3 Spark (including partition-independent keys) and advanced specs, 4 example specs and the `RandSpecs` builders, 5 file and SQLite batch/stream writers, 6 normalized pandas `stream_dict` record contracts, 7 templates, 8 PK/FK consistency, 9 the get-started CLI and its scaffolds — plus the public-import and wheel contract, internal benchmark and observational-comparison contracts, and executable documentation contract (Markdown pages, the agent skill, README landing rules, public docstrings and their examples).
- The five runnable CLI scaffolds execute in-process in a temporary directory, sharing the suite's Spark session; one runs as a plain-python subprocess. The sixth Agent resource is checked as Markdown bytes and project-context content and is never executed as Python.
- Specs under test live as fixtures in `tests/fixtures/f<n>_*.py`; `conftest.py` loads the Spark fixtures as a plugin.
- Spark tests start a local `SparkSession`, with the Java 17 options Spark's Arrow conversion needs, and skip when PySpark is absent or on Windows with Python 3.12 or later, so the Windows legs run them only on Python 3.11.
- The default selector excludes `stress`; default tests generate at most 10^4 rows, while large-volume tests and benchmarks run in the CI benchmark job.
- The observational comparison tests use injected factories and clocks, so ordinary collection needs no comparator package and asserts the two workload shapes, alternating samples, complete output validation, provenance and artifact semantics without a timing target. A separate non-required workflow installs its pinned environment and the public non-editable wheel, runs the real Python and Spark contracts on canonical comparison-path pushes or manual dispatch, and always retains its status and evidence; its measurements never enter the internal regression gate.
- Writer and documentation tests write through pytest temporary paths.
- Documentation contracts run the preparation script in a subprocess and check: isolated input, raw resources and starter files, a byte copy of the canonical skill, untouched tracked sources, ordinary PyPI installs and principal-branch routes. Preparation needs no TOML parser (it runs on the standard library alone), and a workflow contract names `master` as the only Pages-deploying branch.
- Local runs keep caches out of the repo: `PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider`.

## Gates

- The test matrix is 12 legs, Ubuntu, Windows and macOS × Python 3.11–3.14. Each leg installs the package by a fresh `pip install ".[faker]"` resolve of its bounds, never from `poetry.lock`, and prints the resolved versions: the Ubuntu Python 3.11 floor leg pins `pandas==2.2.0 numpy==1.26.0 pyarrow==19.0.0 faker==28.4.1` and PySpark 3.5; the other Python 3.11 legs take the latest stack with PySpark 3.5, and the Python 3.12–3.14 legs the latest stack with PySpark 4.x. Poetry is installed by `pipx` for the wheel fixture only.
- Push to any branch but `master`/`development` with no open PR: the matrix with coverage reported.
- PR to `development`: source must not be `master`; the matrix with `--cov-fail-under=60`; Bandit, Semgrep, Safety and Trivy run advisory (they never fail the job); CodeQL analyzes.
- PR to `master`: source must be `development`; the matrix with coverage.
- PR to `master` or `development`: the benchmark workflow runs stress tests and a same-runner A/B speed comparison against the latest closed-release tag, publishes its summary/comment/artifact and fails a comparable row above the base ratio, a distribution method above its sibling or a modifier above its overhead limit.
- Merge to `master`: tests (Ubuntu, Python 3.11–3.14, the same fresh-resolve legs), build of the `pyproject.toml` version (a version with an rc suffix fails the workflow), PyPI publish once the operator approves the `production` environment, then the tag, then a GitHub release. No workflow publishes, tags or releases a release candidate.
- The repo `verify:` line (the local job gate) runs `ruff check --select D` (numpy convention) on the six public-surface modules before the suite. No type checker is configured, and CI runs no lint.
- Inside every pytest run: an `inspect` check that each public callable of `DataGenerator`, `SparkGenerator`, `RandSpecs` and the writer objects carries a numpydoc docstring (it covers the `_`-prefixed writer modules ruff skips), and the doctest examples of those modules. A full suite run takes 45–93 s on each Ubuntu and macOS leg of Tests on Push run 38973485937.
- Docs workflow, on PRs to `development` and `master` and pushes to `feature/**` and `master`: Python 3.12 prepares an isolated tree and runs the strict Zensical build, aborting on a broken internal link. Only a push to `master` uploads the site and deploys it through the bounded `pages-public-site` queue (`queue: max`, no in-progress cancellation); workflow cancellation stays on for every other ref.

<!-- dadaia:fixed slop-tests -->
### Slop — tests (fixed)
- A test follows the root `AGENTS.md` map §1 test basics; an own module is tested through its interface.
- A test name states current behavior; a tombstone is a test of an absence (removal: root map §1).
- Detection: `dd-code-review` SLOP.md S3.
<!-- /dadaia:fixed slop-tests -->
