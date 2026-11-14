# Job 1 — the K-guard tests state their rows (wave 1)

Runs beside Jobs 2 to 4. The guard itself (`.github/workflows/eval.yml`) is unchanged; one file, one task.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | jr | AC46.1, AC46.2, AC46.3 | `tests/integrations/test_public_api.py` | the guard-pin case (`:905`) is renamed to state that the trials step refuses a K outside 1 to 3 before the eval, literal and asserts unchanged; the refusal parametrize (`:913`) keeps rows `"4"`, `"0"`, `"-1"`, `"abc"`, `""`, `"2.5"` with one `ids=` list of 6 distinct ids; each asserts exit 1 and stderr exactly `f"k={k}: k must be an integer from 1 to 3 (the job timeout fits k up to 3)\n"`; `K="3"` is its own case, exit 0 and stderr `""`; no conditional in an expectation; both cases keep the POSIX `skipif`. Owner: the K-guard cases |

Done when: `verify:`; `tests/integrations/test_public_api.py` passes; `git grep -n 'if exit_code' -- tests/integrations/test_public_api.py` prints nothing; `git diff <base>...HEAD --name-only` is only that file.
