# SPEC — Release: 0.7.0, candidate 1 (relations core + visibility)

**Status:** Draft
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

- Related tables are correct by construction — every key is a pure function of the seed and the row index, with no database and no clock — and a newcomer, human or AI agent, reaches a working related-tables example from PyPI in one read.

## 3. Scope

### Terms

- **RandSpec**, **column spec**: memory `rand-spec-grammar`; a column spec is `{method, kwargs|args, cols?, transformers?}`.
- **Row index**: the 0-based position of a row in a generator's output. `get_df` and `write` cover `[0, size)` on every call. A stream's microbatch k covers `[c_k, c_k + n_k)`, `c_0 = 0`, `c_{k+1} = c_k + n_k`; with a constant size n, `[k·n, (k+1)·n)`.
- **Key column**: a column whose method is `pk` or `fk`.
- **PK column** (`pk`): row i's value is a pure function of the generator seed, the column's kwargs and i; unique by construction.
- **Key style**: `sequence` (`start + i·step`) or `permuted` (a bijection of the row index over a declared **domain**, shifted by `start`); `format` renders either as a string.
- **FK column** (`fk`): child row j's value is the parent PK value of a **parent index** `p(j) ∈ [0, parent_size)`, a pure function of the generator seed and j; the parent key is rebuilt, never looked up or stored.
- **Parent**: the PK column spec an FK names (`parent`) plus the parent row count (`parent_size`).
- **Skew**: one Zipf exponent applied to the parent index; absent means uniform.
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
- ADR 0002 (proposed) records the relations decision; only the operator accepts it.
- A key style is admitted only when the FK side can rebuild it from the column spec alone (D5's rule applied to every key input).

### FR1 — PK column (`pk`)

- kwargs only (no `args`): `style` (`sequence` | `permuted`), `start`, `step` (sequence), `domain` (permuted), `format` (optional, a `str.format` template with exactly one replacement field). Defaults are the PLAN's.
- AC1.1 `{"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}` at size 10^6 yields exactly `1..10^6` in row order, integer dtype.
- AC1.2 `permuted`, `domain` 10^7, `start` 0, size 10^6: values unique, all in `[0, 10^7)`, not monotone in row index.
- AC1.3 `permuted`, `domain` 10^15: the keys of row indices `0..10^6−1` and `10^15−1` are unique and inside `[start, start + domain)` — no silent int64 overflow.
- AC1.4 `format` (e.g. `"C-{:08d}"`) over each style at size 10^6: string values unique.
- AC1.5 Two generators with the same integer seed and kwargs yield identical PK columns, in one process and across two processes.
- AC1.6 A `permuted` PK asked for row index ≥ `domain` raises a `RandEngineError` naming the column and the domain; no duplicate key is ever emitted.
- AC1.7 `SpecValidationError` for: an unknown `style` (the message lists `sequence` and `permuted`); `domain` < 1; a `format` without exactly one replacement field; `args`; `transformers` on a `pk` column.

### FR2 — FK column (`fk`)

- kwargs only: `parent` (a `pk` column spec), `parent_size` (int ≥ 1), `skew` (optional float > 0).
- AC2.1 Integer keys: parent of 10^4 rows (once `sequence`, once `permuted`), child of 10^6 rows, both generators on the same seed: every FK value ∈ the parent PK set.
- AC2.2 String keys (`format` on the parent): every FK value ∈ the parent PK set.
- AC2.3 Parent written to Parquet by one Python process, child generated by a second process with the same seed: every FK value ∈ the PK column read back.
- AC2.4 Uniform, 10^3 parents, 10^6 children: every parent index is referenced at least once.
- AC2.5 `skew` 1.2, 10^4 parents, 10^6 children: the most-referenced 1% of parents receive ≥ 20% of children; uniform, ≤ 2%; every FK value still ∈ the parent PK set.
- AC2.6 `SpecValidationError` for: `parent` not a `pk` column spec; `parent` carrying `transformers`; `parent_size` < 1; `parent_size` > the parent's `domain`; `skew` ≤ 0; `args`.

### FR3 — Keys across batches and streams

- AC3.1 1 batch vs N chunks: for k = 10 and size n, the PK and FK values of the first k·n records of `stream_dict` equal those of one `get_df` at size k·n; the same holds for 10 `writeStream` microbatches read back.
- AC3.2 PK values are unique across 10 microbatches of `stream_dict` and of `writeStream`.
- AC3.3 Two `get_df` calls on one generator return identical key columns.
- AC3.4 A streamed child's FK values ∈ the PK set of parent rows `[0, parent_size)`, whichever process generated them.

### FR4 — One rng per generator

- AC4.1 `np.random.get_state()` is identical before and after constructing a `DataGenerator`, `get_df`, one `stream_dict` microbatch and one batch `write`.
- AC4.2 Two generators with the same integer seed and spec return identical `get_df` frames, every NumPy-engine method included (`uuid4` too), on one machine.
- AC4.3 Generator A's `get_df` frame is unchanged when generator B (another seed) generates between A's construction and A's `get_df`.
- AC4.4 `git grep -nE 'np\.random\.(seed|rand|randn|randint|random|choice|uniform|normal|shuffle|permutation)\b' -- rand_engine` prints nothing; `Changer` is gone.

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

### FR10 — Repo hygiene

- AC10.1 `tests/AGENTS.md` is calibrated for rand-engine from the audit draft, carries no `<…>` placeholder, and names no deleted test file.
- AC10.2 `git ls-files specs_bkp` prints nothing.
- AC10.3 No test imports a deleted module; the relation ACs (FR1–FR3, AC5.2) are asserted by contract tests in the file that owns relations, on the output read back, never on the run alone (constitution invariant 5).

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
- Deferred to the backlog through the main thread's intake: Spark `pk`/`fk` parity; a DB key-sink writer.
- Not offered: composite keys, fan-out per parent, event-time ordering of children after parents, orphan or bad-data rates, hash-UUID keys, Spark seeding, a single method registry, a multi-spec container (`get_dfs`), a docs site, a benchmark page, Python 3.13/3.14 and pandas 3 support, CI security-scan hardening.

## 6. Dependencies and risks

- Order: FR4 (rng) and FR1–FR3, FR5, FR6 before FR7–FR8, whose examples call `pk`/`fk`; the README `write` example needs D5's fix merged first.
- Arm B fixes on the same units (`NPCore.gen_uuid4` D20, the writers D5/D7/D8, both validators D9–D11, `PyCore` D18) land on the work branch through bug worktrees; the PLAN's Parallel schedule orders this candidate's tasks around them.
- Constitution: this SPEC revises invariant 4's seed contract (per-generator rng, values differ from 0.6.x); invariant 8 and the first Exclusion lose their subject (no SQLite/DuckDB state remains).
- Invariant 11: the change dropping `duckdb` updates `specs/memory/ARCHITECTURE.md` `## Tech Stack` in the same change.
- Memory pass at closure: `pk-fk-constraints` (rewritten for keys), `data-generator`, `rand-spec-grammar`, `spark-generator`, `generation-methods`, `public-api`; `ARCHITECTURE.md` Structure and Tech Stack; `QUALITY.md` Test architecture.

| risk | mitigation |
|---|---|
| int64 multiplication overflows silently inside a permutation (measured on the prototype) | bounded arithmetic or Feistel cycle-walking; AC1.3 |
| a key drawn from the rng breaks chunk invariance | keys never read the rng; AC3.1 |
| users' seeded 0.6.x outputs change | the 0.7.0 CHANGELOG break list; AC7.5, AC9.3 |
| README examples drift again | executed in CI; AC7.2, AC8.3 |
| an Arm B fix and a task edit the same function | the Parallel schedule serialises them |

### Open questions — answered before `Approved`

1. Permuted keys and the seed: is a `permuted` permutation keyed by the generator seed (FK ⊂ PK only when parent and child share an integer seed; what does `seed=None` do for a `permuted` parent?) or by the PK kwargs alone (FK ⊂ PK for any seeds)? AC1.5, AC2.1–AC2.3 hold under both.
2. `skew`: carried as one optional parameter per the main thread's brief; the grill holds no operator answer on it.
3. The `pyproject.toml` version 0.6.4 → 0.7.0: which act moves it (the releases law: no agent mints a version)?
4. Constitution invariants 4, 8 and the first Exclusion: amended at closure by the memory pass, or in an operator act before implementation? Invariant 11 asks for Tech Stack in the task's own change, while atoms are written at closure.
5. Event-time ordering (a child references only parents already generated, the old watermark's intent): a third backlog entry, or dropped?
