# SPEC — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** Approved
**Release ID:** 0.7.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-03
**Origin:** operator-demand

- Demand, operator 2026-10-03: fix PK/FK with few library changes, then docs and discoverability for humans and AI agents.
- Sources: the main-thread grill of 2026-10-03 (D1–D5, Visibility, Bugs); the as-is review (PLAN §1); the 0.6.4 audit and the market study of 2026-10-03.
- Bug history: the ledger held no record at definition; the audit's probe-confirmed defects drive the as-is verdicts.

## 1. Problem and context

- Relations in 0.6.4 are a wall-clock lookup into a process-global SQLite/DuckDB checkpoint: integer FKs come back as bytes, a PK does not make rows unique, `db_checkpoint` is a no-op, the spec loses `constraints` after one batch, FK correctness depends on scheduling, and no key crosses a process.
- The seed is process-global: `DataGenerator(..., seed)` resets the caller's NumPy state, and two generators interfere.
- The README's first examples fail as written; the package ships no licence; the PyPI summary still reads "Rand Engine v2".
- TPC-H/DS, PDGF and dbldatagen v1 derive keys from the row index; no maintained, permissive Python tool does it at NumPy speed for batch and streaming — rand-engine's lane (constitution, Purpose).

## 2. Objective

- Related tables are correct by construction — every key is a pure function of its column definition, the seed and the row index, with no database and no clock — and a newcomer, human or AI agent, reaches a working related-tables example from PyPI in one read.

## 3. Scope

### Terms

- **RandSpec**, **column spec**: memory `rand-spec-grammar`; a column spec is `{method, kwargs|args, cols?, transformers?}`.
- **Row index**: the 0-based position of a row in a generator's output. `get_df` and one batch `save` cover `[0, size)` on every call; a `save` over `numFiles` files splits that range into contiguous file ranges — file f covers `[c_f, c_f + n_f)`, `c_0 = 0`, `c_{f+1} = c_f + n_f`, the counter rule below applied to files, and a stream microbatch written to several files splits its range the same way. A stream's microbatch k covers `[c_k, c_k + n_k)`, `c_0 = 0`, `c_{k+1} = c_k + n_k`; with a constant size n, `[k·n, (k+1)·n)`.
- **Key column**: a column whose method is `pk` or `fk`.
- **PK column** (`pk`): row i's value is a pure function of the column's kwargs and i — never of the generator seed; unique by construction.
- **Key style**: `sequence` (`start + i·step`) or `permuted` (a bijection of the row index over a declared **domain**, shifted by `start`, depending only on `domain` and an optional `key`); `format` renders either as a string.
- **FK column** (`fk`): child row j's value is the parent PK value of a **parent index** `p(j) ∈ [0, parent_size)`, a pure function of the generator seed, the spec column name, the fk kwargs and j; the parent key is rebuilt, never looked up or stored.
- **Parent**: the PK column spec an FK names (`parent`) plus the parent row count (`parent_size`).
- **Skew**: one Zipf exponent over permuted parent ranks, so hot parents are scattered, not the first row indices; 0 (the default) means uniform.
- **rng**: the `numpy.random.Generator` a generator owns, built once from its seed and passed to the core as the keyword `rng`.
- _Avoid_ for relations: "checkpoint", "watermark", "references", "unique_ids" — retired by this candidate.

### Decisions

- Operator, grill 2026-10-03, verbatim answers:
  - D1 "Key methods in columns (Recommended)" — `pk`/`fk` in the column grammar; `fk` kwargs carry the parent PK column spec and the parent size; the `constraints` key is removed and its validator error points at the new methods.
  - D2 "Delete + backlog a key sink (Recommended)" — the checkpoint, its three handlers, `db_checkpoint`, `reset_checkpoint` and the `duckdb` dependency leave.
  - D3 "Out; backlog it (Recommended)" — `SparkGenerator` rejects `pk`/`fk`.
  - D4 "rng param per function (Recommended)" — one `np.random.default_rng(seed)` per generator, passed as `rng`; the global seed call leaves; same-seed values differ from 0.6.x (accepted).
  - D5 "sequence + permuted + format (Recommended)" — random-digit PKs are rejected.
  - Visibility "Lean, tested docs (Recommended)" — no docs site, no benchmark page.
  - Bugs "ALL confirmed" — the twelve independent defects are Arm B, outside this candidate (§5).
- Operator, rulings on this SPEC's open questions, 2026-10-03, verbatim answers:
  - Permuted keying "The pk kwargs only (Recommended)" — the bijection depends only on the pk definition (`domain`, optional `key`); FK ⊂ PK holds for any parent and child seeds, `seed=None` included.
  - Skew "Yes, one `skew` kwarg (Recommended)" — `skew` 0 is uniform (default); `skew` > 0 is Zipf over permuted ranks.
  - Event-time ordering "Backlog it (Recommended)" — deferred (§5).
- Settled by inspection, 2026-10-03: the version is 0.7.0 (grill Q2); `auto_tag_publish_master.yml` tags and publishes the `pyproject.toml` version from `master`, and past versions were hand-edited, so the bump is a requirement (AC9.4) and the pipeline mints tag and publish at promote.
- ADR 0002 (proposed) records the relations decision; only the operator accepts it (§6 names the paired constitution and memory hunks).
- Operator, approval 2026-10-03, verbatim: "Approve + AC10.4 + ADR 0002 (Recommended)" — the SPEC is approved with AC10.4 added, ADR 0002 is accepted, and the two inferred rules below are approved with it.
- Operator, rulings on the definition review (2026-10-03), verbatim:
  - "Bug: split size (Recommended)" — confirmed bug `writer-numfiles-rows-per-file`: `size` is the total row count of one `save`, split across `numFiles`; keys follow the file ranges (Row index, AC3.5).
  - "Mix the column name (Recommended)" — the FK parent-index draw hashes the spec column name with the seed and the fk kwargs (AC2.8).
  - "Build from rng bytes (Recommended)" — `uuid4` values are RFC 4122 v4 UUIDs built from the generator rng's bytes (FR4, AC4.5).
  - "Delete `.write.size()` (Recommended)" — the writer's own `size` leaves; the generator's `size` is the one row count.
- Operator re-approval of the amended trio, 2026-10-03, verbatim: "Re-approve all three (Recommended)".
- Operator demand, 2026-10-04, verbatim: "precisamos tirar os testes de stress. esse server não aguenta. vamos cria-los em jobs de CI. não precisamos ficar criando milhoes e milhoes de linhas aqui, ok?? testes devem ser leves. benchmarks deixaremos para etapa de CI." Settled by inspection: marker + CI job — the operator named CI jobs; the `stress` marker is the mechanism (AC10.5); every large-size AC is restated at ≤ 10^4 rows with the same property, its large size kept as a `Stress:` variant.
- Operator re-approval of the light-tests amendment, 2026-10-04, verbatim: "Re-approve (Recommended)".
- Inferred by the product engineer, approved with the SPEC:
  - A key is admitted only when the FK side can rebuild it from the column spec alone (D5's rule applied to every key input), so `transformers` on a `pk` column or an fk `parent` are rejected (AC1.7, AC2.6).
  - `DataGenerator.option` leaves with `reset_checkpoint`, its only key (AC5.3).

### FR1 — PK column (`pk`)

- kwargs only (no `args`): `style` (`sequence` | `permuted`), `start`, `step` (sequence), `domain` and `key` (permuted; `key` an optional integer), `format` (optional, a `str.format` template with exactly one replacement field). Defaults are the PLAN's.
- AC1.1 `{"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}` at size 10^4 yields exactly `1..10^4` in row order, integer dtype. Stress: size 10^6, `1..10^6`.
- AC1.2 `permuted`, `domain` 10^5, `start` 0, size 10^4: values unique, all in `[0, 10^5)`, not monotone in row index. Stress: `domain` 10^7, size 10^6.
- AC1.3 `permuted`, `domain` 10^15: the keys of row indices `0..10^4−1` and `10^15−1`, computed through the key function without building a frame, are unique and inside `[start, start + domain)` — no silent int64 overflow.
- AC1.4 `format` (e.g. `"C-{:08d}"`) over each style at size 10^4: string values unique. Stress: size 10^6.
- AC1.5 Two generators with the same kwargs and different seeds (one of them `seed=None`) yield identical PK columns, in one process and across two processes; a different `key` changes the `permuted` order.
- AC1.6 A `permuted` PK asked for row index ≥ `domain` raises a `RandEngineError` naming the column and the domain; no duplicate key is ever emitted.
- AC1.7 `SpecValidationError` for: an unknown `style` (the message lists `sequence` and `permuted`); `domain` < 1; a non-integer `key`; a `format` without exactly one replacement field; `args`; `transformers` on a `pk` column.

### FR2 — FK column (`fk`)

- kwargs only: `parent` (a `pk` column spec), `parent_size` (int ≥ 1), `skew` (float ≥ 0, default 0 = uniform).
- AC2.1 Integer keys: parent of 10^3 rows (once `sequence`, once `permuted`), child of 10^4 rows: every FK value ∈ the parent PK set. Stress: parent 10^4, child 10^6.
- AC2.2 String keys (`format` on the parent): every FK value ∈ the parent PK set.
- AC2.3 Parent written to Parquet by one Python process, child generated by a second process: every FK value ∈ the PK column read back.
- AC2.4 Uniform, 10^2 parents, 10^4 children: every parent index is referenced at least once. Stress: 10^3 parents, 10^6 children.
- AC2.5 `skew` 1.2, 10^3 parents, 10^4 children: the most-referenced 1% of parents receive ≥ 20% of children; uniform, ≤ 3%; fewer than half of the most-referenced 1% sit among the lowest 1% of parent indices; every FK value still ∈ the parent PK set. Stress: 10^4 parents, 10^6 children, uniform ≤ 2%.
- AC2.6 `SpecValidationError` for: `parent` not a `pk` column spec; `parent` carrying `transformers`; `parent_size` < 1; `parent_size` > the parent's `domain`; `skew` < 0; `args`.
- AC2.7 Parent and child generators on different seeds — integer vs integer, and `seed=None` on either side — and each style: every FK value ∈ the parent PK set.
- AC2.8 Two `fk` columns of one child spec with identical kwargs (same parent) yield different value sequences.

### FR3 — Keys across batches and streams

- AC3.1 1 batch vs N chunks, one generator: for k = 10 and size n, the PK and FK values of the first k·n records of `stream_dict` equal those of one `get_df` at size k·n; the same holds for 10 `writeStream` microbatches read back.
- AC3.2 PK values are unique across 10 microbatches of `stream_dict` and of `writeStream`.
- AC3.3 Two `get_df` calls on one generator return identical key columns.
- AC3.4 A streamed child's FK values ∈ the PK set of parent rows `[0, parent_size)`, whichever process generated them.
- AC3.5 One batch `save` with `numFiles` > 1: PK values are unique across all its files, read back; a child written in N files has every FK value ∈ the parent PK set.

### FR4 — One rng per generator

- `NPCore.gen_uuid4` builds its values from the generator rng's bytes, vectorised where possible; its signature and output format are kept.
- AC4.1 `np.random.get_state()` is identical before and after constructing a `DataGenerator`, `get_df`, one `stream_dict` microbatch and one batch `write`.
- AC4.2 Two generators with the same integer seed and spec return identical `get_df` frames, every NumPy-engine method included (`uuid4` too), on one machine.
- AC4.3 Generator A's `get_df` frame is unchanged when generator B (another seed) generates between A's construction and A's `get_df`.
- AC4.4 `git grep -nE 'np\.random\.(seed|rand|randn|randint|random|choice|uniform|normal|shuffle|permutation)\b' -- rand_engine` prints nothing; `Changer` is gone.
- AC4.5 Every `uuid4` value parses as a `uuid.UUID` with version 4 and the RFC 4122 variant.

### FR5 — The relations surface; the checkpoint leaves

- AC5.1 A spec carrying a top-level `constraints` key raises `SpecValidationError` whose message names `pk` and `fk`.
- AC5.2 A dict spec with `pk` and `fk` columns is deep-equal to a copy taken before `get_df`, a `stream_dict` microbatch and a batch `write` (constitution invariant 2).
- AC5.3 `DataGenerator` has no `db_checkpoint` and no `option` (its only key was `reset_checkpoint`); `import rand_engine.integrations` fails.
- AC5.4 `git grep -niE 'duckdb|sqlite|checkpoint|watermark|ConstraintsHandler' -- rand_engine pyproject.toml requirements.txt` prints nothing; `poetry.lock` holds no `duckdb` package.

### FR6 — Spark refuses keys

- AC6.1 `SparkGenerator` with a `pk` or an `fk` column raises `SpecValidationError` containing "NumPy engine only in 0.7.0" and naming `DataGenerator`.
- AC6.2 Every `SparkGenerator` spec valid in 0.6.4 without `pk`/`fk` still validates.

### FR7 — README on the identity

- AC7.1 The README's first section states the constitution's identity: sink-agnostic, NumPy-fast, Faker composes on top, related tables; the reviewer's product lens judges it against `specs/constitution.md` Purpose.
- AC7.2 Every `python` block of `README.md` executes in CI, in order, in a temporary directory; a block that raises fails the suite.
- AC7.3 The README shows, executed: one DataFrame, one Faker pool sampled at scale, one file write, one `stream_dict` loop, one related-tables pair whose block asserts FK ⊂ PK.
- AC7.4 The README carries no relative link (PyPI breaks them), every link targets a file in this tree or an external page, and no hand-written test count, coverage or timing figure.
- AC7.5 The README states the seed contract: per-generator, the caller's NumPy state untouched, values differ from 0.6.x.

### FR8 — Docs, recipes, `llms.txt`

- AC8.1 `docs/4_CONSTRAINTS.md` is rebuilt for keys: both styles, `format`, `fk`, `skew`, the row index in streams, the Spark refusal; it contains none of `constraints` (as a spec key), `watermark`, `checkpoint`, `references`.
- AC8.2 Short recipes — Faker pools, Kafka/queue, Parquet lake, related tables — live in `docs/5_RECIPES.md`.
- AC8.3 Every `python` block of each doc the README or `llms.txt` links executes in CI; the only exception is a block fenced `python no-run`, admitted only for a client outside the test dependencies (a Kafka producer), and that recipe still carries an executed block producing the records it sends.
- AC8.4 `llms.txt` at the repo root follows llmstxt.org: an H1 name, a `>` summary, H2 sections of `[title](url): note` links to the README, the docs, the recipes and the CHANGELOG; every link resolves to a file in this tree.

### FR9 — Licence and package metadata

- AC9.1 `LICENSE` at the repo root carries the MIT text with the author as copyright holder.
- AC9.2 The built distribution's metadata carries: licence MIT (`pyproject.toml` `license`); a summary stating the identity without "v2"; keywords; `License :: OSI Approved :: MIT License` among the classifiers; project URLs Homepage, Documentation, Repository, Issues, Changelog; `twine check` passes.
- AC9.3 `CHANGELOG.md` carries 0.6.1, 0.6.2, 0.6.3, 0.6.4 and 0.7.0; 0.7.0 lists every break: `constraints` removed, `pk`/`fk` added, `db_checkpoint` and `option` removed, Spark rejects keys, `duckdb` dropped, same-seed values differ from 0.6.x.
- AC9.4 `pyproject.toml` `version` is `0.7.0`, delivered by the last task of TASKS; tag and publish stay the project pipeline's, at promote.

### FR10 — Repo hygiene

- AC10.1 `tests/AGENTS.md` is calibrated for rand-engine from the audit draft, carries no `<…>` placeholder, and names no deleted test file.
- AC10.2 `git ls-files specs_bkp` prints nothing.
- AC10.3 No test imports a deleted module; the relation ACs (FR1–FR3, AC5.2) are asserted by contract tests in the file that owns relations, on the output read back, never on the run alone (constitution invariant 5).
- AC10.4 The repo `AGENTS.md` carries no checkpoint stop condition and no `integrations/` or `_constraints_handler.py` key path; it states that relations are stateless `pk`/`fk` columns.
- AC10.5 A default test run generates at most 10^4 rows per test. A test needing more carries the `stress` pytest marker, deselected by default in the `pyproject.toml` pytest configuration, and runs only in one dedicated GitHub Actions job (one OS, one Python) together with the benchmarks; no benchmark runs in the default suite. Each AC's `Stress:` variant is such a test.

## 4. Replaces

- `ConstraintsHandler` — PK rows inserted into `checkpoint_<name>` with a `creation_time`; FK columns overwritten by keys sampled from rows newer than a wall-clock watermark (→ FR1–FR3).
- The top-level `constraints` spec key (`tipo`, `fields`, `watermark`) and its validation (→ AC5.1).
- `SQLiteHandler`, `DuckDBHandler`, `BaseDBHandler`: the class-level connection pool and the process-shared `:memory:` checkpoint; the `duckdb` runtime dependency.
- `DataGenerator`: `np.random.seed(seed)` on the global state; `del spec["constraints"]` on the first call; `db_checkpoint(conn)`; `option("reset_checkpoint", True)` and `option` itself; one SQLite handler per instance.
- `Changer` (`utils/update.py`) and its `np.random.seed(None)` reseed — imported by `WebServerLogs`, never called.
- README: the `unique_ids`, `references`, `get_dfs`, multi-spec and `splitable` examples; six dead links; the MIT claim without a `LICENSE`; the 81.5 s benchmark and the hand-written test count.
- `docs/4_CONSTRAINTS.md`'s `constraints`/`references` guide.
- `specs_bkp/` — the tracked retire backup.
- Tests: `tests/integrations/test_sqlite.py`, `test_duckdb.py`, `test_constraints_cleanup.py`; `tests/test_8_consistency.py` with `tests/fixtures/f3_data_generator_constraints.py` (VARCHAR-only, watermark-timed, subset asserts commented out).

## 5. Out of scope

- Arm B, operator-confirmed, fixed in parallel bug worktrees — not tasks of this candidate: D5 writer size, D7 stream `timeout`/`trigger`, D8 `numFiles` consumed, D9 warnings raised as errors, D10 `integers.dtype`, D11 `distincts_external`, D12 timezone, D14 `int_type` overflow, D15 float bounds and Spark exclusive max, D17 dead CDC module, D18 unused dependencies (`fastavro`, `fastparquet`) and `PyCore`'s DuckDB import, D20 `uuid4` kwargs and `length`.
- Deferred to the backlog through the main thread's intake: Spark `pk`/`fk` parity; a DB key-sink writer (output only); an event-time-ordered FK (`born_before`).
- Not offered: composite keys, fan-out per parent, orphan or bad-data rates, hash-UUID keys, Spark seeding, a single method registry, a multi-spec container (`get_dfs`), a docs site, a benchmark page, Python 3.13/3.14 and pandas 3 support, CI security-scan hardening.

## 6. Dependencies and risks

- Order: FR4 (rng) and FR1–FR3, FR5, FR6 before FR7–FR8, whose examples call `pk`/`fk`; the README `write` example needs D5's fix merged first.
- Arm B fixes on the same units (`NPCore.gen_uuid4` D20, the writers D5/D7/D8, both validators D9–D11, `PyCore` D18) land on the work branch through bug worktrees; the PLAN's Parallel schedule orders this candidate's tasks around them.
- Constitution and Tech Stack: the ADR 0002 accept commit, at SPEC approval in this release worktree (an `impl` worktree cannot write `specs/`), carries the paired canonical hunks: invariant 8 rewritten (no SQL surface remains), Exclusion 1 rewritten (relations are stateless keys; a database is only ever an output sink), invariant 4 kept (this approved SPEC is the revision it requires), and `ARCHITECTURE.md` `## Tech Stack` without `duckdb`, `fastavro`, `fastparquet` (invariant 11).
- Memory pass at closure: `pk-fk-constraints` (rewritten for keys), `data-generator`, `rand-spec-grammar`, `spark-generator`, `generation-methods`, `public-api`; `ARCHITECTURE.md` Structure and Tech Stack; `QUALITY.md` Test architecture.
- Also at closure: `writers-and-streaming` (the writer `size` text leaves by ruling; `numFiles` now splits `size`); `ARCHITECTURE.md`'s frontmatter `summary` and `## Structure` still describe the checkpoint and are rewritten; the Tech Stack removal of `fastavro`/`fastparquet` anticipates the Arm B fix of D18.
- Constitution Exclusion 2 drops "persisted checkpoint" in its own commit (owner: `specs/AGENTS.md` canon table; no `### P-NN` statement, so no ADR).

| risk | mitigation |
|---|---|
| int64 multiplication overflows silently inside a permutation (measured on the prototype) | bounded arithmetic or Feistel cycle-walking; AC1.3 |
| a key drawn from the rng breaks chunk invariance | keys never read the rng; AC3.1 |
| users' seeded 0.6.x outputs change | the 0.7.0 CHANGELOG break list; AC7.5, AC9.3 |
| README examples drift again | executed in CI; AC7.2, AC8.3 |
| an Arm B fix and a task edit the same function | the Parallel schedule serialises them |

