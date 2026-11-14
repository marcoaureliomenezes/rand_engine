# Job 2 — library test hygiene: one-row parametrize and docstrings (wave 1)

Runs beside Jobs 1, 3 and 4. Asserts are unchanged in every task.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC47.1 | `tests/test_0_np_core.py`, `tests/test_1_common_validator.py`, `tests/test_2_data_generator.py` | delete the six one-row `parametrize` decorators (`test_0_np_core.py:642,658`, `test_1_common_validator.py:749`, `test_2_data_generator.py:151,165,182`); bind each value in the case's body. Owner: the six cases, asserts unchanged |
| J2.T2 | jr | AC47.2 | `tests/test_8_consistency.py` | the docstring at `:335` states the case pins `gen_fk` heads by seed; `:342` states it pins the top-of-domain rank literal; neither names `zipf_index` or `proto`. Docstring text only |

Done when: `verify:`; the four test files pass; `git grep -nwE -e zipf_index -e proto -- tests/test_8_consistency.py` prints nothing; `git grep -n 'parametrize' -- tests/test_0_np_core.py tests/test_1_common_validator.py tests/test_2_data_generator.py` shows none of the six decorators.
