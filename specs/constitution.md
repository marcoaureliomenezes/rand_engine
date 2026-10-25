---
specs_pattern_version: 13
gitflow: {"principal": "master", "integration": "development", "work": "feature/"}
---
# Constitution — rand-engine

> **Created:** 2026-10-03

## Purpose

- rand-engine generates synthetic data very fast, from a declarative RandSpec, for anyone on any platform — batch and streaming.
- It is sink-agnostic: its output is meant for Kafka and other queues or streams, data lakes and object storage, files, databases and Spark.
- The core is Python + NumPy (`DataGenerator`); Spark is supported (`SparkGenerator`), never the center nor a requirement.
- Faker composes on top: users build small realistic value pools with Faker and rand-engine samples millions of rows from them at NumPy speed — a complement, not a dependency nor a competitor.
- It serves data engineers learning, stress-testing pipeline throughput and bandwidth, and feeding pipeline tests with synthetic datasets.

## Direction

Operator rulings of 2026-10-11, confirmed 2026-10-24: "Confirmo todas (Recomendado)"; north star: "Velocidade e nicho (Recomendado)".

- North star, for twelve months from 2026-10-24: rand-engine is the fastest Python generator of related synthetic data on a single node, NumPy and Arrow — a declarative spec becomes pk/fk tables, then files and streams.
- Speed ("velocidade") is rows per microsecond, the mean of a measured run; speed comes first, then resource efficiency.
- The NumPy single-node engine comes first; `SparkGenerator` gets nothing new.
- No new runtime dependency is added.
- No new method or key lands without a benchmark row at 1M and 10M rows.
- Benchmarks run only in CI.
- A generation method is touched only after seeded golden tests pin its values.
- Local tests stay light, as `specs/memory/QUALITY.md` `## Test architecture` states.

## Invariants

1. The public import surface is `DataGenerator`, `SparkGenerator` and `RandSpecs`; it changes only through an approved release, under semantic versioning.
2. A RandSpec is user input: the library never mutates or deletes a key of a spec it was given.
3. A spec that validates generates: a validator accepts only methods and parameters the target engine runs.
4. Seeded generation is reproducible; any change to seed behaviour revises this contract in an approved SPEC first.
5. A writer writes exactly what was asked — row count, format, compression and file count — and tests assert the output read back, not only that a write ran.
6. Credentials, PyPI or GitHub tokens, API keys and generated local state are never committed; PyPI publishing uses Trusted Publishing (OIDC) only.
7. Examples, templates, tests, fixtures and evidence use synthetic, sanitized or license-safe data only — never production data or PII.
8. Generation holds no database state and never reads a database or runs lookup SQL. An explicitly approved output-only database sink may execute SQL only to persist generated rows; it quotes every spec-supplied identifier and parameter-binds every value before either reaches the database.
9. Tests write output to pytest `tmp_path` or the workspace `.dadaia/tmp/`, never to a persistent directory in the repo tree.
10. The core generates data with Python, NumPy, pandas and PyArrow alone: Spark, Faker, a message broker or a database server is never required to generate data.
11. A runtime dependency, build tool, supported Python range or release mechanism changes only through an approved SPEC, with `specs/memory/ARCHITECTURE.md` `## Tech Stack` updated in the same change.
12. The function bodies released in v0.6.4 (the `gen_*` functions of `rand_engine/core/_np_core.py`, `_spark_core.py`, `_py_core.py`, and `StreamHandler`) are the operator's hand-written code: each changes only when the operator approves that function by name in the SPEC Origin, and the change keeps the operator's style (2-space indentation, one-line guards, terse NumPy). A SPEC REBUILD row alone never authorizes it; reviewers reject otherwise.
13. PyPI receives only closed releases, each published after the operator approves it through the GitHub environment `production`; no release candidate is published to PyPI, tagged or released on GitHub, and a release's tag is created only after its approved publish. The required-reviewer setting lives outside the repo and is held by the operator.

## Exclusions

- Not a correlation engine on a database: relations are stateless keys computed from the column definition, the seed and the row index; a database is only ever an output sink, never a lookup, and a sink needs its own approved SPEC and security review.
- Never ingests real data: no external table, example, test, log or template reads production data or PII.

<!-- dadaia:fixed slop-law -->
## Slop — workspace law (fixed)
- A SPEC declares scope, observable criteria and decisions in domain names; past the size `specs/releases/AGENTS.md` recommends, open `rc-<N+1>/`.
- A concept takes a glossary name; a numbered code exists only where a mechanical index reads it (FR, AC, T-).
- Every file has a canonical home and a GC path; summaries, backups, notes and scratch live in `.dadaia/tmp/` or do not exist.
- A branch dies at merge; a candidate exists only with scope that changes behavior.
- Slop is defined in `dd-code-review` SLOP.md; measured by `.dadaia/.venv/bin/dadaia doctor` (FIXED-1/2).
<!-- /dadaia:fixed slop-law -->
