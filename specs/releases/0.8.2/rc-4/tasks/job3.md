# Job 3 — test and docstring hygiene (wave 1)

Runs beside Jobs 1, 2 and 4. Order inside the job: T1, T2, T3 (after T2), T4 (after T3, same file as T3), T5. The files outside this job's `W:` that the backlog item names go to the job that owns them: `test_0_np_core.py` (Job 8), `test_eval_check.py:8` (Job 4), `test_eval_gate.py:28,37` (Job 5), `test_9_cli.py` (Job 2), `method_specs.py:213-214` (Job 7), `test_3_spark_generator.py` (Job 9). Test paths are `test(<id>)` commits (PLAN D7).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC21.2 | `tests/test_docs.py` | delete `_docs_site_module` and the `importlib.util` import (`:968-972,4`; grep shows no caller); a message after fence stripping keeps the page's line numbers (`:1033-1035`); a page without front matter fails naming the page, not with `AttributeError` (`:1050-1051`). Owner: the changed helpers themselves, each shown by running the failing input once in the hand-back |
| J3.T2 | jr | AC21.6 | `tests/test_2_data_generator_fails.py`, `tests/test_5_files_write_batch.py` | tighten the unset-size asserts at `test_2_data_generator_fails.py:179-182` and `test_5_files_write_batch.py:188-194` from `.size(n)` to the full literal of `resolve_size` ("No size set: call .size(n) with an int or a callable returning one."). Nothing loosened. `test(J3.T2)` |
| J3.T3 | jr | AC21.6 | `tests/test_2_data_generator.py` | delete the `get_df` and `save` cases of `:713-719`, keeping the `stream_dict` case with its full-literal assert. `test(J3.T3)`, body quotes the operator order: "Confirmo, apagar os 2 (Recommended)" and names J3.T2 as the tightened coverage |
| J3.T4 | jr | AC21.1 | `tests/test_2_data_generator.py` | rename the tests at `:424,628` for what they assert (`pd.NA`, Arrow text); asserts unchanged (diff shows only `def` lines). `test(J3.T4)` |
| J3.T5 | jr | AC21.3 | `rand_engine/main/_rand_generator.py`, `.github/workflows/benchmarks.yml` | `RandGenerator._column` (`:37`) drops "never empty" and says the Arrow branch wraps any Arrow type; the stale comment at `benchmarks.yml:37` is corrected against the line it describes. Text only; `docs(J3.T5)` |

Done when: `verify:`; `tests/test_docs.py`, `tests/test_2_data_generator.py`, `tests/test_2_data_generator_fails.py`, `tests/test_5_files_write_batch.py` pass. Sweep: `git grep -n "_docs_site_module" -- tests` prints nothing. Reviewer check (AC21.6): revert J3.T2 and the unset-size cases in the two files stay red on a changed message.
