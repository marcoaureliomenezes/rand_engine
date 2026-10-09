# PLAN — Release: 0.7.0, candidate 2 (bounded generation + RandSpec breadth)

**Status:** Approved
**Release ID:** 0.7.0
**Owner:** dd-software-engineer
**SPEC:** `specs/releases/0.7.0/rc-2/SPEC.md` at approved commit `86c5a33580529bca61397bb688b1fbd9ff97ddf8`.

## 1. As-is review

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `validators/common_validator.py` intake | common kwargs table plus semantic branches that continue after type errors | `probability-wrong-type-escapes-validation`; registry/schema family | REBUILD | Fundamental intake behavior changes; structure and type validity must gate semantics once. |
| `validators/advanced_validator.py` intake | repeats common structure; mapped pools permit empty domains; refuses `args` | `distincts-map-empty-pool-validates`, `distincts-multi-map-empty-domain-validates`; registry/schema family | REBUILD | Repeated fixes and the approved kwargs-only migration make additive guards another bug loop. |
| `validators/method_specs.py` integer semantics | `_integers` validates `int_type` but accepts an inverted `min`/`max` domain | schema-validation family | UPDATE | Normal validation must reject `min > max` at the catalog authority while retaining equal and ordered domains without a new ceiling. |
| `core/_np_core.py` numeric methods | continuous float draw then rounding; one owned RNG | `float-rounded-domain-violates-bounds`; prior bounds/dtype family | REBUILD | Generate over the representable decimal lattice, add the four distributions and constant, and preserve one RNG. |
| `core/_py_core.py` `METHODS` | sole NumPy dispatch map plus correlated implementations | registry and mapped-pool family | UPDATE | Keep one implementation map, add real callers, and delete commented implementation; do not layer another dispatch path. |
| `core/_spark_core.py` numeric methods | integer result arithmetic passes through double; floats round after draw | `spark-bigint-precision-lost`; prior Spark numeric/date family | REBUILD | Exact result arithmetic and honest supported domains are fundamental; preserve UTC fixes and no Python UDF. |
| `main/_rand_generator.py` | column generation and embedded transformers; global transformers live above it | registry family | REBUILD | One post-transform modifier step must own anomaly then null application; delete dead `validate` and unused Spark import. |
| `main/data_generator.py` | owns RNG/seed, global transformers and DataFrame factory | writer-size family | REBUILD | One row-batch pipeline must enforce row-count preservation and the approved ordering without a second generation path. |
| `file_handlers/_writer_batch.py` | splits total rows by file, builds lazy factories, computes offsets quadratically, generates each file whole | writer size/numFiles/state family | REBUILD | Replace with one linear lazy plan, cumulative offsets and bounded same-filesystem staging. |
| `file_handlers/file_handler.py` | one-shot CSV/JSON/Parquet adapters; Arrow schema inferred independently per call | writer options and Windows timezone family | REBUILD | Existing three adapters must hold per-file append state and validate stable schemas while preserving timezone rendering. |
| `file_handlers/_writer_stream.py` | one size-row microbatch per emitted file with cumulative offset | writer state/size family | KEEP | It is already row-bounded; the SPEC explicitly excludes `writeStream` from `maxRowsPerBatch`. |
| `tests/fixtures/f3_integrations.py` writer paths | module-autouse fixture creates and recursively removes persistent `tests/test_outputs` | writer fixture debt | UPDATE | AC8.6 requires pytest-owned temporary output; the repair belongs in GREEN after an assertion-first tests-only RED. |
| `examples/common_rand_specs.py` (`RandSpecs`) and packaging | ten fixed specs; Faker is test-only | none | UPDATE | The existing exported class carries two helpers without a new public class; Faker becomes an optional extra, never core. |

Test debt is part of the rebuild: consolidate duplicate-name NumPy tests so Python cannot discard parameter tables, and move writer fixtures to `tmp_path`. `SparkGenerator`, stateless keys, correlated output order, the public three-name export and unbatched call cadence stay unless an approved AC replaces them.

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| accepted method names, kwargs, defaults and engine support | one method catalog replacing both validator tables | NumPy/Spark implementation maps | duplicated validator registries and free-running semantics |
| NumPy implementation dispatch | `core/_py_core.py` `METHODS` | method catalog set-equality test | any second NumPy dispatch path |
| structural/type/semantic validation order | `AdvancedValidator.validate` delegating catalog-driven column validation | method catalog | semantic checks on invalid values |
| integer `min`/`max` validity | method catalog `_integers` semantic validator | `AdvancedValidator`, `DataGenerator` and `RandSpecs.from_schema` callers | helper-local range checks and generation-time failure for accepted inverted domains |
| RNG state and row-batch execution order | `DataGenerator.wrapped_df_generator` | `RandGenerator` | dead validation switch and hidden reseeding |
| ordinary-column anomaly/null policy | `RandGenerator` post-transform step | validated column metadata and DataGenerator RNG | modifiers on keys/correlated methods |
| Arrow/Faker RandSpec construction | `RandSpecs.from_schema` and `RandSpecs.faker_pool` | PyArrow types and optional Faker | business inference, global Faker seed, second generator |
| total rows/files/batches/offsets | `FileBatchWriter` private linear plan | DataGenerator size resolver | `sum(sizes[:f])`, eager DataFrame collections |
| writer test output location | pytest `tmp_path` supplied to `tests/fixtures/f3_integrations.py` | writer integration tests | persistent `tests/test_outputs` creation and recursive repo cleanup |
| format append/schema/compression state | existing `FileHandler` CSV/JSON/Parquet adapters | writer plan | reopening a destination for each batch |
| Spark exact integer expression | `SparkCore.gen_ints` | catalog dtype/range validation | double result arithmetic |
| representable decimal domain | one pure core decimal-lattice helper used by both engines and delegated to by catalog validation | float generators | copied validator-domain calculations, clipping and sample-value branches |

### 1.2 Bug-window disposition coverage

The SPEC's 25-row review is binding. The rebuild jobs preserve all assertions behind its 18 REBUILD verdicts: writer options/size/state/numFiles/CSV timezone; validator warnings/schema/defaults/registry/arity; NumPy timezone/dtype/float bounds; Spark inclusive integers, timezone, empty date and inverted float domains; category-first correlated output. Its seven KEEP results remain untouched: shell-safe CI summary, deleted CDC, anchored memory ignore, removed runtime dependencies, valid advanced examples, advisory Codecov and the portable date oracle. The five open RC2 bugs close only after their independent RED owners are green; ledger lineage is not rewritten.

## 2. Design

### 2.1 One intake and one method catalog

- Replace `CommonValidator.METHOD_SPECS` and `AdvancedValidator.METHOD_SPECS` with one small catalog under `validators/`; it records required/optional kwargs, defaults, engine support, ordinary/correlated/key kind and semantic validator. It is metadata, not a new generation engine.
- `AdvancedValidator` owns whole-RandSpec intake and issue collection. It validates shape and types first; semantic functions receive only typed values. `CommonValidator` is the Spark-facing adapter over the same catalog and refuses unsupported methods/modifiers before `SparkGenerator` builds a frame.
- One shared typed-intake seam under `CommonValidator` consumes catalog metadata for required, optional, type, unknown and semantic checks. After J1.S2 establishes the catalog/common path, sequential J1.S3 rebuilds that seam and makes `AdvancedValidator` delegate to it before adding correlated/key shape rules; no parallel task shares either validator file.
- J1.S4/J1.S5 own the additional-review regressions and corrections after that rebuild: preserve executable legacy float/normal decimal and infinity behavior (except invalid negative std), make new-distribution numeric predicates total for accepted Python numeric types, and reuse one declared-scalar predicate for constant and anomaly structure. After GREEN, the repeated J1.S2 additional checkpoint must approve before the close task; terminal `done`, the official Stage J1.S5 gate and its closing trailer establish the complete closing HEAD that the final Job 1 review binds before canonical merge. No bug record closes at the intermediate checkpoint.
- Diagnostics name fields, options and existing key-path identifiers. The mapped-arity key-path diagnostic remains, but collection contents, pairs, items and input value payloads are never dumped.
- Keep `core/_py_core.py` `METHODS` as the NumPy callable map used by ordinary columns and nested templates. A contract test requires catalog NumPy names to equal this map plus `pk`/`fk`. The Spark map equals catalog entries with Spark engine support plus correlated-kind entries retained by the legacy warning-and-NULL adapter; that compatibility path is not full Spark support. No third registry, manual expected-name list or fallback dispatch survives.
- J2.S1.T1/J2.S2.T1 own that contract in `tests/test_1_advanced_validator.py`: expected NumPy names come from catalog engine metadata, while expected Spark names come from Spark engine metadata plus correlated kind for the preserved legacy adapter. This replaces the prior equal-engine-set assumption while retaining the existing name, parameter and signature checks.
- The approved `args` removal is one early collected issue naming `kwargs`; generation reads only `kwargs`.
- Job 7 is the corrective prerequisite for the existing normal-validation contract: J7.S1 exercises the public `AdvancedValidator`/`DataGenerator` boundary with an inverted integer range plus literal equal and ordered controls, then J7.S2 adds the single `_integers` catalog semantic and deletes only its satisfied RED marker. It rejects only `min > max`; it adds no integer-domain ceiling or helper-specific rule. Job 7 opens from the current feature after Jobs 1 and 2, then merges before the clean paused J4.S3.T1 helper tree is rebased and that task resumes. Already-authorized, disjoint J4.S3.T2 packaging work continues independently.

### 2.2 Numeric domains and new methods

- Convert float bounds with `Decimal(str(value))`. For decimals `d`, compute integer endpoints `ceil(min*10**d)` and `floor(max*10**d)`, refuse only an empty lattice, draw inclusive lattice integers, then divide by the scale. NumPy and Spark share the endpoints, not an implementation wrapper. The common int64-sized case stays vectorized; a wider finite lattice uses unbiased rejection from enough owned-RNG raw 64-bit limbs into Python integers before conversion to the approved float64 output. No new decimals ceiling or int64-only public-domain refusal is introduced for implementation convenience.
- J2.S1.T1 owns public constructor RED cases for empty/invalid numeric lattices while retaining legacy negative decimals. J2.S2.T1 owns the catalog file with the NumPy core so validation delegates to that pure helper instead of copying domain arithmetic; Spark remains a disjoint J2.S2.T2 consumer of the same endpoints.
- `NPCore` adds direct vectorized calls to the owned RNG for exponential, lognormal, poisson and zipf, with the SPEC defaults/dtypes. Rounding uses the declared decimals after the distribution draw. `constant` broadcasts an immutable approved scalar without touching RNG.
- Preserve existing uniform/normal goldens except the declared uniform-float lattice change. Consolidated test tables keep every useful original bound, timezone, dtype, categorical and normal assertion. J2.S2.T1 also owns the existing `tests/test_2_data_generator.py` seeded-output table narrowly enough to replace the one approved uniform-float hash and add the five new method hashes; its existing catalog/map coverage assertion remains unchanged. This is GREEN ownership of expectations that become red only after the approved registry expands, not a new behavior or corrective stage.
- The integrated NumPy path still formats a wide lattice integer as a decimal string before float conversion, so accepted `decimals=5000` singletons cross CPython's 4,300-digit safety limit. J2.S3.T1 owns assertion-first strict-xfail RED only for the independently verified positive-decimal cases that build those oversized integers; the already-green `decimals=-308` finite singleton and `decimals=-5000` zero singleton remain unmarked assertions, alongside low ambient Decimal precision and unchanged process digit-limit preservation. J2.S4.T1 reuses the existing exact Decimal tuple shift to apply `-decimals` directly to `Decimal(integer)` before float conversion; it adds no global switch, string conversion, context arithmetic or hidden decimals ceiling, and leaves the vectorized common path untouched. The diagnosed conversion passed all six signed-scale singleton probes under precision 2 and reproduced the prior seeded 1,000-row wide-domain bytes exactly (`ee024755131895b17e118517ac64a8cf81058c7258f74b470624a81f2e7a7714`). These corrective stages are required only to keep RED and GREEN write sets disjoint; they correct the existing AC8.3/AC9.1 Job 2 envelope and add no feature or AC.

#### Spark wide integers

Spark validates the logical dtype before expression construction: signed int8/16/32/64 and uint8/16/32 bounds must fit both their logical domain and the signed Spark carrier; `uint64`, bools and out-of-domain endpoints are refused.

For a non-constant width `w = max-min+1 <= 2**64`, construct three independent native 32-bit limbs as separate `floor(rand() * 2**32)` expressions. SparkGenerator has no seed today, so this retains its documented unseeded semantics; no same-seed lane reuse is introduced. Each limb is exactly representable in double, then cast to `Decimal(10,0)`. Cast `w` to `Decimal(20,0)` and reduce during the fold so Spark's inferred arithmetic precision stays below 38:

```text
hi_mod = cast(pmod(limb0 * decimal10(2**32) + limb1, decimal20(w)) as decimal(20,0))
word_mod = pmod(cast(hi_mod * decimal10(2**32) + limb2 as decimal(32,0)), decimal20(w))
value = decimal20(min) + word_mod
```

The first multiply/add has inferred precision at most 22 and the second at most 32; the fold is algebraically the same as reducing the full 96-bit word, without constructing a `Decimal(38,0)` operand whose multiplication could overflow inferred precision. Only the final in-range value casts to the signed carrier. Under the independent pseudorandom-word assumption already inherent in separate Spark `rand()` expressions, reducing a 96-bit source gives each residue either `q` or `q+1` preimages with `q=floor(2**96/w) >= 2**32`; relative point imbalance is at most `2**-32`, rather than the up-to-2x imbalance of a 64-bit modulo. This prevents material modulo bias but does not claim exact statistical uniformity. Literal-limb integration tests compare each folded Decimal stage with a Python-bigint oracle for constant, small, negative-only, crossing-zero, `2**53+1`, both int64 extremes and full signed width. No Python UDF, double result arithmetic or finite-retry fallback is permitted.

### 2.3 DataFrame pipeline and modifiers

- `DataGenerator` retains one `np.random.Generator`. One internal row-batch call evaluates the current spec, generates columns, applies embedded transformers, applies each global transformer, verifies unchanged row count/index width, then delegates anomalies and nulls to `RandGenerator`.
- A global transformer that changes row count raises `RandEngineError` before modifiers or writer commit. Unbatched `get_df` and save keep one call. Batched save calls once per non-empty row batch. Zero-size partitions call neither transformer nor RNG.
- Ordinary-column anomaly masks and values draw only when `anomaly_rate > 0`; null masks draw only when `null_rate > 0`. Anomalies apply first, compatibility is checked against the transformed Series without widening, then dtype-specific null assignment runs last. Constants consume no RNG.
- Modifier validation and application resolve an ordinary column once from the same existing metadata as generation: its sole `cols` alias when present, otherwise its spec key. That resolved output name drives compatibility, anomaly and null handling; no second naming path is added, and embedded-transformer legacy mapping is unchanged.
- Nullable integer/boolean extension dtypes, float `NaN`, datetime `NaT`, and object/string-backed Python `None` are established before Arrow conversion. A transformed pandas string Series becomes object dtype when nulls are assigned so its values are literal `None`, not `pd.NA`. `stream_dict` normalizes all missing sentinels to Python `None`.

### 2.4 Helpers

- `RandSpecs.faker_pool` imports Faker inside the call, creates a local instance, calls `seed_instance`, resolves one named provider and materializes exactly `pool_size` scalar values into the returned ordinary `distincts` column spec. Import/provider/locale/size/output errors become `RandEngineError`. Packaging exposes an optional Faker extra and keeps the ordinary install Faker-free.
- `RandSpecs.from_schema` accepts only `pyarrow.Schema`, performs the SPEC's literal mapping, rejects duplicate/unsupported fields unless completely overridden, and never reads data. It copies schema/override inputs. Whole-method overrides replace a column; kwargs-only overrides merge into the default then normal validation runs. The result is an ordinary dict.
- `RandSpecs.from_schema` delegates the assembled result to `AdvancedValidator`; it does not duplicate the catalog's integer range arithmetic. Job 7 therefore supplies the required normal-validation prerequisite before paused helper task J4.S3.T1 resumes; disjoint packaging task J4.S3.T2 is unaffected.

### 2.5 Bounded writer and stable schemas

- Validate writer options, `maxRowsPerBatch`, resolved total size and the complete write plan before touching output. Split total rows across final files first, then subdivide each non-empty file range; maintain one cumulative offset. The iterator holds plan scalars and at most one generated DataFrame.
- Write each requested output into a unique same-filesystem staging sibling. CSV keeps one compressed stream and emits one header; JSON keeps one stream and appends JSON-lines without forwarding `numFiles`/`maxRowsPerBatch`; Parquet keeps one `ParquetWriter`. The existing three adapters are a real seam—no generic port is added.
- The first concrete transformed batch establishes field names/order and Arrow schema; nullable/all-null columns remain typed by the DataFrame contract. Every later batch must match. An object column whose transformed output is genuinely indeterminate fails in staging. Empty final partitions use the already established schema; if every partition is empty, the validator's method/dtype plan supplies it, and arbitrary transformers make the request indeterminate and refused without calling them.
- Staging bounds memory while preserving the old destination through option, transformer, anomaly and schema failures. After all files close and read-back metadata is valid, commit the staged single file with `os.replace`; for a multi-file directory, rename the old destination aside, rename staging into place, then remove the aside, rolling back the first rename if the second fails. Cleanup removes only the writer-created staging sibling. Append also builds the complete replacement in staging: copy existing CSV/JSON bytes or files before appending, and stream existing Parquet row groups through the staged `ParquetWriter`; it never mutates the destination before the same commit step and never loads the prior dataset whole.
- Writer fixture migration follows the same RED/GREEN chronology as production behavior: J5.S1.T3 only records the final `tmp_path` expectation against the current persistent fixture, while J5.S2.T3 changes `f3_integrations.py` and deletes that satisfied marker in the same task. No RED task repairs the fixture early or manufactures an XPASS.

## 3. Verification and gates

- Every job starts with tests-only Stage 1. Each new acceptance test holds its final expected values, fails by assertion and carries one `@pytest.mark.xfail(strict=True, ...)` line so RED remains explicit and auditable. The green task deletes only that marker line after the implementation satisfies the assertion.
- Default tests stay at or below `10**4` rows. Distribution/modifier throughput is measured only by the official same-runner benchmark workflow at final feature preparation.
- Unit: validator issue collection, numeric lattice/distributions/constants, RNG draw order, masks, helpers, write-plan arithmetic and schema decisions.
- Integration: Spark expressions, pandas dtypes, stream/sink nulls, read-back CSV/JSON/Parquet, transactional overwrite, public imports.
- E2E: none; this is a library with no browser or deployed service. Public import plus documented executable examples are the outer interface.
- Security/privacy: no external data or URLs; Faker stays local/optional; writer staging uses a generated sibling under the caller-selected parent and never follows a new arbitrary remote fetch; errors retain field, option and key-path identifiers without dumping collections, pairs, items or input value payloads; no credentials or PII enter fixtures.
- Local task/stage/job gates use the repo's existing shared environment and redirected caches. No worktree push or remote worktree CI. The main thread may publish only `feature/0.7.0` during final release preparation to obtain AC2.4/AC4.4 evidence.

## DAG

| job | waits on | why |
|---|---|---|
| Job 1 | none | Rebuild validation intake/catalog first; it owns three confirmed bugs and every later grammar. |
| Job 2 | Job 1 | Numeric implementations require the approved catalog and close the two numeric bugs. |
| Job 3 | Job 2 | Modifiers consume the catalog, new constant/distributions and RNG contract. |
| Job 7 | Job 2 | Canonical integer range semantics are a prerequisite for the helper's merged-override normal-validation contract. |
| Job 4 | Job 7 | Stage 3 is open: disjoint packaging T2 continues, while the clean paused helper T1 rebases after Job 7 and then resumes. |
| Job 5 | Job 3 | Writer batching consumes the final row-batch/modifier/dtype pipeline. |
| Job 6 | Job 4, Job 5 | Reconciliation is last; it consumes all public behavior and final feature benchmark evidence. |

### Hot files

| path | jobs | serialization |
|---|---|---|
| `benchmarks/speed.py`, `tests/test_benchmarks.py` | 2, 3 | Job 3 waits for Job 2 and adds modifier rows after new-method rows. |
| `tests/test_2_data_generator.py` | 2, 3 | Job 2 owns only the approved uniform-float replacement hash and five new method hashes; Job 3 waits for Job 2 before adding modifier pipeline contracts. |
| method catalog, validator intake and validator registry/domain contracts | 1, 2, 7 | Job 1 serializes catalog/common J1.S2, shared-common/advanced J1.S3 and review corrections J1.S4–J1.S5; after Job 1 merges, Job 2 owns numeric-helper delegation and engine sets; Job 7 then owns only `_integers` range semantics. |
| `tests/fixtures/f3_integrations.py`, `tests/test_5_writer_fixture_paths.py` | 5 | J5.S1.T3 is tests-only RED; J5.S2.T3 owns the fixture repair and its marker cleanup together. |
| `rand_engine/main/data_generator.py`, `rand_engine/main/_rand_generator.py` | 3 | J3.S2 owns the coupled pipeline; J3.S4 corrects modifier output-name resolution and object/string null representation in the same RandGenerator seam. |
| `rand_engine/file_handlers/_writer_batch.py`, `file_handler.py` | 5 | separate task owners use disjoint tests and merge at the stage barrier. |
| docs/README/`llms.txt`/benchmark artifacts | 6 | reconciliation only, after final behavior is merged. |

## 5. Job envelopes

- Job 1 — validation intake: validator catalog/modules and validator tests, including the three validation-bug RED/fix owners.
- Job 2 — numeric methods: NumPy/Spark cores, method map and numeric/core/benchmark tests, plus the existing DataGenerator seeded-output table's six approved numeric-method hash entries, including the two numeric-bug RED/fix owners.
- Job 3 — DataFrame modifiers: DataGenerator/RandGenerator, stream conversion and modifier benchmark rows/tests.
- Job 7 — schema validation prerequisite: canonical `_integers` range semantics and focused public validator/generator controls only; no helper-local logic or new domain policy.
- Job 4 — spec helpers: RandSpecs helpers and optional-Faker packaging plus focused helper/public tests; Stage 3 is open, its disjoint packaging T2 remains authorized, and only helper T1 is paused until Job 7 merges and its clean tree rebases.
- Job 5 — batch writer: write planner, format sessions and writer fixtures/tests; `writeStream` production stays untouched.
- Job 6 — canonical reconciliation tree `0.7.0-rc2/reconcile`: executable docs, README/llms, benchmark artifacts and public integration evidence finish first; the main thread then advances to CLOSURE at that exact implementation SHA, the product engineer performs the derived memory worklist in the same tree, and the main thread records the terminal narrative/dispositions/artifact GC before its single review and merge.

## 6. Task authority and acceptance trace

The canonical task authority is the seven files under `tasks/`, one per DAG job. The current `release.py` validates each stage contract and disjoint `W:` sets; no `TASKS.md`, duplicated marker list or second task description is maintained.

| requirement | RED owner | GREEN/closure owner |
|---|---|---|
| AC1.1–AC1.6 | J5.S1 | J5.S2; J6 local read-back reconciliation |
| AC2.1–AC2.3 | J1.S4 totality regression and J2.S1 numeric contracts | J1.S5 validator correction and J2.S2 numeric implementation, including DataGenerator inventory and seeded hashes |
| AC2.4 | J2.S1 benchmark contract | J6.S2 final-preparation CI artifact |
| AC3.1–AC3.3, AC3.5 | J3.S1 and corrective J3.S3 | J3.S2 and corrective J3.S4 |
| AC3.4 | J3.S1 stream and J5.S1 sinks | J3.S2 and J5.S2 |
| AC4.1–AC4.3 | J3.S1 and corrective J3.S3 | J3.S2 and corrective J3.S4 |
| AC4.4 | J3.S1 benchmark contract | J6.S2 final-preparation CI artifact |
| AC5.1–AC5.4 | J4.S1 and corrective J4.S2 | J4.S3 |
| AC6.1, AC6.3–AC6.4 | J4.S1 and corrective J4.S2 | J4.S3 |
| AC6.2 | J4.S1, corrective J4.S2 and J7.S1 catalog-prerequisite RED | J7.S2 canonical range semantics, then J4.S3 helper delegation |
| AC7.1 | J1.S4 scalar-structure regression and J2.S1 | J1.S5 shared scalar predicate and J2.S2 |
| AC7.2–AC7.3 | J2.S1 and J3.S1 | J2.S2 and J3.S2 |
| AC8.1–AC8.2 | J1.S1 and J1.S4 review regressions | J1.S2–J1.S3 and J1.S5; canonical post-Job-5 bug batch records resolution |
| AC8.3–AC8.5 | J1.S4 legacy-compatibility regression, J2.S1 and J2.S3 extreme-decimal RED | J1.S5 compatibility correction, J2.S2 and J2.S4 exact tuple-shift conversion, including the approved uniform-float DataGenerator hash replacement; canonical post-Job-5 bug batch records resolution |
| AC8.6 | J5.S1.T3 tests-only fixture-path RED | J5.S2.T3 fixture repair and satisfied-marker cleanup |
| AC8.7 | J1.S1 behavioral single-intake/no-generation test | J1.S2–J1.S3, J2.S2 and J3.S2 preserve that interface while their diffs evidence deletion; J6 review confirms no replacement path |
| AC9.1 | J2.S1, J2.S3, J3.S1, corrective J3.S3, J5.S1 | owning GREEN stages; J2.S2 owns its DataGenerator inventory/hash reconciliation, J2.S4 owns accepted extreme-decimal generation and J3.S4 owns modifier alias/null correction |
| AC9.2 | J1.S1, J1.S4 and J2.S1 | J1.S2–J1.S3, J1.S5, J2.S2 and J6 public reconciliation |
| AC9.3 | J3.S1, corrective J3.S3 and J5.S1 | J3.S2, corrective J3.S4 and J5.S2 |
| AC9.4 | J4.S1 and J6.S1 | J4.S3 and J6.S2 |

The five bug paths are exact: J1.S1/J1.S2–J1.S3 own the original RED/fix evidence for `probability-wrong-type-escapes-validation`, `distincts-map-empty-pool-validates` and `distincts-multi-map-empty-domain-validates`; J1.S4/J1.S5 close the additional-review compatibility, totality and scalar-structure gaps before any of those records can resolve. J2.S1/J2.S2 own the evidence for `float-rounded-domain-violates-bounds` and `spark-bigint-precision-lost`. After Job 5, the canonical bug batch outside the DAG reruns each independent RED/GREEN command and resolves all five through the ledger writer before reconciliation opens; it adds no alternate implementation path.

AC8.7's RED is behavioral, not a source tombstone: constructing `DataGenerator` from a counting callable that returns independently invalid common and advanced columns must evaluate that callable once for the failed construction, return one collected issue per column, never enter the generation seam and never leak `TypeError`, `KeyError` or `ColumnGenerationError`. The J1.S3 GREEN keeps that public boundary while the implementation diff deletes the dead validation parameter, imports, redundant branches, commented implementation and history comments. The unmerged provisional `b91a1c8` is superseded by J1.S3.T1 and carries no task authority. Job 1 closes in J1.S5.T2 after corrective GREEN and the repeated additional checkpoint; its official stage gate and closing trailer then establish the exact HEAD for final Job 1 review before canonical merge. Job 2 closes in J2.S4.T2 only after the corrective J2.S3 RED and J2.S4.T1 GREEN; every other job's final stage likewise has one disjoint close task whose only write is that job file's terminal `done`. Each close task runs only after its stage contract is green and commits as `chore(tasks): done <job>`.

Job 4's rejected additional checkpoint routes the omitted existing-AC cases into tests-only J4.S2. J4.S3 opened after J4.S2 task and stage gates were green and the reviewer issued an APPROVED checkpoint-recovery verdict; no helper source or packaging task was authorized before that recovery. Its disjoint packaging T2 remains authorized and active while helper T1 is paused cleanly for Job 7.

The merged-override case exposed a pre-existing catalog gap rather than helper-owned validation: `_integers` accepted `min=101, max=100`. Job 7 owns the assertion-first public-boundary RED and the one canonical catalog correction under AC6.2. It must merge before the already-approved J4.S3.T1 helper tree rebases and resumes; fixed Job 4 task IDs and write sets do not change, and disjoint J4.S3.T2 packaging progress is preserved.

## 7. Closure sequence

1. Merge reviewer-approved jobs locally in DAG order, including Job 7 before paused J4.S3.T1 resumes and Job 6 last; disjoint J4.S3.T2 packaging may progress under its existing approval. No worktree push. Run the canonical outside-DAG bug batch and resolve all five records from their existing owners before opening reconciliation.
2. With benchmark code present, the main thread performs the authorized final-preparation push of `feature/0.7.0`; AC2.4/AC4.4 must pass or the owning job reopens locally.
3. Open Job 6 only as `0.7.0-rc2/reconcile`. Its RED/green implementation stages consume the exact CI artifact, update derived docs and run local full/default tests, build and package metadata checks.
4. At Job 6's green implementation SHA, the main thread records the IMPLEMENTATION → CLOSURE transition in that same tree. Only then does the product engineer execute the drift-derived memory worklist and ledger memory entry there; the main thread adds the closure narrative, dispositions and artifact-GC evidence there. No second closure tree or authority is opened.
5. The reviewer issues one Job 6 verdict over the complete reconciliation HEAD; its merge is the candidate-close boundary. No PR42 bypass, admin merge, release push, tag, deploy or premature candidate-complete claim occurs in a task.
