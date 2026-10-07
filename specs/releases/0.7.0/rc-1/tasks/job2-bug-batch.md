# Job 2 — registered rc-1 bug batch

**Status:** Approved

## Stage J2.S1 — RED

- Contract: exit one strict-xfail assertion-level reproduction per registered bug, with prior registry and golden assertions retained; envelope `tests/test_0_py_core.py`, `tests/test_1_advanced_validator.py`, `tests/test_2_data_generator.py`; ACs AC13.2 and the three registered-bug contracts
- J2.S1.T1 — method-registry-has-five-owners, distincts-multi-map-drops-levels-silently · `W:` `tests/test_1_advanced_validator.py` · owner `tests/test_1_advanced_validator.py` · RED: pandas `args` and invalid complex templates reject before generation; multi-map `cols` equals levels + 1
- J2.S1.T2 — distincts-map-column-order-reversed, AC13.2 · `W:` `tests/test_0_py_core.py`, `tests/test_2_data_generator.py` · owner `tests/test_0_py_core.py` · RED: category first; stage the deliberate map and multi-map golden expectations

## Stage J2.S2 — registry rebuild

- Contract: exit registry cases green and one validator contract agrees with both engine dispatch maps and callable parameters; envelope the modules below; ACs the method-registry-has-five-owners contract
- J2.S2.T1 — method-registry-has-five-owners · `W:` `rand_engine/validators/common_validator.py`, `rand_engine/validators/advanced_validator.py`, `rand_engine/main/_rand_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/core/_py_core.py`, `tests/test_1_advanced_validator.py` (RED marker lines only), `specs/bugs/BUGS.jsonl` (by `bugs.py resolve` only) · owner `tests/test_1_advanced_validator.py` · REBUILD the registry authority, remove pandas `args`, and validate complex templates through the engine contract

## Stage J2.S3 — correlated methods

- Contract: exit exact multi-map arity and category-first output green without changing unrelated seeded output; envelope the paths below; ACs AC13.2 and the two correlated-method bug contracts
- J2.S3.T1 — distincts-multi-map-drops-levels-silently, AC13.2 · `W:` `rand_engine/validators/advanced_validator.py`, `benchmarks/speed.py`, `tests/test_1_advanced_validator.py` (RED marker line only), `tests/test_2_data_generator.py` (RED marker line only), `specs/bugs/BUGS.jsonl` (by `bugs.py resolve` only) · owner `tests/test_1_advanced_validator.py` · enforce levels + 1 and correct only its sample/golden

## Stage J2.S4 — category-first map

- Contract: exit category-first output green without changing unrelated seeded output; envelope the paths below; ACs AC13.2 and the distincts-map-column-order-reversed contract
- J2.S4.T1 — distincts-map-column-order-reversed, AC13.2 · `W:` `rand_engine/core/_py_core.py`, `docs/1_DATA_GENERATOR.md`, `CHANGELOG.md`, `tests/test_0_py_core.py` (RED marker line only), `tests/test_2_data_generator.py` (RED marker line only), `specs/bugs/BUGS.jsonl` (by `bugs.py resolve` only) · owner `tests/test_0_py_core.py` · emit category first and correct only its docs/changelog/golden

## Stage J2.S5 — close

- Contract: exit unit + integration green, none of the three ids open, and FR13 goldens cover the unchanged method set; envelope this file; ACs AC13.2 and the three registered-bug contracts
- J2.S5.T1 — AC13.2 · `W:` this file (`done`) · owner `tests/test_2_data_generator.py`
