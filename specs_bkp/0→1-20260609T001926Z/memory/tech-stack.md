---
slug: tech-stack
title: rand-engine tech stack
category: core
tldr: 'Poetry-managed Python package with NumPy, Pandas, Arrow/FastParquet/FastAvro, DuckDB, pytest/PySpark, and GitHub Actions publishing.'
summary: 'Current package, dependency, test, CI, and release truth for rand-engine based on pyproject, workflows, PyPI/GitHub audit, and QA evidence.'
tags:
- python
- poetry
- pypi
- ci
- qa
agent_tier: self-pull
token_estimate: 510
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

# Tech Stack: rand-engine

## Linguagens

| Component | Current truth |
|---|---|
| Package name | `rand-engine` |
| Source package | `rand_engine` |
| Current local/stable version | `0.6.3` |
| Latest prerelease observed | `0.6.4rc1` |
| README advertised version | `0.7.0` drift; not approved as stable truth |
| Python requirement | `^3.10` in `pyproject.toml` |
| Build backend | `poetry.core.masonry.api` |
| Dependency source of truth | `pyproject.toml` + `poetry.lock`; `requirements.txt` is drift-prone unless generated |

Runtime dependencies in `pyproject.toml`: `numpy`, `pandas`, `fastavro`,
`fastparquet`, `pyarrow`, and `duckdb`. DuckDB is currently required metadata,
not optional.

Test dependencies: `pytest`, `pytest-cov`, `faker`, `pyspark`, and `setuptools`
for PySpark/Python 3.12+ compatibility.

## Comandos canônicos

Use project tooling with caches disabled or redirected outside the repo.

```bash
poetry install --with test --no-interaction

PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider

COVERAGE_FILE=$WORKSPACE_ROOT/.dadaia/tmp/rand-engine.coverage \
  PYTHONDONTWRITEBYTECODE=1 \
  poetry run pytest tests/ -q -p no:cacheprovider --cov=rand_engine --cov-report=term-missing

poetry check
poetry build
twine check dist/*
```

## Estado runtime

The QA audit ran a full isolated suite on 2026-06-05:

- `494 passed`.
- Coverage: `85.98%`.
- Lowest coverage areas include `utils/update.py`, validators, advanced examples,
  base DB handler, and template contracts.
- Current CI floor is inconsistent: one PR workflow enforces 60%, while the
  previous placeholder constitution said 80%. The restart release must choose
  an approved policy before implementation resumes.

## Runtimes e ferramentas

GitHub Actions currently include multi-OS/multi-Python testing, coverage, package
build/install checks, security scans, CodeQL/SAST/dependency jobs, development
RC publishing, and production PyPI publishing via Trusted Publishing/OIDC.

Known release governance issues:

- Security jobs are advisory in some workflows through `continue-on-error` or
  `|| true`.
- PR-to-master coverage is measured but not consistently fail-under.
- No lint/type tool is configured in `pyproject.toml`.
- PyPI classifiers advertise Python 3.13/3.14 while CI evidence covers 3.10-3.12.
- No canonical license file was found even though docs mention MIT.
- GitHub/PyPI stable is `0.6.3`; prerelease is `0.6.4rc1`; README badge says
  `0.7.0`.

## Restrições e proibições

- Whether supported Python is 3.10-3.12 or includes 3.13/3.14.
- Whether to expose runtime `rand_engine.__version__`.
- Whether security scans block merges/releases.
- Coverage threshold for restart work.
- Whether `requirements.txt` remains hand-maintained, generated, or removed.
- Whether RC tags must point at source commits whose `pyproject.toml` already
  contains the RC version.
