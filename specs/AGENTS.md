# rand-engine specs rules

This file governs `repos/rand-engine/specs/**`.

## Status Tokens

Use only these SDD status tokens:

- `Draft`
- `Em revisão`
- `Aprovado`

Do not translate them.

## Canonical Tree

- Active release pointer: `specs/releases/ACTIVE.md`
- Release artifacts: `specs/releases/<release-id>/SPEC.md`, `PLAN.md`, `TASKS.md`
- Product memory: `specs/memory/product/index.md` plus atoms in
  `specs/memory/product/*.md`
- Backlog: `specs/backlog/candidates.md`
- Bugs: `specs/bugs/*.md` when bug records exist

Deprecated root `specs/SPEC.md`, `specs/foundation/`, and
`specs/memory/product.md` must not be recreated.

## Memory Rules

Memory is current product truth, not changelog. Product atoms require YAML
frontmatter compatible with dadaia memory lint. Use reports, backlog, release
artifacts, and CLOSURE files for history.

## Implementation Gate

No production edit may begin unless the active release SPEC/PLAN/TASKS are
`Aprovado`, the task is reserved with `[-]`, and the write set matches the task.
