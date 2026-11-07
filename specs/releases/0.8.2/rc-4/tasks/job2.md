# Job 2 — the Spark test session and the databricks starter (wave 1)

Runs beside Jobs 1, 3 and 4. T1 (RED) first; T2 turns it green; T3 is independent (fixture only); T4 follows T1 (same test file). The Arrow conf at `databricks.py.txt:44` stays: it is user advice (PLAN D6).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC20.1, AC20.3 | `tests/test_9_cli.py` | RED: (a) the test that runs the databricks starter on the shared `spark_session` (`:165-176`) leaves `spark.sql.execution.arrow.pyspark.enabled` as it found it, by a restore in the test or an isolated session (sr picks; the literal expectation is the value read before the run); (b) the scaffold and the docs page carry no `netty` text (`check_databricks` and a read of `docs/tutorials/databricks.md`). Red today on (b); (a) is a regression pin that fails if the restore is removed. `test(J2.T1)` |
| J2.T2 | jr | AC20.3 | `rand_engine/cases/databricks.py.txt`, `docs/tutorials/databricks.md` | delete the netty sentence (`.py.txt:39`) and its prose copy (`.md:35`); nothing else moves. Owner: J2.T1(b). Consumer sweep: `git grep -n -e netty -e tryReflectionSetAccessible -- rand_engine docs tests` lists only the fixture comment J2.T3 removes |
| J2.T3 | jr | AC20.2 | `tests/fixtures/f2_spark_generator_specs_right.py` | delete the Java 17 option block and its comment (`:35-39`), the two `extraJavaOptions` configs (`:46-47`); no other config changes. `test(J2.T3)`; the three Arrow tests of `tests/test_3_spark_generator.py` pass on CI's Java 17 (the E2E leg), and the whole Spark suite passes locally when Java is present |
| J2.T4 | jr | AC21.4 | `tests/test_9_cli.py` | `:172-176`: parametrize (slug, expectation) so the test body has no slug branch; every expectation is kept as a literal. `test(J2.T4)`. Owner: the test itself, red-proofed by reverting one expectation |

Done when: `verify:`; `tests/test_9_cli.py` and `tests/test_3_spark_generator.py` pass. Sweep: `git grep -n "add-opens" -- tests rand_engine docs` prints nothing.
