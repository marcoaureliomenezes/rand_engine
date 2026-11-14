# Job 4 — eval test hygiene 3 (wave 1)

Runs beside Jobs 1 to 3. J4.T2 deletes two lines on the operator's order, "Delete the glob assert (Recommended)" (2026-11-14); its `test(J4.T2)` commit quotes it verbatim.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | jr | AC48.1, AC48.2 | `tests/integrations/test_eval_tasks.py` | a function `_load_eval_run()` loads `evals/run.py` and returns the module, bound at module level as `eval_run`; `spec` is local to the function; the locals at `:99,104,151,234` are named `result`; the case at `:147` is renamed to state what all 11 rows hold (each reference trial passes its check, and an undecodable byte in an agent-written file, where the row writes one, does not crash it). Rows and asserts unchanged, no case added. Owner: the eval-task cases |
| J4.T2 | jr | AC48.3 | `tests/integrations/test_eval_check.py` | in `test_rerun_writes_no_bytecode` (`:196-200`) delete the `before` snapshot (`:198`) and the glob assert (`:200`); `monkeypatch.delenv` and the child-side `assert sys.dont_write_bytecode` stay. Commit `test(J4.T2): …`, body quotes the operator's order |

Done when: `verify:`; `tests/integrations/test_eval_tasks.py` and `tests/integrations/test_eval_check.py` pass; `git grep -nE '^(spec|run) =|^\s+run =' -- tests/integrations/test_eval_tasks.py` prints nothing; `git grep -n 'rglob("\*.pyc")' -- tests/integrations/test_eval_check.py` prints nothing.
