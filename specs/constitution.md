---
specs_pattern_version: 11
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

## Invariants

1. The public import surface is `DataGenerator`, `SparkGenerator` and `RandSpecs`; it changes only through an approved release, under semantic versioning.
2. A RandSpec is user input: the library never mutates or deletes a key of a spec it was given.
3. A spec that validates generates: a validator accepts only methods and parameters the target engine runs.
4. Seeded generation is reproducible; any change to seed behaviour revises this contract in an approved SPEC first.
5. A writer writes exactly what was asked — row count, format, compression and file count — and tests assert the output read back, not only that a write ran.
6. Credentials, PyPI or GitHub tokens, API keys and generated local state are never committed; PyPI publishing uses Trusted Publishing (OIDC) only.
7. Examples, templates, tests, fixtures and evidence use synthetic, sanitized or license-safe data only — never production data or PII.
8. The library holds no database state and runs no SQL; a database sink, if one is ever added, validates or quotes every spec-supplied identifier before it reaches the database.
9. Tests write output to pytest `tmp_path` or the workspace `.dadaia/tmp/`, never to a persistent directory in the repo tree.
10. The core generates data with Python, NumPy and pandas alone: Spark, Faker, a message broker or a database server is never required to generate data.
11. A runtime dependency, build tool, supported Python range or release mechanism changes only through an approved SPEC, with `specs/memory/ARCHITECTURE.md` `## Tech Stack` updated in the same change.

## Exclusions

- Not a correlation engine on a database: relations are stateless keys computed from the column definition, the seed and the row index; a database is only ever an output sink, never a lookup, and a sink needs its own approved SPEC and security review.
- Never ingests real data: no external table, example, test, log or template reads production data or PII.

<!-- dadaia:fixed slop-law -->
## Slop — workspace law (fixed)
- Slop is what passes the deletion test without loss: removed, no behavior changes and no decision loses its record.
- A SPEC declares scope, observable criteria and decisions in domain names; past the size `specs/releases/AGENTS.md` recommends, open `rc-<N+1>/`.
- A concept takes a glossary name; a numbered code exists only where a mechanical index reads it (FR, AC, T-).
- Every file has a canonical home and a GC path; summaries, backups, notes and scratch live in `.dadaia/tmp/` or do not exist.
- A branch dies at merge; a candidate exists only with scope that changes behavior.
- Measured by `.dadaia/.venv/bin/dadaia doctor` (FIXED-1/2); detection signals: `dd-code-review` SLOP.md.
<!-- /dadaia:fixed slop-law -->
