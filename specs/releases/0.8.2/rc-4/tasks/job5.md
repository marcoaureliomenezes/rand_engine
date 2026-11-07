# Job 5 — honest trial records and workflow guards (wave 2)

Waits on Job 4. Runs beside Jobs 6, 7 and 8. Test files are shared across the RED tasks, so order inside the job: T1, T3, T4 (all `test_public_api.py`); T2 (`test_eval_gate.py`) beside them; T5 after T1, T6 after T2, T7 after T3. The RED tasks add asserts; the existing ones are only tightened (PLAN D7).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J5.T1 | sr | AC23.1, AC23.2 | `tests/integrations/test_public_api.py` | RED, `test(J5.T1)`: in the `run.py` contract tests, a trial whose run raises records `passed: false`; the trial JSON holds the agent's final message and the check's first failure line; the file is written as UTF-8; a stream with no init event raises an error naming the result event's `errors` or `startup_failure_reason`, never `StopIteration` |
| J5.T2 | sr | AC23.3, AC21.4 | `tests/integrations/test_eval_gate.py` | RED, `test(J5.T2)`: a discovery trial with no surface counts as `other`, never `None`; a passing usage trial with unknown tokens prints `tokens unknown`, never `-`. The fixture writes at `:28,37` use `encoding="utf-8"` |
| J5.T3 | sr | AC23.4 | `tests/integrations/test_public_api.py` | RED, `test(J5.T3)`, hardened never loosened: `eval.yml`'s `pull_request` trigger has a concurrency group and still no `paths` filter; the trials step fails for `k` above 3; `apt-get update` runs before `apt-get install`; the sysctl lift runs only where its key exists |
| J5.T4 | jr | AC23.5 | `tests/integrations/test_public_api.py` | tighten the pin at `:854` to assert the `apt-get install -y bubblewrap socat` line and its place before `python evals/run.py`, then delete the separate socat test (`:859-861`) in the same commit. `test(J5.T4)`, body quotes the operator order: "Confirmo, apagar os 2 (Recommended)" and names the tightened assert that carries the socat line. Reviewer check: reverting the tightening turns it red |
| J5.T5 | jr | AC23.1, AC23.2 | `evals/run.py` | the matching edits in `run_trial` and `main`: an errored trial `passed: false`, final message and first failure line in the record, `StopIteration` replaced by the named error, `encoding="utf-8"` on the write (`:182`). The token env at `:113-117` is untouched. Owner: J5.T1 |
| J5.T6 | jr | AC23.3 | `evals/gate.py` | `:109` counts a `None` surface as `other`; `:83-85` prints `tokens unknown` for unknown tokens. No fourth walk over `specs`. Owner: J5.T2 |
| J5.T7 | jr | AC23.4 | `.github/workflows/eval.yml` | the concurrency group (no `paths` filter), the `k` guard, `apt-get update` before `apt-get install`, the sysctl guard. Owner: J5.T3 |

Done when: `verify:`; `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_gate.py` pass. Sweep: `git grep -n "paths:" -- .github/workflows/eval.yml` prints nothing.
