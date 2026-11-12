# Job 6 — the eval tests: bytecode, reference trials and the bare-pk row (wave 2)

Waits on Job 5 for J6.T8 only; T1 to T7 do not read Job 5's output. Order inside the job: `test_eval_check.py` tasks T1, T2, T3, then `test_eval_tasks.py` tasks T4, T5, T6, T7, T8, so T8 is the last. Asserts are unchanged except where a task says it tightens.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | sr | AC43.1 | `tests/integrations/test_eval_check.py` | RED, `test(J6.T1)`: under `PYTHONDONTWRITEBYTECODE=1` (the `verify:` line's env), `test_rerun_writes_no_bytecode` asserts the set of `.pyc` files under `rand_engine/` is equal before and after; it still asserts the re-run's own `sys.dont_write_bytecode`. Red at 0a72a09 (7 `__pycache__` dirs after a lone run) |
| J6.T2 | jr | AC43.1 | `tests/integrations/test_eval_check.py` | `run_script` (`:62-64`) delivers the artifacts with the flag set, so the agent-run subprocess writes no bytecode; the case's `delenv` (`:196`) no longer reaches it. Owner: J6.T1 |
| J6.T3 | jr | AC41.5 | `tests/integrations/test_eval_check.py` | rename `record` to `generations` (26 whole-word hits, docstring and locals); `RAND_EVAL_RECORD` and `"records"` stay. Owner: the provenance cases, asserts unchanged |
| J6.T4 | jr | AC43.5 | `tests/integrations/test_eval_tasks.py` | delete the `CUSTOMER_PK` row (`:93`) of `test_pk_fk_check_accepts_a_parent_equal_to_the_pk_after_its_defaults`; `test(J6.T4)` quotes the order "Delete :93 duplicate (Recommended)"; the pk-fk-constraints row (`:142`) and the constant stay |
| J6.T5 | jr | AC43.3 | `tests/integrations/test_eval_tasks.py` | `run` is loaded by `importlib.util.spec_from_file_location`, as `test_eval_check.py:43`, `test_eval_gate.py:17` and `test_public_api.py:689` load their modules; `git grep -n 'sys.path' -- tests/integrations/test_eval_tasks.py` prints nothing |
| J6.T6 | jr | AC43.4 | `tests/integrations/test_eval_tasks.py` | the name at `:147` covers all 11 rows: each reference trial passes its check, and an undecodable byte in an agent-written file does not crash it |
| J6.T7 | sr | AC43.6 | `tests/integrations/test_eval_tasks.py` | one row of the existing parametrize: a bare `'{"method": "pk"}'` parent expects exit 0 and `"layer": "pass"`. Green at birth (grill 4); the hand-back says so and the reviewer mutates `pk_identity` (`evals/tasks/pk-fk-constraints/tests/check.py:50-57`) and sees the row red |
| J6.T8 | sr | AC43.2 | `tests/integrations/test_eval_tasks.py` | waits on Job 5 (J5.T2): `reference_trial` (`:107-125`) copies a task's seed environment through `run.seed_cwd`; the transcript rule stays, with a one-line docstring note naming `evals/selfcheck.py` as its source. Net test lines ≤ 0. Owner: the reference trials, asserts unchanged |

Done when: `verify:`; `tests/integrations/test_eval_check.py`, `tests/integrations/test_eval_tasks.py` pass (Spark row may be deselected in scratch); a lone run of `test_rerun_writes_no_bytecode` under the `verify:` env leaves the `.pyc` set under `rand_engine/` as found; `git grep -nw record -- tests/integrations/test_eval_check.py` prints nothing.
