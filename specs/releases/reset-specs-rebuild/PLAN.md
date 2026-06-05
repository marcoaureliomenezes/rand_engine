# PLAN: reset-specs-rebuild - rand-engine SDD foundation restart

**Status:** Em revisão
**Release ID:** reset-specs-rebuild
**Owner:** product-engineer
**Created:** 2026-06-05

## Phase 1 - Canonicalize SDD Tree

Create the current dadaia-workspace spec structure and remove deprecated
tree-v1 surfaces: root `specs/SPEC.md`, `specs/foundation/`, and
`specs/memory/product.md`.

## Phase 2 - Rebuild Product Truth

Replace placeholder memory with current truth: constitution, architecture,
tech-stack, product index, and atomic feature memory.

## Phase 3 - Preserve Audit Findings As Work

Record unresolved audit findings in backlog and release tasks without inventing
approval: DuckDB correlation design, runtime/validator mismatches, checkpoint
bug, spec mutation, Spark stubs, CDC staleness, test gaps, version drift, and
quality gate decisions.

## Phase 4 - Validate And Report

Run:

```bash
DADAIA_CONTEXT=rand-engine .dadaia/.venv/bin/dadaia specs doctor
```

Then emit product-engineer report and handoff under the workspace report/handoff
paths.

## Risk Controls

- Keep all new release artifacts `Em revisão`.
- Do not edit implementation, tests, docs, workflows, package metadata, or README.
- Do not create repo-local cache/state directories.
- Document unresolved decisions instead of silently deciding them.
