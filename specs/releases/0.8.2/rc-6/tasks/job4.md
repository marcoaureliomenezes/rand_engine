# Job 4 — the K guard names both bounds (wave 1)

Runs beside Jobs 1 to 3 and 5. Order T1, T2, T3: the RED first, then the guard, then the name in the same test file. The guard's literal pin and behaviour test move with the guard under grill ruling 2; the RED `test(J4.T1)` commit names that ruling.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC42.1, AC42.2, AC42.3 | `tests/integrations/test_public_api.py` | RED, `test(J4.T1)`: the K-guard case (`:912-919`) gains rows `"0"` and `"-1"`; a K outside 1 to 3 exits 1 with stderr exactly `k=<K>: k must be an integer from 1 to 3 (the job timeout fits k up to 3)` plus a newline; `"3"` exits 0 with empty stderr; the pin (`:905-909`) expects the `if [ "$K"` prefix, one `2>/dev/null`, and the guard before `python evals/run.py`; the case keeps its POSIX `skipif` and its name states the bounds 1 to 3. Red on stderr at 0a72a09 for every failing row |
| J4.T2 | jr | AC42.1, AC42.2 | `.github/workflows/eval.yml` | the guard line (`:145`) prints the ruled message and the first `[` carries `2>/dev/null`; the `if [ "$K"` prefix stays. Owner: J4.T1 |
| J4.T3 | jr | AC43.7 | `tests/integrations/test_public_api.py` | the test at `:858` is named for its asserts: the error carries the result event's reason and no `StopIteration`. Assert unchanged |

Done when: `verify:`; `tests/integrations/test_public_api.py` passes; `git grep -n 'paths:' -- .github/workflows/eval.yml` prints nothing; the diff of `eval.yml` is the one guard line.
