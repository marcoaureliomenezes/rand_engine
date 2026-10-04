# rand-engine - Repo Context

> This file is loaded by Claude Code, OpenCode, and Codex when working in this repo.
> It complements the workspace-root `AGENTS.md` with repo-domain knowledge.
> Edit this file directly. It is not lib-originated and will not be overwritten by `dadaia public install`.

## Repo Purpose

`rand-engine` is a Python library for fast synthetic data generation. It serves
engineers, data teams, QA engineers, and demo builders who need deterministic
Pandas dataframes, Spark dataframes, files, streams, and relation-aware test data
without hand-building fixtures.

## Spec Structure

Specs live under `specs/` (dadaia canon; tree and status tokens: `specs/AGENTS.md`).
Ground every session with `dd-spec-navigator`, in this order:

1. `specs/constitution.md`
2. `specs/memory/ARCHITECTURE.md` (its `## Tech Stack` included) and `specs/memory/QUALITY.md`
3. `specs/memory/product/index.md`, then the relevant atoms under `specs/memory/product/<area>/`
4. The live release: `specs/releases/<M.m.p>/_RELEASE.json` (`phase`) and the highest `rc-<N>/` trio — `SPEC.md`, `PLAN.md`, `TASKS.md`

Production edits need the live release in `IMPLEMENTATION` and its trio at
`**Status:** Approved`; a bug fix follows the workspace bug flow instead.

## Repo-Specific Stop Conditions

- Relations are stateless `pk`/`fk` columns computed per row; stop before adding
  any persisted key state or database to generation.
- Stop before changing public API names, RandSpec method grammar, writer
  semantics, release/version policy, or the supported Python/Spark matrix without
  an approved SPEC.
- Stop if a command would create repo-local caches such as `.venv/`,
  `.pytest_cache/`, `.coverage`, `coverage/`, `test-results/`, or
  `playwright-report/`.

## Key Paths

- `rand_engine/main/data_generator.py` - Pandas generation composition root.
- `rand_engine/main/spark_generator.py` - Spark generation facade.
- `rand_engine/core/` - NumPy, Python, and Spark generation primitives.
- `rand_engine/validators/` - RandSpec grammar validation.
- `rand_engine/file_handlers/` - batch and stream writers.
- `rand_engine/examples/` and `rand_engine/templates/` - built-in specs/templates.
- `tests/` - pytest suite; run with caches disabled or redirected outside the repo.
- `specs/` - dadaia-workspace SDD truth.

## Key Commands

```bash
# Install dependencies
poetry install --with test --no-interaction

# Run tests without pytest cache
PYTHONDONTWRITEBYTECODE=1 poetry run pytest tests/ -q -p no:cacheprovider

# Coverage evidence
COVERAGE_FILE=$WORKSPACE_ROOT/.dadaia/tmp/rand-engine.coverage \
  PYTHONDONTWRITEBYTECODE=1 \
  poetry run pytest tests/ -q -p no:cacheprovider --cov=rand_engine --cov-report=term-missing

# Build package
poetry build

# Validate specs from workspace root
.dadaia/.venv/bin/dadaia doctor --context rand-engine
```
