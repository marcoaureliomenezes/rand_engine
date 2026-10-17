# Job 1 — Event-time FK foundation

**Wave:** 1
**Waits on:** —
**W:** `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py`,
`rand_engine/core/_keys.py`, `rand_engine/validators/method_specs.py`,
`rand_engine/validators/advanced_validator.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.4 | `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py` | RED tests for exact four-field grammar, builtin numeric types/bool refusal, inclusive/clamped eligibility, zero eligible parent, seed determinism and continuity through uneven parts and streams. Include huge valid row indexes and values that prove accepted input never overflows into engine failure. |
| J1.T2 | sr | AC1.1–AC1.4 | `rand_engine/core/_keys.py`, `rand_engine/validators/method_specs.py`, `rand_engine/validators/advanced_validator.py` | Implement one catalog/validator grammar and one internal indexed `Keys` eligibility/value path. Preserve ordinary FK values when `born_before` is omitted; use it for pandas offsets without altering protected `gen_*` bodies. |

`J1.T2` may not edit tests. The implementation uses integer/rational-safe internal
arithmetic where needed; it does not expose a new numeric input type.
