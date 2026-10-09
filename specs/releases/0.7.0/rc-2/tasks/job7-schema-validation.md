# Job 7 — integer schema validation prerequisite

**Status:** Approved

## Stage J7.S1 — RED

- Contract: exit `tests/test_1_common_validator.py` fails by final assertion under a strict xfail marker for an inverted integer domain while literal equal and ordered boundary controls remain GREEN; envelope `tests/test_1_common_validator.py`; ACs AC6.2.
- J7.S1.T1 — integer range validation RED · AC6.2 · `W:` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · prove public `AdvancedValidator` and `DataGenerator` refusal for `min=101, max=100`, with literal `min=max` and `min<max` generation controls; no raw NumPy exception and no helper-owned validation.

## Stage J7.S2 — canonical catalog range semantics

- Contract: exit `tests/test_1_common_validator.py` GREEN by deletion of only the satisfied marker, then write this job file's terminal `done` once; envelope `rand_engine/validators/method_specs.py tests/test_1_common_validator.py specs/releases/0.7.0/rc-2/tasks/job7-schema-validation.md`; ACs AC6.2.
- J7.S2.T1 — canonical integer range semantics · AC6.2 · `W:` `rand_engine/validators/method_specs.py` `tests/test_1_common_validator.py` · owner `tests/test_1_common_validator.py` · make `_integers` refuse only typed `min > max`; retain equal, ordered, signed and unsigned accepted domains without a new ceiling or helper-local branch.
- J7.S2.T2 — close schema-validation prerequisite · AC6.2 · `W:` `specs/releases/0.7.0/rc-2/tasks/job7-schema-validation.md` · owner `tests/test_1_common_validator.py` · after the stage contract is green, write terminal `done` exactly once and commit `chore(tasks): done job7-schema-validation`.
