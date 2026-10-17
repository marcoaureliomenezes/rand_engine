# PLAN — Release: 0.8.0, candidate 4 (stateless relations and output throughput)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-4/SPEC.md`

## 1. As-is review

The pre-SPEC investigation found zero open bugs, pending ADRs, or live audit
findings. The prior candidate's documentation-only repair is outside this tree;
the main thread syncs this definition after that repair lands.

| unit | today | bugs | verdict | why |
|---|---|---:|---|---|
| `core/_keys.py` `Keys` | owns stateless PK/FK values by contiguous offsets; FK always selects from `parent_size` | 0 | UPDATE | one shared eligible-parent and arbitrary-index helper can extend the existing pure key authority without a second Spark algorithm. |
| `validators/{method_specs,advanced_validator,common_validator}.py` | catalog owns key grammar; Advanced accepts keys and Common rejects them for Spark | 0 | UPDATE | the catalog and validators must accept the same bounded key grammar before either engine runs. |
| `main/_rand_generator.py` | passes offset, seed and column to `Keys` | 0 | KEEP | existing dispatch already carries every pandas key input; it needs no alternate generation path. |
| `main/spark_generator.py` | builds ordinary columns natively from `spark.range`, then drops technical `id` | 0 | UPDATE | add one vectorized adapter for key columns while retaining the native ordinary-column path. |
| `file_handlers/{writer,_writer_batch}.py` | file-only batch builder stages CSV, JSON and Parquet output | 0 | UPDATE | the existing builder is the sole SQLite entry point; staging and writer validation can carry its bounded transactional sink. |
| `main/data_generator.py` `stream_dict` | normalizes then calls pandas `to_dict("records")` | 0 | UPDATE | substitute Arrow only after unchanged normalization and only for representation failures. |
| `utils/stream_handler.py` | owns normalization and throughput sleep | 0 | KEEP | normalization and protected `StreamHandler` body stay exactly as released. |
| `tests/test_{8_consistency,1_advanced_validator,1_common_validator,3_spark_generator,5_files_write_batch,6_stream_objects,docs}.py` | current contract homes for keys, validation, Spark, batch output, streams and executable docs | 0 | UPDATE | each new contract hardens its existing seam; no current assertion is removed, skipped or weakened. |
| public docs, skill and docstrings | currently describe key refusal on Spark, file-only output and pandas record conversion | 0 | UPDATE | these are the established human/agent consumers of the changed behavior. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| accepted key grammar and builtin numeric input types | `METHOD_CATALOG` plus validator semantic rules | `AdvancedValidator`, `CommonValidator` | duplicated Spark key refusal |
| event-time eligibility and key reconstruction | `Keys` | pandas and Spark adapters | duplicated eligibility formula |
| pandas key dispatch and continuity | `RandGenerator` existing offset/key-seed call | `DataGenerator`, file/stream writers | none |
| Spark key output | `SparkGenerator` vectorized adapter over `Keys` | `spark.range` source indexes | xxhash approximation and any driver parent table |
| SQLite builder policy and transaction | `FileBatchWriter` | `FileWriter`, stdlib `sqlite3` | no sink or file-option reuse for SQLite |
| record representation conversion | `DataGenerator.stream_dict` after `StreamHandler.convert_dt_to_str` | PyArrow table conversion | unconditional pandas conversion for compatible batches |
| published behavior | final code and public docstrings | docs, skill, `llms.txt`, catalog atoms | stale Spark-key refusal claims |

`born_before` accepts only builtin `int` and `float`, excluding `bool`; no
Decimal, Fraction, or NumPy-scalar public promise is introduced. Its shared
authority computes the inclusive floor/clamp without accepting finite inputs
that overflow during generation.

### 1.2 Consumers and deletions

| changed surface | consumers | answer |
|---|---|---|
| FK eligibility | DataFrame, file parts, stream offsets and Spark key adapter | Job 1 |
| Spark key acceptance | `SparkGenerator`, validation tests, Spark guide and method inventory | Job 2 |
| SQLite batch format | `DataGenerator.write`, writer guides and executable docs | Job 3 |
| Arrow records | `stream_dict`, Kafka examples and stream tests | Job 4 |
| public guidance | docstrings, guides, skill, `llms.txt`, rendered navigation and memory | Job 5 and reconciliation |

## 2. Decisions and gate cost

- `Keys` remains the one key-value authority. Its new indexed helper is internal:
  `mapInPandas` supplies partition-local source row indexes and invokes it; no
  Spark hash, UDF/pandas_udF, random expression, capped cycle walk or parent table
  is introduced.
- SQLite uses only `sqlite3`, adjacent staging for overwrite and a single
  transaction for append. Identifiers are quoted and values are parameter-bound.
  No database handle crosses into generation.
- Arrow conversion first makes one cheap lossless-type decision for object cells,
  then catches only representation exceptions. It keeps scalar strings and dates,
  including the benchmark workload, on Arrow; it sends nested containers, NumPy
  arrays, custom objects and other unproved cells to pandas without comparing two
  complete conversions. It neither changes `StreamHandler` nor swallows unrelated
  errors.
- The existing `verify:` remains the only job gate. Its latest official rc-3
  worktree merge measured 1,155 passed, 8 deselected and 9 warnings in 115.42 s.
  Targeted RED evidence runs before a task merge; later worktree merge runs the
  unchanged full gate. No dependency, environment, workflow, benchmark or gate is
  added.
- The evolved worktree workflow is used as supplied. No hook, projection, law or
  dadaia-workspace code changes belong to this candidate.

## DAG

| job | waits on | wave | W: |
|---|---|---:|---|
| Job 1 | — | 1 | `tests/test_8_consistency.py`, `tests/test_1_advanced_validator.py`, `rand_engine/core/_keys.py`, `rand_engine/validators/method_specs.py`, `rand_engine/validators/advanced_validator.py` |
| Job 2 | Job 1 | 2 | `tests/test_1_common_validator.py`, `tests/test_3_spark_generator.py`, `rand_engine/validators/method_specs.py`, `rand_engine/validators/common_validator.py`, `rand_engine/main/spark_generator.py` |
| Job 3 | Job 1 | 2 | `tests/test_5_files_write_batch.py`, `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py` |
| Job 4 | — | 2 | `tests/test_6_stream_objects.py`, `rand_engine/main/data_generator.py` |
| Job 5 | Job 1, Job 2, Job 3, Job 4 | 3 | `tests/test_docs.py`, `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/reference.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md` |

Jobs 2 and 3 wait for Job 1 because they consume the shared key grammar;
Job 4 is independent. Job 5 waits for all behavior jobs because it owns the one
documentation-test seam and all public consumers. The only cross-job source-file
overlaps are ordered by those edges.

## 3. Reconciliation (after Jobs 1–5)

**W:** `CHANGELOG.md`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`,
`docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`,
`docs/explanation.md`, `docs/reference.md`, `llms.txt`, `skills/rand-engine/SKILL.md`,
`specs/backlog/BACKLOG.json`, `specs/backlog/_archive/backlog_histo.jsonl`,
`specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`,
`specs/memory/product/catalog.json`, `specs/memory/product/index.md`,
`specs/memory/product/relations/pk-fk-constraints.md`,
`specs/memory/product/generation/spark-generator.md`,
`specs/memory/product/generation/data-generator.md`,
`specs/memory/product/generation/generation-methods.md`,
`specs/memory/product/output/writers-and-streaming.md`,
`specs/memory/product/spec/rand-spec-grammar.md`,
`specs/memory/product/api/public-api.md`,
`specs/memory/product/onboarding/documentation.md`,
`specs/memory/product/quality/benchmarks.md`,
`specs/releases/0.8.0/_RELEASE.json`.

The product engineer runs the RC-FLOW closure: reconcile the final diff, refresh
affected docs/skill derived-from markers after atoms settle, regenerate the catalog,
record the CHANGELOG/closure summary, and exit exactly the four Origin entries as
delivered. `outreach` remains active. Existing memory, backlog, release and doctor
checks validate closure. A successful candidate-head benchmark is evidence only;
its artifacts are copied byte-for-byte only if available before closure.
