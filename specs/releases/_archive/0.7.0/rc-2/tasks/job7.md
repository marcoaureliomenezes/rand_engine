# Job 7 — integer schema validation prerequisite

**Status:** Approved
**done:** true

| task | AC | `W:` | outcome |
|---|---|---|---|
| J7.S1.T1 | AC6.2 | `tests/test_1_common_validator.py` | integer range validation RED · owner `tests/test_1_common_validator.py` · prove public `AdvancedValidator` and `DataGenerator` refusal for `min=101, max=100`, with literal `min=max` and `min<max` generation controls; no raw NumPy exception and no helper-owned validation. |
| J7.S2.T1 | AC6.2 | `rand_engine/validators/method_specs.py` `tests/test_1_common_validator.py` | canonical integer range semantics · owner `tests/test_1_common_validator.py` · make `_integers` refuse only typed `min > max`; retain equal, ordered, signed and unsigned accepted domains without a new ceiling or helper-local branch. |
| J7.S2.T2 | AC6.2 | `specs/releases/0.7.0/rc-2/tasks/job7.md` | close schema-validation prerequisite · owner `tests/test_1_common_validator.py` · after the stage contract is green, write terminal `done` exactly once and commit `chore(tasks): done job7-schema-validation`. |

## Contracts

- J7.S1 — RED: exit `tests/test_1_common_validator.py` fails by final assertion under a strict xfail marker for an inverted integer domain while literal equal and ordered boundary controls remain GREEN; envelope `tests/test_1_common_validator.py`; ACs AC6.2.
- J7.S2 — canonical catalog range semantics: exit `tests/test_1_common_validator.py` GREEN by deletion of only the satisfied marker, then write this job file's terminal `done` once; envelope `rand_engine/validators/method_specs.py tests/test_1_common_validator.py specs/releases/0.7.0/rc-2/tasks/job7.md`; ACs AC6.2.
