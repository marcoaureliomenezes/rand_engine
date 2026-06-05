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

Specs live under `specs/`. Load them in this order before making any change:

1. `specs/constitution.md`
2. `specs/memory/tech-stack.md`
3. `specs/memory/architecture.md`
4. `specs/memory/product/index.md`
5. The relevant product memory atoms under `specs/memory/product/`
6. `specs/releases/ACTIVE.md`
7. `specs/releases/<active-release>/SPEC.md`
8. `specs/releases/<active-release>/PLAN.md`
9. `specs/releases/<active-release>/TASKS.md`
10. `specs/backlog/candidates.md`

Approval marker: `**Status:** Aprovado` in SPEC, PLAN, and TASKS is required
before implementation. Newly rebuilt artifacts stay `Em revisão` until the
operator explicitly approves them.

## Repo-Specific Stop Conditions

- Stop before any production edit under `rand_engine/`, `tests/`, docs, package
  metadata, or workflows unless the active release SPEC/PLAN/TASKS are
  `Aprovado` and the task is reserved in `TASKS.md`.
- Stop before treating DuckDB as a correlation engine. Current truth is:
  DuckDB supports integration/checkpoint state; correlation-engine behavior is
  future design work.
- Stop before changing public API names, generation method grammar, writer
  semantics, release/version policy, or supported Python/Spark matrix without
  updating specs first.
- Stop if a command would create repo-local caches such as `.venv/`,
  `.pytest_cache/`, `.coverage`, `coverage/`, `test-results/`, or
  `playwright-report/`.

## Key Paths

- `rand_engine/main/data_generator.py` - Pandas generation composition root.
- `rand_engine/main/spark_generator.py` - Spark generation facade.
- `rand_engine/main/_constraints_handler.py` - DuckDB-backed PK/FK checkpoint state.
- `rand_engine/core/` - NumPy, Python, and Spark generation primitives.
- `rand_engine/validators/` - RandSpec grammar validation.
- `rand_engine/file_handlers/` - batch and stream writers.
- `rand_engine/integrations/` - DuckDB and SQLite handlers.
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
DADAIA_CONTEXT=rand-engine .dadaia/.venv/bin/dadaia specs doctor
```
