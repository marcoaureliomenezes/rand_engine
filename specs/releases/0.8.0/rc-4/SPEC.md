# SPEC — Release: 0.8.0, candidate 4 (stateless relations and output throughput)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-17
**Origin:** backlog:spark-pk-fk-parity,db-key-sink-writer,event-time-ordered-fk,stream-dict-via-arrow

- Operator demand, 2026-10-17: finish every real open rand-engine item while
  adapting this repository and its child worktrees to the evolved dadaia-workspace;
  do not change dadaia-workspace.
- The mandatory refinement found zero open bugs, pending ADRs or live audit
  findings. It bounded the candidate's product behavior to the four technical
  backlog entries above.
- The same operator demand authorizes preparing a factual in-repository comparison
  page before stable 0.8.0 publishes the Pages site. This preparation avoids a
  later documentation-only release; it performs no external outreach act and does
  not deliver or exit the separate `outreach` entry, whose external work remains
  scheduled after stable publication.
- Approval also authorizes one narrow governance correction required by the
  output-only SQLite sink: constitution invariant 8 stops prohibiting SQL in the
  entire library and instead prohibits database state, reads and lookup SQL in
  generation. It permits an explicitly requested output sink to execute only
  quoted, parameter-bound output SQL. The constitution changes at reconciliation,
  after the approved behavior exists; no generation or key contract is relaxed.
- The concrete compatibility choices below are proposed defaults from repository
  inspection. They take effect only when the operator approves this SPEC and its
  PLAN.

## Bug window review

Rc-3 delivered documentation only and resolved no bug record. `BUGS.jsonl` is
unchanged across `c713b02..3e69edd`, reports zero open bugs, and introduces no
`fix_sha` after the rc-2 fixes already judged in rc-3's bug window. There is
therefore no fix to classify KEEP or REBUILD and no bug-window implementation work
in this candidate.

## 1. Problem

Four useful capabilities remain deliberately deferred:

- Relation keys are stateless and deterministic in `DataGenerator`, but
  `SparkGenerator` rejects `pk` and `fk`, so equivalent pandas and Spark pipelines
  cannot produce the same identifiers.
- An `fk` can select any declared parent. It cannot yet express that a child may
  reference only parents whose logical event time is no later than the child's.
- Batch output is limited to files. Users cannot write a generated frame to a
  local relational database through the existing writer builder, even though
  SQLite is available in the Python standard library.
- `stream_dict` normalizes each pandas frame and then converts it with
  `DataFrame.to_dict("records")`. Arrow can convert compatible batches faster, but
  some valid mixed object columns cannot be represented by Arrow and must retain
  the current result.

These changes must preserve the product's defining boundaries: keys remain pure
functions of definitions, seed and row index; generation never reads a database;
DataGenerator still needs only Python, NumPy and pandas to generate; existing
ordinary Spark methods do not acquire seeded semantics; and current record values
and types remain compatible.

## 2. Measurable goals

- The same explicit seed and key RandSpec produce bit-for-bit equal complete
  `pk`/`fk` vectors in `DataGenerator` and `SparkGenerator`, independently of Spark
  partition count.
- `born_before` deterministically limits every child key to an inclusively eligible
  parent and keeps the current one-batch/chunk/stream continuity contract.
- `.write.format("sqlite").option("table", name).save(path)` writes every generated
  column and row with atomic overwrite or transactional append semantics, quoted
  identifiers and bound values.
- Arrow-compatible `stream_dict` batches use Arrow after existing normalization;
  incompatible Arrow representations fall back to the current pandas conversion
  with exactly the current records.
- Public docstrings, human docs, the agent skill, CHANGELOG and product memory state
  the delivered behavior. Existing benchmark CI supplies performance evidence
  without a new gate or invented result.
- The stable documentation set includes a sourced capability comparison of
  rand-engine, Faker and dbldatagen without unsupported performance claims.

## 3. Non-goals

- Database-backed key lookup, checkpoint or watermark state; input/database
  ingestion; a database server; DuckDB, SQLAlchemy, callable sinks or a new public
  database API.
- A SQLite stream sink, database sharding, migrations, indexes, upsert/merge,
  schema evolution or file-only options on SQLite.
- Seeding ordinary Spark generation, changing any existing ordinary Spark value,
  exposing Spark's technical range id, or changing partition-dependent ordering.
- Per-row `F.udf`, pandas UDF, `F.rand`, a capped Feistel cycle walk or a driver-side
  parent table for Spark keys.
- Changing the protected v0.6.4 `gen_*` bodies or `StreamHandler`, the top-level
  `rand_engine.__all__`, the supported Python/Spark matrix, dependencies,
  workflows, benchmark code, release policy or dadaia-workspace.
- A break in `stream_dict` values, missing-value handling, date/datetime behavior,
  transformed mixed columns, ordering, timestamps or throughput controls.
- Competitive speed claims without a reproducible cross-tool protocol, a winner,
  aggregate score or unsupported cost/adoption claim; and external posts,
  Context7, awesome-list PRs, Discussions or conda-forge. The factual in-repository
  comparison in AC5.5 is included, while the separate `outreach` entry remains
  active until its post-publication external work is performed or otherwise
  dispositioned.

## 4. Requirements

### Terms

- **Logical event time:** for a row index `i`, `start + i / rate`.
- **Eligible parent:** parent index `p` whose Logical event time is less than or
  equal to the child row's Logical event time.
- **Key parity:** equal complete output values for the same explicit seed, RandSpec
  and row indexes; output order is compared by row index and does not redefine
  Spark ordering.
- **Arrow-compatible batch:** the already-normalized pandas batch passes a cheap
  lossless-type eligibility check and can be converted by
  `pyarrow.Table.from_pandas(..., preserve_index=False)` without an Arrow
  representation error. Typed numeric/boolean columns, nulls and scalar object
  values proved lossless by contract tests — including ordinary strings and dates
  used by the existing stream benchmark — are eligible. Nested containers, NumPy
  arrays, custom objects and other unproved object-cell representations are not,
  even when Arrow can encode them.
- **SQLite destination:** the database file passed to `save`; the `table` option
  selects the only table this save may replace or append.

### FR1 — Add stateless event-time eligibility to foreign keys

- AC1.1 (unit): `fk` accepts an optional `born_before` mapping with exactly
  `parent_start`, `parent_rate`, `child_start` and `child_rate`. Starts are finite
  builtin `int` or `float` values and rates are finite builtin `int` or `float`
  values strictly greater than zero. Booleans, missing/extra keys, non-mappings,
  non-finite values and non-positive rates are collected as validation errors
  before generation. No `Decimal`, `Fraction`, NumPy-scalar or other numeric input
  promise is introduced.
- AC1.2 (unit): for child row index `j`, the eligible count is the number of parent
  indexes in `[0, parent_size)` satisfying
  `parent_start + p / parent_rate <= child_start + j / child_rate`. Equivalently it
  is `floor((child_time - parent_start) * parent_rate) + 1`, clamped to
  `[0, parent_size]`. The inclusive boundary, clamp and arithmetic have one shared
  implementation; tests cover a parent born exactly at the child's time.
- AC1.3 (unit): the existing uniform or skew sampler selects only inside that row's
  eligible count, then reconstructs the declared sequence, permuted or formatted
  parent key exactly as today. If any requested child row has zero eligible
  parents, generation raises `RandEngineError` with the FK output column named.
  Omitting `born_before` preserves every current key value.
- AC1.4 (integration): explicit-seed output is deterministic across repeated calls
  for the same indexes, and a contiguous result equals the same indexes generated
  through uneven file parts, row batches and stream offsets. No clock, retained
  state, database or producer coordination participates.

### FR2 — Give Spark exact pandas key parity

- AC2.1 (unit): `SparkGenerator(spark, F, spec, seed=None)` accepts `pk` and `fk`
  through the catalog and shared key validation. With the same explicit seed, its
  key-seed derivation matches `DataGenerator`; the optional seed applies only to
  keys. Every ordinary Spark method remains unseeded and behaviorally unchanged.
- AC2.2 (integration): across at least two Spark partition counts, complete Spark
  vectors equal DataGenerator vectors for sequence, permuted and formatted primary
  keys; uniform and skewed foreign keys; non-default starts/steps and parent sizes;
  and `born_before`, including its inclusive boundary and zero-eligible error.
- AC2.3 (integration): Spark key calculation is a vectorized `mapInPandas` adapter
  over the authoritative NumPy `Keys` semantics and source row indexes. It works
  for arbitrary partition boundaries, uses no per-row Python UDF/pandas UDF,
  `F.rand`, fixed-cycle approximation or driver parent table, and exposes no
  technical helper column in the returned schema. Only row indexes and key columns
  cross that adapter; ordinary columns stay on their existing native Spark path.
- AC2.4 (unit and integration): malformed key grammar is refused during Spark
  validation by the same semantic authority used for pandas. Non-key Spark
  validation and generation remain green, the existing native `SparkCore` methods
  remain untouched, and `rand_engine.__all__` is unchanged.

### FR3 — Add an atomic, output-only SQLite batch sink

- AC3.1 (integration): the existing builder accepts only
  `.write.format("sqlite").option("table", name).mode(mode).save(database_path)`
  for SQLite, where `mode` is `overwrite` (default) or `append`. `table` is required
  and must be a non-empty string without NUL; all generated column and table names
  are safely quoted, including spaces, quotes and SQL-looking text.
- AC3.2 (integration): overwrite leaves the prior destination unchanged until a
  complete staged database transaction succeeds, then atomically replaces the
  destination. It replaces only the selected table's schema and rows while
  preserving unrelated tables in an existing database. A generation,
  transformation, conversion, SQL or commit failure preserves the complete prior
  destination and leaves no staging sibling.
- AC3.3 (integration): append creates a missing database/table or appends all rows
  to an existing table with the same ordered column contract. A schema mismatch or
  any failed row rolls back the whole append and leaves prior rows unchanged.
  Overwrite and append both preserve the requested total row count and generated
  values. Python/NumPy integers and booleans use SQLite INTEGER, floats use REAL,
  strings use TEXT, bytes use BLOB, missing values use NULL, and date/datetime
  values use their ISO text representation; a value outside this bounded mapping
  is refused before commit.
- AC3.4 (unit and integration): row values are always parameter-bound rather than
  interpolated into SQL. Hostile-looking identifiers and values round-trip through
  `sqlite3` under `tmp_path` without executing additional SQL. Generation never
  receives a database connection and never reads keys from the destination.
- AC3.5 (unit): SQLite explicitly refuses `numFiles`, `maxRowsPerBatch`,
  `compression` and other file-only options, unsupported modes, and every
  `writeStream.format("sqlite")` attempt before touching output. It adds no runtime
  dependency, server, public export or state subsystem.

### FR4 — Use Arrow for compatible record streams without a contract break

- AC4.1 (integration): after the unchanged `StreamHandler.convert_dt_to_str`
  normalization, an Arrow-compatible batch is converted through
  `Table.from_pandas(..., preserve_index=False).to_pylist()`. Ordinary scalars,
  nullable integer/boolean/float columns, nulls, dates, normalized datetimes,
  transformed safe scalar columns and `timestamp_created` have exactly the current
  Python values and types. The ordinary string-heavy workload measured by the
  existing `stream_dict` benchmark remains eligible for this Arrow path.
- AC4.2 (integration): a batch that fails the lossless-type eligibility check, or
  raises a narrow Arrow representation error such as
  `ArrowInvalid`/`ArrowTypeError`, uses the existing
  `DataFrame.to_dict("records")` conversion. Real tuple, NumPy-array and mixed
  object partitions prove the fallback preserves their current values and Python
  types even where Arrow could encode them by changing representation. The guard
  may inspect object-column cell types cheaply; it does not run both complete
  conversions for an eligible batch, swallow unrelated exceptions, add a public
  flag/framework or change `StreamHandler`.
- AC4.3 (integration): record order, infinite iteration, resolved size, throughput
  bounds, batch cadence, transformer/modifier behavior and timestamp insertion
  remain unchanged. Existing `stream_dict` tests stay green without weakening or
  skipping an assertion.
- AC4.4 (no new test; the existing same-runner A/B benchmark already measures the
  one-million-row `stream_dict` sink): the candidate-head benchmark job must pass
  its existing limits and publish its `stream_dict` row. No workflow, benchmark
  script, dependency or performance gate is added.

### FR5 — Keep public guidance, evidence and product truth synchronized

- AC5.1 (unit and executable documentation): public API docstrings, human guides
  and `skills/rand-engine/SKILL.md` describe the exact `born_before` mapping,
  Spark seed/key parity, SQLite builder/modes/options/refusals and Arrow fallback.
  Examples are synthetic, use at most 10^4 rows, write only to temporary paths and
  execute through existing test homes.
- AC5.2 (unit): the method/engine and writer option inventories remain derived from
  their code authorities. `llms.txt` and the rendered reference/navigation expose
  the changed guides without a new export pipeline or new public import.
- AC5.3 (no new test; evidence is copied and compared byte-for-byte): if a
  successful candidate-head CI run emits a replacement benchmark artifact before
  closure, `docs/BENCHMARKS.md` and `docs/benchmarks.json` are refreshed only from
  that artifact and cite its run/head. If the final run exists only after closure,
  its Actions/PR result is the evidence and no source artifact is fabricated.
- AC5.4 (no new test; existing memory catalog, drift and release checks): closure
  updates `specs/constitution.md`, replacing invariant 8 with: "Generation holds no database state and
  never reads a database or runs lookup SQL. An explicitly approved output-only
  database sink may execute SQL only to persist generated rows; it quotes every
  spec-supplied identifier and parameter-binds every value before either reaches
  the database." Closure then reconciles `pk-fk-constraints`,
  `spark-generator`, `data-generator`,
  `writers-and-streaming`, `rand-spec-grammar`, `generation-methods`, `public-api`,
  `documentation` and `benchmarks` as changed or reviewed from the final diff;
  refreshes every affected docs/skill consumer marker; updates ARCHITECTURE and
  QUALITY only where repository truth changed; records CHANGELOG; and exits only
  the four delivered Origin backlog entries.
- AC5.5 (unit and existing strict docs build): `docs/comparison.md` presents a
  factual capability table for rand-engine, Faker and dbldatagen using primary
  official sources for each tool's execution model, output surface, required data
  source, relationship/repeatability scope and deployment scope. It explains that
  the tools serve overlapping rather than identical use cases; links rand-engine's
  existing internal same-runner A/B benchmark methodology and results; and states
  that those results are not a Faker/dbldatagen speed comparison. Existing
  navigation and `llms.txt` expose the page. It publishes no invented competitor
  measurement, winner, score, dependency, benchmark, workflow or gate.

## 5. Replaces

- The unconditional `parent_size` FK selection remains the default and gains the
  optional row-dependent `born_before` eligibility bound; no-state key semantics
  replace no existing behavior.
- Spark's `pk`/`fk` refusal is replaced by exact DataGenerator key parity through a
  vectorized partition adapter; all other current Spark refusals and native method
  behavior remain.
- Arrow-compatible `stream_dict` batches replace pandas record conversion with
  Arrow conversion; incompatible batches retain the existing pandas path and
  output contract.
- No database writer is replaced. SQLite is added as one batch format on the
  existing builder, bounded to one output table and the standard library.
- Constitution invariant 8's library-wide "runs no SQL" wording is replaced by
  the narrower generation/key-state prohibition and the explicitly bounded
  output-SQL permission in AC5.4; every no-read, no-lookup and SQL-safety guarantee
  remains.

## 6. Constraints, risks and approval choices

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — shared relation foundation | catalog-owned `born_before` grammar, inclusive eligibility and stateless NumPy behavior | AC1.1–AC1.4 |
| 2 — independent product paths | Spark key parity after wave 1; SQLite batch output and compatible Arrow records may proceed independently | AC2.1–AC4.3 |
| 3 — promote-facing evidence | public docstrings, human/agent guidance, factual comparison page, existing CI benchmark evidence and closure reconciliation | AC4.4, AC5.1–AC5.5 |

| risk | control |
|---|---|
| floating event-time boundaries select one parent too many or too few | one inclusive eligible-count authority; exact-boundary, before-first-parent and parent-size-clamp tests |
| Spark partitioning changes key values | index-based authoritative `Keys` adapter; complete-vector parity over multiple partition counts |
| executor conversion introduces a second key implementation | `mapInPandas` calls the shared key semantics; no Spark hash approximation |
| SQLite identifiers or values become SQL | quote every identifier, bind every value, and test hostile-looking round trips |
| a failed SQLite write damages an existing database | adjacent staged overwrite and single-transaction append, each with failure mutation tests |
| SQLite delivery leaves constitution invariant 8 false | approval includes the exact AC5.4 replacement; reconciliation updates `specs/constitution.md` with the delivered sink |
| Arrow changes a Python record or masks a real error | existing normalization first, representative exact equality, narrow Arrow-only fallback |
| rc-4 races the rc-3 integration PR | definition may be reviewed now; rc-4 is neither merged nor pushed ahead of the completed rc-3 PR |

Approval of this Draft confirms these concrete choices: compatibility fallback for
Arrow instead of either previously suspected break; SQLite only through the
existing batch builder; the explicit four-field `born_before` mapping and
zero-eligible refusal; and vectorized `mapInPandas` over authoritative key
semantics for Spark. It also confirms the exact invariant 8 replacement in AC5.4,
which permits bounded output SQL without permitting database state, reads or
lookups in generation. No other product question remains.
