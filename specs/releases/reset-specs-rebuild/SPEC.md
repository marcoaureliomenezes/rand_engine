# SPEC: reset-specs-rebuild - rand-engine SDD foundation restart

**Status:** Em revisão
**Release ID:** reset-specs-rebuild
**Owner:** product-engineer
**Created:** 2026-06-05

## 1. Objective

Rebuild rand-engine's SDD foundation so future implementation can restart from
canonical dadaia-workspace truth instead of placeholder specs.

This release establishes:

- Real constitution for rand-engine.
- Current-state memory for architecture, tech stack, product, and features.
- Canonical release/backlog/bugs structure.
- Audit-preserving backlog candidates for implementation work.
- Explicit block on production changes until this reset is reviewed and approved.

## 2. Evidence Inputs

This reset is based on the completed audit fan-out:

- Project audit: `2026-06-05T052047Z-reset-baseline-audit.html`.
- DevOps audit: `2026-06-05T052131Z-packaging-release-audit.html`.
- Architecture audit: `2026-06-05T052136Z-full-architecture-audit.html`.
- Python implementation audit: `2026-06-05T052226Z-python-implementation-audit.html`.
- QA audit: `2026-06-05T052837Z-full-test-quality-audit.html`.

## 3. Scope

In scope:

- Replace placeholder `AGENTS.md` and `specs/constitution.md`.
- Migrate memory to `specs/memory/product/index.md` plus product atoms.
- Add frontmatter to memory atoms.
- Remove deprecated root `specs/SPEC.md`, deprecated `specs/foundation/`, and
  non-canonical `specs/memory/product.md`.
- Create `specs/AGENTS.md`, `specs/backlog/candidates.md`, `specs/bugs/`,
  `specs/releases/ACTIVE.md`, and this release directory.
- Preserve future implementation findings as backlog candidates and release
  tasks.
- Run `dadaia specs doctor` and record remaining issues.

Out of scope:

- Any production code change under `rand_engine/`.
- Tests, docs, `pyproject.toml`, workflows, package metadata, or README edits.
- Promoting `0.6.4rc1`, publishing, or version changes.
- Implementing DuckDB-backed correlations.

## 4. Current Product Truth

rand-engine is a high-value Python synthetic-data generation library. Its core
strength is fast synthetic data generation through vectorized NumPy/Pandas paths,
with Spark support for common methods, validators, file writers, streaming,
templates/examples, DB integrations, and DuckDB-backed PK/FK checkpoint state.

DuckDB is not a correlation engine today. Current correlations are in-memory
advanced methods, while DuckDB persists/query-checkpoints relation state for
constraints.

## 5. Known Follow-up Work

Follow-up implementation must be split into approved releases. Priority items:

- DuckDB-backed correlation engine design.
- `distincts_external` validation/runtime mismatch.
- `checkpoint()` active handler bug.
- DataGenerator spec mutation bug.
- Spark advanced null stubs.
- Stale CDC module classification.
- Writer correctness tests.
- Quality gate hardening.
- Version/release truth reconciliation.

## 6. Acceptance Criteria

- `dadaia specs doctor` has no structural errors, or remaining issues are
  explicitly documented in the product-engineer report.
- Canonical tree exists under `specs/releases/`, `specs/backlog/`,
  `specs/bugs/`, and `specs/memory/product/`.
- Memory files describe current product truth and include YAML frontmatter where
  required.
- Release SPEC/PLAN/TASKS remain `Em revisão` until operator approval.
- No production code, tests, docs, workflows, package metadata, or README files
  are changed in this pass.

## 7. Operator Decisions Required

- Approve or revise the rebuilt SDD foundation.
- Decide the next implementation release ordering.
- Decide the version baseline: keep stable `0.6.3`, promote/discard `0.6.4rc1`,
  or start a new base version.
- Decide DuckDB's future role: constraints only, correlations only, or both.
- Decide the restart quality gate threshold and whether security scans block.
