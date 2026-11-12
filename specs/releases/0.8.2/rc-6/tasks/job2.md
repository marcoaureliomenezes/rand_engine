# Job 2 — library test hygiene: writer, benchmark and fixture tests (wave 1)

Runs beside Jobs 1, 3, 4 and 5. Each task is a test or law-text edit whose owner test already exists; none adds a case. T1 is the only task in `test_5_files_write_batch.py`.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC40.3, AC40.4 | `tests/test_5_files_write_batch.py` | the refusal case (`:252-263`) saves to `tmp_path / f"f.{format_type}"`, the json rows keep `f.json`; the one-row parametrize (`:284-290`) becomes a plain case keeping the literal `^json option 'indent' is not documented; accepted: orient, force_ascii, compression$` and its `not path.exists()` assert. Revert-check in the hand-back: drop the csv refusal in `file_handler.py` in scratch, the csv row goes red |
| J2.T2 | jr | AC40.1, AC40.2 | `tests/test_benchmarks.py`, `tests/test_9_cli.py`, `tests/test_3_spark_generator.py` | `test_benchmarks.py:194` is named for what its rows pin, the quickest base and head samples; `spark_guard` (`:167-171`) and `arrow_conf` (`:703-705`) `return` their value with no `yield`; `arrow_conf_restored` keeps the restore. Rows and asserts unchanged |
| J2.T3 | jr | AC40.8, AC40.9 | `tests/AGENTS.md` | `:8` names `test_benchmarks.py` as owning the speed benchmark script, with no requirement id. `git grep -nE -e '\bAC[0-9]+' -e '\bFR[0-9]+' -- tests/` prints nothing |

Done when: `verify:`; `tests/test_5_files_write_batch.py`, `tests/test_benchmarks.py`, `tests/test_9_cli.py`, `tests/test_3_spark_generator.py` pass (Spark rows may be deselected in scratch; CI runs them); `git diff <base>...HEAD -U0 -- tests | grep -E '^-.*assert'` is empty except the rewritten lines J2.T1 tightens.
