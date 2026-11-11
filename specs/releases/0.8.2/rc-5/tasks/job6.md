# Job 6 — `run.py`, `gate.py`, `eval.yml` and their tests (wave 2)

Runs beside Jobs 7, 8 and 9; disjoint from Job 3 (it does not touch `_check.py`). Order inside the job: `test_public_api.py` tasks T1, T3, T7, T9 then T8; `test_eval_gate.py` tasks T2 then T8; each implementation after its RED.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | sr | AC32.5 | `tests/integrations/test_public_api.py` | RED, `test(J6.T1)`: a failing check that also prints a malformed `RESULT` line keeps `first_failure`; a stream with no result event raises naming the missing result event, never "no init event: None" |
| J6.T2 | sr | AC32.6 | `tests/integrations/test_eval_gate.py` | RED, `test(J6.T2)`: `gate.py --calibrate` with a missing results directory names the missing results and exits non-zero, no `FileNotFoundError`; the "passed and no error" cases hold through one decider |
| J6.T3 | sr | AC32.6 | `tests/integrations/test_public_api.py` | RED, `test(J6.T3)`: the K guard (`eval.yml:145`) fails closed on a non-integer K |
| J6.T4 | jr | AC32.5 | `evals/run.py` | `:152-154` keeps `first_failure`; `:134` raises the named error. Owner: J6.T1 |
| J6.T5 | jr | AC32.6 | `evals/gate.py` | "passed and no error" decided once (`:80`, `:86`); `:117` reports missing results truly. Owner: J6.T2 |
| J6.T6 | jr | AC32.6 | `.github/workflows/eval.yml` | the K guard fails closed on a non-integer; no `paths` filter. Owner: J6.T3 |
| J6.T7 | sr | AC37.3 | `tests/integrations/test_public_api.py` | `:853` replaces a boundary, not `run.run_trial`; `:912` accepts only the guard form `eval.yml` ships; `:848` expects one literal per case; the concurrency test (`:954`) pins `cancel-in-progress`. Each assert tightens, none loosens |
| J6.T8 | jr | AC37.5 | `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_gate.py` | the tests at `test_public_api.py:948` and `test_eval_gate.py:222` are named for their asserts |
| J6.T9 | jr | AC37.4 | `tests/integrations/test_public_api.py` | pending the operator's order (SPEC §6.1): the malformed-result test (`:823`) asserts `passed` is false and its repeat (`:830`) folds into it; `test(J6.T9)` quotes the order. Without it: cancelled, both stay |

Done when: `verify:`; `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_gate.py` pass. Sweep: `git grep -n "paths:" -- .github/workflows/eval.yml` prints nothing.
