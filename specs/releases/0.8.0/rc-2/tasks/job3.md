# Job 3 — FR2 Spark on Python 3.13: the skip predicate and the docs line

**Wave:** 2 · **Waits on:** Job 1, Job 2

Runs after the main thread pushed `feature/0.8.0` with Jobs 1 and 2 merged and read that CI run (PLAN §3.3: pyspark 3.5.8 passes on Linux 3.13 in a measured run; macOS 3.13 is unmeasured, Windows 3.13 is already skipped by `>= (3, 12)`).

- The brief carries the run id and the failing 3.13 Spark legs, or "none".
- J3.T1 is conditional: with no failing Spark leg it is cancelled and its row keeps that reason; AC2.2 then holds with zero code, because the one predicate already skips where Spark cannot run and Spark runs everywhere else. With a failing leg it widens the one predicate to exactly the failing platform, with a reason naming pyspark 3.5 and Python 3.13, and the commit body cites the failing run id.
- J3.T2 states the true requirement in one line (AC2.4). The operator's grill wording ("Spark needs Python <= 3.12 until pyspark 4") is false on Linux 3.13 by the measurement, so the line follows the CI evidence (question Q1 to the main thread).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | sr | AC2.2 | `tests/fixtures/f2_spark_generator_specs_right.py`, `tests/conftest.py`, `tests/AGENTS.md` | conditional: widen the skip predicate to the platform CI showed failing, reason names pyspark 3.5 and Python 3.13; the docstring lines of `conftest.py:7-9` and `tests/AGENTS.md:9` change with it. No test (fixture; evidence = the failing run id and the green run after). Cancelled with the reason "no 3.13 Spark leg failed in run <id>" otherwise. Owner test: none |
| J3.T2 | jr | AC2.4 | `docs/2_SPARK_GENERATOR.md` | one requirement line on the Spark page after "bring your own session" (`:3-4`), worded as CI shows; no other page changes. No test (prose). Owner test: `tests/test_docs.py` still executes the page's blocks, unchanged |
