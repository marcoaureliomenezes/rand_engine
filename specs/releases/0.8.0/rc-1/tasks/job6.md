# Job 6 — FR4 the get-started CLI

**Wave:** 3 · **Waits on:** Job 2, Job 4

- stdlib `argparse` only; `[tool.poetry.dependencies]` unchanged (AC4.7). `main(argv)` sits behind `if __name__ == "__main__"` in `__main__.py` (`test_every_shipped_module_imports` imports every `.py`).
- The five cases ship as `rand_engine/cases/<slug>.py.txt`, read with `importlib.resources`: a `.py` file would be executed by that import test, and the file name `test-data` is not an identifier. `get-started` writes the exact bytes as `DIR/<slug>.py`; the tutorials include the same file (J8), so the code of case N has one source.
- Slugs and order: `test-data`, `lake`, `kafka`, `databricks`, `faker`. Databricks source format: first line `# Databricks notebook source`, `# COMMAND ----------` separators.
- Tests run in-process (`main(argv)`, `exec` of the written file sharing the suite's Spark session: 0.85 s measured for 5 cases) plus ONE plain-python subprocess run of `test-data` (2.4 s). Added cost about 3.3 s (ruling 7).
- `list` and `--help` cost about 1.8 s (the package `__init__` imports numpy/pandas/pyarrow); accepted, no lazy-import work (ruling 8).
- `verify:` installs `--no-root`, so the console script is absent there: tests call `main(argv)` and `python -m rand_engine`; the wheel test checks the entry point.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | sr | AC4.1, AC4.2, AC4.3, AC4.4, AC4.7 | `tests/test_9_cli.py` | RED: `list` prints five slugs in order, exit 0, identical bytes; `get-started` writes exactly `DIR/<slug>.py` (DIR created), prints path; unknown slug / missing argument exit 2 with slugs on stderr; existing target unchanged, exit 1; `--help` lists every argument and slug; CLI imports only stdlib and `rand_engine`; no stdin read. Owner: tests/test_9_cli.py |
| J6.T2 | sr | AC4.1, AC4.2, AC4.3, AC4.4 | `rand_engine/cli.py`, `rand_engine/__main__.py`, `tests/test_9_cli.py` | argparse CLI: `list`, `get-started <slug> [--out DIR]`, slug table with descriptions, resource read, exit codes. Owner: tests/test_9_cli.py |
| J6.T3 | sr | AC4.5, AC4.6, AC4.8 | `tests/test_9_cli.py`, `tests/AGENTS.md` | RED: every written file is in Databricks format and executes (in-process; `test-data` once as a plain-python subprocess) writing only under tmp_path, <= 10^4 rows; `kafka` prints JSON lines with no broker/client; `lake` reads Parquet back and every `fk` joins a `pk`; `test-data` frame holds nulls and anomalies; `faker` runs with the extra; `databricks` skips where Spark tests skip. Adds the `test_9_cli.py` layout line to tests/AGENTS.md. Owner: tests/test_9_cli.py |
| J6.T4 | jr | AC4.5, AC4.6 | `rand_engine/cases/test-data.py.txt`, `tests/test_9_cli.py` | case: DataFrame for pipeline tests with `null_rate` and `anomaly_rate`. Owner: tests/test_9_cli.py |
| J6.T5 | jr | AC4.5, AC4.6 | `rand_engine/cases/lake.py.txt`, `tests/test_9_cli.py` | case: `pk`/`fk` related tables to a Parquet lake, read back. Owner: tests/test_9_cli.py |
| J6.T6 | jr | AC4.5, AC4.6 | `rand_engine/cases/kafka.py.txt`, `tests/test_9_cli.py` | case: event stream, JSON lines on stdout, producer block disabled by default. Owner: tests/test_9_cli.py |
| J6.T7 | jr | AC4.5, AC4.6 | `rand_engine/cases/databricks.py.txt`, `tests/test_9_cli.py` | case: native `SparkGenerator` notebook, note on `DataGenerator`-only features and the `spark.createDataFrame` path. Owner: tests/test_9_cli.py |
| J6.T8 | jr | AC4.5, AC4.6 | `rand_engine/cases/faker.py.txt`, `tests/test_9_cli.py` | case: Faker pools through `RandSpecs.faker_pool`, `pip install "rand-engine[faker]"`. Owner: tests/test_9_cli.py |
| J6.T9 | sr | AC3.2 | `tests/integrations/test_public_api.py` | RED: the built wheel declares the `rand-engine` console script (`rand_engine.cli:main`) and ships the five case files. Owner: tests/integrations/test_public_api.py |
| J6.T10 | jr | AC3.2, AC4.7 | `pyproject.toml`, `tests/integrations/test_public_api.py` | `[tool.poetry.scripts] rand-engine = "rand_engine.cli:main"`; dependencies untouched. Owner: tests/integrations/test_public_api.py |
