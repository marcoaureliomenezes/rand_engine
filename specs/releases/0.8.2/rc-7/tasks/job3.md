# Job 3 — the docs tests name the page that drifted (wave 1)

Runs beside Jobs 1, 2 and 4. Job 5 waits on this job's merge (`tests/test_docs.py` is in both write sets).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC47.3 | `tests/test_docs.py` | each bare match assert at `:88` (`_table_rows`, `match`), `:340` (the Method-and-Spark table of `2_SPARK_GENERATOR.md`, `match`) and `:888` (the CHANGELOG 0.8.0 `### Fixed` group, `fixed`) gains a message naming the page and what was not found, modelled on `:884`. The nine non-match `is not None` asserts elsewhere stay. Owner: the docs cases |

Done when: `verify:`; `tests/test_docs.py` passes (the three Spark rows need Java); `git grep -nE 'assert \w+ is not None\s*$' -- tests/test_docs.py` prints nothing.
