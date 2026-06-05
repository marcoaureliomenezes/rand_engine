# TASKS: reset-specs-rebuild - rand-engine SDD foundation restart

**Status:** Em revisão
**Release ID:** reset-specs-rebuild
**Owner:** product-engineer
**Created:** 2026-06-05

Marks: `[ ]` OPEN, `[-]` IN PROGRESS, `[x]` DONE.

## Group G1 - SDD Foundation Reset

### T-SDD-01 - Rebuild repo AGENTS and constitution

- **Status:** [x]
- **Owner:** product-engineer
- **Write set:**
  - `AGENTS.md`
  - `specs/constitution.md`
- **Acceptance:**
  - Repo rules describe rand-engine purpose, spec load order, stop conditions,
    key paths, and safe commands.
  - Constitution defines product invariants, architecture principles, quality
    gates, release governance, and SDD workflow.

### T-SDD-02 - Rebuild canonical memory

- **Status:** [x]
- **Owner:** product-engineer
- **Write set:**
  - `specs/memory/architecture.md`
  - `specs/memory/tech-stack.md`
  - `specs/memory/product/index.md`
  - `specs/memory/product/*.md`
- **Acceptance:**
  - Memory contains current product truth, not history.
  - Memory atoms include required YAML frontmatter.
  - Product index links the atomic feature set.

### T-SDD-03 - Replace legacy tree-v1 layout

- **Status:** [x]
- **Owner:** product-engineer
- **Write set:**
  - `specs/AGENTS.md`
  - `specs/backlog/candidates.md`
  - `specs/bugs/`
  - `specs/releases/`
  - delete `specs/SPEC.md`
  - delete `specs/foundation/`
  - delete `specs/memory/product.md`
- **Acceptance:**
  - Canonical tree-v2 surfaces exist.
  - Deprecated root spec, foundation dir, and non-canonical product memory are
    absent.

### T-SDD-04 - Validate specs doctor and emit handoff

- **Status:** [x]
- **Owner:** product-engineer
- **Write set:**
  - `.dadaia/reports/rand-engine/product-engineer/`
  - `.dadaia/handoff/rand-engine/`
- **Acceptance:**
  - `dadaia specs doctor` is run after edits.
  - Report records remaining issues and unresolved decisions.
  - Handoff validates with `dadaia reports validate`.

## Group G2 - Future Implementation Candidates

### T-FUT-01 - Design DuckDB-backed correlation model

- **Status:** [ ]
- **Owner:** software-architect + software-engineer-python + qa-engineer
- **Write set:** TBD in a future approved release.
- **Acceptance:**
  - Decide DuckDB role for correlations/constraints.
  - Define grammar, persistence, query safety, determinism, Spark boundaries,
    and acceptance tests before code changes.

### T-FUT-02 - Fix validation/runtime mismatches

- **Status:** [ ]
- **Owner:** software-engineer-python
- **Write set:** TBD in a future approved release.
- **Acceptance:**
  - `distincts_external` either becomes implemented/tested or is removed from
    supported validation.
  - Parameter alias drift such as `dtype`/`int_type` and
    `prob_true`/`true_prob` is resolved.

### T-FUT-03 - Fix checkpoint and spec mutation defects

- **Status:** [ ]
- **Owner:** software-engineer-python
- **Write set:** TBD in a future approved release.
- **Acceptance:**
  - `checkpoint()` rewires/persists constraints as specified.
  - DataGenerator does not mutate user specs.
  - Regression tests prove both behaviors.

### T-FUT-04 - Classify Spark advanced and CDC support

- **Status:** [ ]
- **Owner:** software-architect + software-engineer-python + qa-engineer
- **Write set:** TBD in a future approved release.
- **Acceptance:**
  - Spark advanced methods either fail explicitly or are implemented.
  - CDC module is supported with tests, deprecated, or removed.

### T-FUT-05 - Harden QA, release, and metadata gates

- **Status:** [ ]
- **Owner:** qa-engineer + devops-engineer
- **Write set:** TBD in a future approved release.
- **Acceptance:**
  - Decide coverage threshold and hard security behavior.
  - Add lint/type policy or explicitly defer it.
  - Reconcile `0.6.3`, `0.6.4rc1`, and README `0.7.0` drift.
  - Ensure package build/install/import/version checks are release gates.
