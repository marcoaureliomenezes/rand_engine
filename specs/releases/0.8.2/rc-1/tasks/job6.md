# Job 6 — did-you-mean in validation messages (wave 5)

One helper over stdlib `difflib.get_close_matches`, default cutoff, in `CommonValidator` (which `AdvancedValidator` already imports); no new module. It is the only ADD of the rc in `rand_engine/validators/` and nothing else holds a suggestion rule. Serial: T1 then T2.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | sr | AC3.1, AC3.2 | `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py` | RED: an unknown method, kwarg or column key with a close match gets one added line `Did you mean '<name>'?` on `AdvancedValidator.validate` and on `CommonValidator.validate_spark_spec` (`'integerz'` gives `'integers'`, `'mni'` gives `'min'`, `'null_rat'` gives `'null_rate'`); a name with no close match gets no suggestion line; every existing line of each message is asserted unchanged (type, banner, footer). Red today: no suggestion |
| J6.T2 | sr | AC3.1, AC3.2 | `rand_engine/validators/common_validator.py`, `rand_engine/validators/advanced_validator.py` | `CommonValidator` gains the helper; the four name-list sites consult it: parameter (`common_validator.py:94-100`), column key (`:116`), Spark method (`:190-203`), and `AdvancedValidator` method (`advanced_validator.py:83-99`); `_raise` and every existing message line stay. Sweep: `git grep -n get_close_matches -- rand_engine` prints one hit |

Done when: `verify:`; `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`, `tests/test_2_data_generator_fails.py`, `tests/test_docs.py` pass.
