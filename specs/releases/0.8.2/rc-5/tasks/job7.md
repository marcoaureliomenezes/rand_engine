# Job 7 — eval task checks and `test_eval_tasks.py` (wave 2)

Waits on Job 3 (`pk-fk-constraints/tests/check.py` is renamed there). Runs beside Jobs 6, 8 and 9. `tests/integrations/test_eval_tasks.py` is shared by T2, T4, T5, T6: they run in that order, after T1 and T3. J7.T1's risk: `Keys._pk_at` is private and no public source of the pk defaults is found (`Keys.gen_pk` takes `**kwargs`, `rand_engine/core/_keys.py:76`); then the task stops and returns to the main thread, and no `rand_engine/` edit is made for the eval.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J7.T1 | sr | AC32.7 | `evals/tasks/pk-fk-constraints/tests/check.py` | `check.py` reads no private `Keys._pk_at` (`:16,51,55`); pass and fail cases unchanged. Owner: the `pk-fk-constraints` reference and decoy trials in `test_eval_tasks.py` |
| J7.T2 | jr | AC33.2 | `tests/integrations/test_eval_tasks.py` | a case accepts `rand-engine get-started --out=starter lake` (`:176-202`); reviewer check: dropping the `--out=VALUE` handling (`check.py:54`) turns it red |
| J7.T3 | jr | AC33.1, AC33.3 | `evals/tasks/get-started-cli/tests/check.py` | the `Ceilings:` sentence (`:43`) lists the four ruled ceilings of intake rows 115-116, one clause each; the `any(...)` continuation (`:70-71`) is indented under its opening. No other accept or refuse case changes. Owner: J7.T2 |
| J7.T4 | sr | AC37.7 | `tests/integrations/test_eval_tasks.py` | one reference trial per slug; the child env built once (`:85-86`, `:107-108`, `:227-228`); the unused runner (`:114`, `:125`) deleted; `:144` takes its literal from the case; the get-started fixture stops exec-ing the whole `check.py` (`:166-169`). The hand-back quotes the file's wall time against today's 31-102 s |
| J7.T5 | sr | AC37.8 | `tests/integrations/test_eval_tasks.py` | a case per usage slug asserts its reference trial ends in a `RESULT` line that `evals/run.py` `check_result` (`:86`) reads as layer `pass` with its `surfaces`; rides J7.T4's trials, no new trial |
| J7.T6 | jr | AC37.8 | `tests/integrations/test_eval_tasks.py` | delete `test_usage_check_prints_one_pass_line_with_layer_and_surfaces` (`:52-55`); `test(J7.T6)` quotes the order "Replace :52-55, keep rest (Recommended)"; `:59-62` and `:70-73` stay |

Done when: `verify:`; `tests/integrations/test_eval_tasks.py` passes, its wall time quoted.
