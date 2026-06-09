---
specs_pattern_version: 1
---
# Constitution: rand-engine

> This document defines the non-negotiable rules for rand-engine development.
> Every agent and human working in this repository must follow it.

## Project Purpose

rand-engine is a Python synthetic-data generation library optimized for fast,
deterministic generation of realistic dataframes, files, and relation-aware test
data. It exists for developers, QA engineers, data engineers, and platform teams
who need high-volume mock data without building custom fixtures by hand.

## Mandatory Technology Stack

| Component | Technology | Minimum |
|---|---|---|
| Language | Python | 3.10 |
| Package manager | Poetry | 2.x lock format currently present |
| Build backend | poetry-core | configured in `pyproject.toml` |
| Dataframe runtime | Pandas + NumPy | `pyproject.toml` runtime deps |
| Optional distributed runtime | PySpark | test dependency, common methods only |
| State/query backend | DuckDB | required runtime dependency |
| Secondary DB integration | SQLite stdlib | internal integration handler |
| Test runner | pytest + pytest-cov | configured by project tests |

No runtime dependency, build tool, release mechanism, or quality gate may be
added or replaced without updating this constitution and `specs/memory/tech-stack.md`.

## Product Invariants

- The supported public import surface is `DataGenerator`, `SparkGenerator`, and
  `RandSpecs` until an approved release changes it.
- RandSpec dictionaries are user input and must be treated as immutable. Runtime
  code must not delete or mutate user-provided spec keys.
- Deterministic seed behavior is a product feature. Any generator change must
  preserve documented reproducibility or explicitly revise the contract.
- DuckDB is currently a checkpoint/state and integration backend, not an
  approved correlation engine. DuckDB-backed correlation requires a dedicated
  approved design spec before implementation.
- Spark supports common generation methods. Advanced/correlation methods are not
  approved Spark behavior while they are null stubs.
- File writers must prove output correctness, not only successful execution:
  schema, row count, readability, compression, and destructive behavior must be
  accepted in tests.

## Security And Data Safety

- Never commit credentials, PyPI tokens, GitHub tokens, API keys, or generated
  local state.
- PyPI publishing must use Trusted Publishing/OIDC, not checked-in API tokens.
- rand-engine examples, templates, tests, committed fixtures, and generated
  evidence must use synthetic, sanitized, or license-safe public test data only.
- Production data, PII, unsafe fixtures, committed runtime logs, and unlicensed
  external datasets must not be committed, embedded in specs, used as fixture
  input, or captured in generated evidence.
- Future DuckDB/correlation features must not ingest sensitive production data
  or PII through external tables, persisted checkpoints, examples, tests, logs,
  or templates without an approved spec and security review.
- User-supplied SQL identifiers must be validated or quoted before they reach
  DuckDB/SQLite query construction. Raw query surfaces must remain internal until
  threat-modeled.
- Generated output paths must be explicit and testable; tests must write to
  pytest `tmp_path` or workspace `.dadaia/tmp/`, not persistent repo artifact
  directories.

## Architecture Principles

- `DataGenerator` and `SparkGenerator` are composition roots. Core generation
  primitives must stay independent from file writers, release tooling, and SDD
  state.
- Validators, runtime method dispatch, docs, and tests must converge on one
  generation method registry. Duplicated method catalogs are treated as drift.
- Relational state must be modeled through explicit ports before expanding
  DuckDB responsibilities. DuckDB/SQLite handlers are adapters, not product
  semantics by themselves.
- Stale modules must be classified as supported, deprecated, or removed. Broken
  packaged modules are not acceptable even when the public API tests pass.
- Public API compatibility is governed by semantic versioning and must be
  reflected in tests and release notes.

## Quality Gates

- Minimum current baseline evidence: full pytest suite green and coverage at or
  above the last audited baseline, 85.98%.
- Target restart gate for new feature work: coverage policy must be decided in
  the active release before implementation. QA recommends 90% project coverage
  or stricter feature-specific floors.
- Required future gates: pytest matrix, coverage threshold, package build,
  wheel install/import smoke, public API metadata checks, writer read-back
  checks, DuckDB lifecycle tests, lint/type policy, and hard security scan
  policy.
- Commands must disable or redirect caches so forbidden repo-local state is not
  created.

## Release Governance

- Current stable baseline is package/source/PyPI `0.6.3`.
- A newer prerelease exists as `0.6.4rc1` on remote development/PyPI/GitHub.
- README advertising `0.7.0` is drift until a release spec decides otherwise.
- Existing tag convention is numeric tags such as `0.6.3`; keep that convention
  unless an approved release migrates it.
- Stable releases must reconcile `pyproject.toml`, README badges, changelog,
  docs, PyPI metadata, GitHub release notes, and runtime version policy.

## SDD Workflow

- Production implementation requires approved `SPEC.md`, `PLAN.md`, and
  `TASKS.md` under `specs/releases/<active-release>/`.
- Status tokens are exactly `Draft`, `Em revisão`, and `Aprovado`.
- Do not mark a rebuilt spec `Aprovado` without explicit operator approval.
- Memory is present product truth, not changelog. Historical audit findings live
  in reports, backlog, release artifacts, and closure records.
- If implementation diverges from specs, update and re-approve specs before code
  changes continue.

## Spec Ownership Map

- `specs/constitution.md` is the project law.
- `specs/memory/architecture.md` is the source of package structure and
  architecture decisions.
- `specs/memory/tech-stack.md` is the source of dependency, tooling, CI, and
  release truth.
- `specs/memory/product/index.md` and atoms under `specs/memory/product/` are the
  source of product and feature truth.
- `specs/backlog/candidates.md` holds unresolved decisions and future candidates.
- `specs/releases/ACTIVE.md` selects the active release.
- `specs/releases/<release>/SPEC.md`, `PLAN.md`, and `TASKS.md` gate release work.
