# Job 3 — library test hygiene: docs and consistency tests (wave 1)

Runs beside Jobs 1, 2, 4 and 5. Test and docstring text only.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC40.5 | `tests/test_docs.py` | each of the six `re.search(...).group()` sites (`:165,579,870,1010,1011,1036`) asserts its match first, with a message naming its page or section, as `:1044-1046` does. Owner: the six cases themselves, asserts otherwise unchanged. `git grep -nE 're\.(search\|match)\(.*\)\.group' -- tests evals` prints nothing |
| J3.T2 | jr | AC40.6, AC40.7, AC40.9 | `tests/test_8_consistency.py`, `tests/test_1_common_validator.py` | `test_8_consistency.py:335` states its pins with no `proto/` path; `:418` reads "writeStream into 10 files carries ids 1..1000 and the parent_id of one 1000-row get_df"; `test_spark_float_span_overflowing_float64_is_refused` (`test_1_common_validator.py:772`) carries the one-line docstring "max - min is inf in float64". `git grep -n 'proto/' -- tests/` prints nothing. The full three-grep sweep of AC40.9 runs at the `wt-rc` once Jobs 2 and 3 are merged |

Done when: `verify:`; `tests/test_docs.py`, `tests/test_8_consistency.py`, `tests/test_1_common_validator.py` pass; the diff touches no assert but the six named sites.
