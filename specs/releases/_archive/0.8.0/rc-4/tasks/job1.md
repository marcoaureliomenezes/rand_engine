# Job 1 — Event-time FK foundation

**Wave:** 1
**Waits on:** —
**W:** `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py`,
`rand_engine/core/_keys.py`, `rand_engine/validators/method_specs.py`,
`rand_engine/validators/advanced_validator.py`, `docs/1_DATA_GENERATOR.md`,
`skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.4 | `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py` | RED tests for exact four-field grammar, builtin numeric types/bool refusal, inclusive/clamped eligibility, zero eligible parent, seed determinism and continuity through uneven parts and streams. Include huge valid row indexes and values that prove accepted input never overflows into engine failure. |
| J1.T2 | sr | AC1.1–AC1.4 | `rand_engine/core/_keys.py`, `rand_engine/validators/method_specs.py`, `rand_engine/validators/advanced_validator.py` | Implement one catalog/validator grammar and one internal indexed `Keys` eligibility/value path. Preserve ordinary FK values when `born_before` is omitted; use it for pandas offsets without altering protected `gen_*` bodies. |
| J1.T3 | sr | AC5.2 | `docs/1_DATA_GENERATOR.md`, `skills/rand-engine/SKILL.md` | Synchronize only the catalog-derived `born_before` optional-parameter inventory in the DataGenerator guide and skill after J1.T2. This is the immediate consumer update required by the existing inventory contract; Job 5 retains all broader guidance. |

`J1.T2` may not edit tests. The implementation uses integer/rational-safe internal
arithmetic where needed; it does not expose a new numeric input type.

J1.T3 is the bounded operator-authorized consumer-order workaround: the normal
definition plan would defer these consumers to Job 5, but the existing inventory
test requires them when Job 1's catalog changes. It changes no behavior, test,
gate, workspace rule or release phase and does not bypass the worktree workflow.
