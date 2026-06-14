# Backlog candidates

Surfaced issues awaiting operator triage into approved releases. Newest first.

## FEAT-RAND-CORR-01 - DuckDB-backed correlation engine design

**Reported:** 2026-06-05 audit fan-out and operator restart request.

**Surface:** RandSpec grammar, DataGenerator, DuckDB integration, constraints,
tests, docs.

**Problem:** DuckDB is checkpoint/state infrastructure today, not a correlation
engine. The next product direction needs a first-class correlation model before
code changes.

**Required decision:** Is DuckDB the canonical engine for correlations,
constraints, or both? Define grammar, external sources, query safety,
persistence, deterministic sampling, Pandas/Spark boundaries, and performance
acceptance.

## BUG-RAND-CHECKPOINT-01 - `checkpoint()` does not rewire active constraints handler

**Reported:** 2026-06-05 software-architect and software-engineer-python audits.

**Surface:** `DataGenerator.checkpoint(db_path)` and constraints persistence.

**Defect:** `checkpoint(db_path)` changes a stored path but does not recreate or
reconfigure the already-instantiated constraints handler.

**Suggested fix:** Move constraints handler creation after checkpoint selection
or rebuild/inject the handler when checkpoint is called. Add file-backed
checkpoint tests.

## BUG-RAND-SPECMUT-01 - DataGenerator mutates input specs

**Reported:** 2026-06-05 software-engineer-python audit.

**Surface:** `DataGenerator.get_df()` internal spec handling.

**Defect:** The generator deletes `constraints` from an evaluated spec dict,
which can mutate user input and remove consistency behavior on later calls.

**Suggested fix:** Copy evaluated specs before removing internal keys. Add a
regression test that the original spec remains unchanged across repeated calls.

## BUG-RAND-DISTINCTS-EXTERNAL-01 - `distincts_external` validates but is not implemented

**Reported:** 2026-06-05 software-architect and software-engineer-python audits.

**Surface:** `AdvancedValidator`, Pandas runtime method map, future DuckDB
correlation work.

**Defect:** A RandSpec can pass validation and then fail at generation because
the runtime has no mapped method.

**Suggested fix:** Either remove/disable validation until implemented or
implement it under an approved DuckDB correlation/store design with tests.

## BUG-RAND-SPARK-ADV-01 - Spark advanced methods are null stubs

**Reported:** 2026-06-05 audits.

**Surface:** `SparkGenerator`, `_spark_core.py`, validators, docs.

**Defect:** Advanced Spark methods are mapped but return null placeholders.

**Suggested fix:** Treat advanced Spark methods as unsupported with explicit
validation/runtime errors, or implement Spark-native semantics under an approved
release.

## BUG-RAND-CDC-01 - CDC generator appears stale and untested

**Reported:** 2026-06-05 Python and QA audits.

**Surface:** `rand_engine/main/_cdc_generator.py`.

**Defect:** The module imports stale paths/symbols and is not covered by the
test suite.

**Suggested fix:** Classify CDC as supported, deprecated, or removed. Add import
smoke coverage for every packaged module.

## GOV-RAND-RELEASE-01 - Version and release truth conflict

**Reported:** 2026-06-05 DevOps and QA audits.

**Surface:** `pyproject.toml`, README, PyPI, GitHub releases, CI release flows.

**Problem:** Stable source/PyPI/GitHub are `0.6.3`, remote/PyPI/GitHub
prerelease is `0.6.4rc1`, and README advertises `0.7.0`.

**Required decision:** Promote/finalize `0.6.4rc1`, discard it, or start a new
base version. Align README, changelog, package metadata, GitHub releases, and
runtime version policy.

## QA-RAND-GATES-01 - Quality gates are strong locally but weak as release policy

**Reported:** 2026-06-05 QA and DevOps audits.

**Surface:** CI, pytest, coverage, security scans, lint/type tooling.

**Problem:** The suite is green, but security jobs can be advisory, coverage
thresholds conflict, no lint/type gate is configured, and writer/correlation
tests need stronger behavior assertions.

**Suggested fix:** Define required gates before implementation resumes:
pytest matrix, coverage threshold, package build/install, import smoke, writer
read-back checks, DuckDB lifecycle tests, lint/type policy, and hard security
scan behavior.
