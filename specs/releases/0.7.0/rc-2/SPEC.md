# SPEC — Release: 0.7.0, candidate 2 (bounded generation + RandSpec breadth)

**Status:** Approved
**Release ID:** 0.7.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-07
**Origin:** operator-demand

- Demand: deliver the seven RC2 themes deferred by RC1 §5, repair the five defects confirmed by the full forensic review, and rebuild recurrent validation, numeric and writer units instead of layering exceptions.
- Sources: confirmed grill handoff `2026-10-07T165344Z-main-thread-grill-rc2-confirmed`; forensic report `2026-10-07T153804Z-main-thread-bug-forensics-rc2.html`; RC1 SPEC §5; operator instruction to proceed.
- Approval: operator, 2026-10-07, verbatim: “aprovo a Spec Atual da RC2” — the current contract, including the product-engineer API spellings/defaults below, is approved without substantive amendment.

## Bug window review

All 25 resolved records, cited tests and current seams were reviewed. KEEP preserves the examined fix. REBUILD preserves useful regression assertions while replacing the recurrent unit around it; it does not relabel the historical fix as bad.

| bug | verdict | contract carried forward |
|---|---|---|
| `writer-options-consumed-by-use` | REBUILD | reused writer keeps options; rebuild plan |
| `writer-size-not-from-generator` | REBUILD | generator `size` is the sole total |
| `ci-summary-commit-message-shell-injection` | KEEP | text stays outside shell source |
| `validator-warnings-raised-as-errors` | REBUILD | warnings remain non-fatal |
| `validator-engine-schema-drift` | REBUILD | grammar and engine agree |
| `timestamps-depend-on-local-timezone` | REBUILD | NumPy time remains UTC |
| `int-type-overflow-silent` | REBUILD | impossible dtype domains are refused |
| `floats-bounds-truncated` | REBUILD | complete decimal domain, not one edge |
| `spark-integers-max-exclusive` | REBUILD | inclusive bounds with exact arithmetic |
| `cdc-generator-unimportable` | KEEP | CDC stays deleted |
| `writer-state-shared-across-chains` | REBUILD | chains stay independent |
| `writer-numfiles-rows-per-file` | REBUILD | total rows split across files |
| `memory-atom-ignored-by-output-glob` | KEEP | anchored ignore stays |
| `unused-runtime-deps-shipped` | KEEP | deleted deps/imports stay deleted |
| `method-registry-has-five-owners` | REBUILD | one authority; `args` break authorized only here |
| `advanced-rand-specs-fail-validation` | KEEP | examples validate and generate |
| `spark-timestamps-depend-on-timezone` | REBUILD | Spark time remains UTC/session-independent |
| `spark-empty-date-range-not-refused` | REBUILD | empty/inverted domains are refused |
| `spark-floats-inverted-range-not-refused` | REBUILD | inverted floats are refused |
| `codecov-upload-blocks-ci` | KEEP | telemetry remains advisory |
| `date-format-required-but-docs-omit-it` | REBUILD | documented defaults remain valid |
| `distincts-multi-map-drops-levels-silently` | REBUILD | exact arity and non-empty domain |
| `csv-tz-aware-fails-on-windows` | REBUILD | keep cross-platform CSV adapter |
| `dates-oracle-fails-on-windows-past-3000` | KEEP | portable oracle stays |
| `distincts-map-column-order-reversed` | REBUILD | category remains first |

Five confirmed bugs enter: `float-rounded-domain-violates-bounds`, `distincts-map-empty-pool-validates`, `distincts-multi-map-empty-domain-validates`, `probability-wrong-type-escapes-validation`, `spark-bigint-precision-lost`. Each uses its independent failing public reproduction; no historical RED chronology or causal link is invented.

## 1. Problem and context

- A final file is generated as one whole DataFrame. The factory list is lazy, but a large file has no row-batch bound.
- RandSpec lacks four requested distributions, a scalar constant, explicit null/anomaly modifiers, an optional Faker pool helper and a metadata-only schema starter.
- Repeated validation branches run semantic comparisons after type failure. Rounded floats can leave requested bounds; Spark `long` loses integers above 2^53 through double arithmetic.
- Writer fixes left misleading factory names/types and quadratic offsets; duplicate Python test names discard earlier NumPy parameter tables before collection.

## 2. Objective

Bound writer generation by rows and broaden NumPy-first RandSpecs without hidden state, business inference or new mandatory dependencies, while one validation intake and honest numeric domains ensure every accepted spec generates.

## 3. Scope

### Terms and operator decisions

- **Ordinary column:** one output column from a non-key, non-correlated method. `pk`, `fk`, `distincts_map`, `distincts_map_prop`, `distincts_multi_map` and `complex_distincts` are excluded.
- **Row batch:** a contiguous slice of one final file, bounded by rows. It is not a new file, retained state or byte-RAM promise.
- **Modifier:** `anomaly_rate` or `null_rate` on an ordinary column. Rates are independent per-row probabilities, not exact counts.
- Order: generation → embedded transformers → global transformers → anomalies → nulls; null wins on overlap.
- New methods/modifiers are NumPy/DataGenerator-first. Spark explicitly refuses unsupported method names/keys; no dummy columns or Python UDF.
- Same seed, spec, size and row-batch configuration reproduces values. Changing row-batch size may change ordinary values. Disabled features consume no RNG.
- With batching, global transformers run once per row batch. Without it, the old one-frame path and call count stay.
- Faker is optional and locally seeded; PyArrow is already required. No data samples, business inference, SQL, database or persisted relations.

### Draft API proposals

- Writer option `maxRowsPerBatch`; absent/`None` disables it, positive integer enables it.
- Methods: `exponential(scale=1.0, decimals=2)`, `lognormal(mean=0.0, std=1.0, decimals=2)`, `poisson(lam=1.0)`, `zipf(a=2.0)`.
- Constant: `{"method":"constant","kwargs":{"value": <scalar>}}`.
- Modifiers are sibling column-spec keys `null_rate`, `anomaly_rate`; a positive anomaly rate requires non-empty scalar list `anomaly_values`, sampled uniformly.
- Helpers on existing exported `RandSpecs`: `faker_pool(provider, locale="en_US", pool_size=100, seed=None)` and `from_schema(schema, overrides=None)`.

### FR1 — Bounded batch-save generation

- `maxRowsPerBatch` applies only to `FileBatchWriter.save`; `writeStream` is unchanged. `size` stays total rows and `numFiles` final-file count. Each file's contiguous range is subdivided without changing file count/order.
- AC1.1 (integration): size 23, four files, maximum batch 3 yields four readable files with sorted row counts `[5,6,6,6]`, 23 total, RC1-contiguous key ranges, and no generated frame above 3 rows.
- AC1.2 (integration): CSV has one header, JSON remains JSON-lines and Parquet one readable file per part; read-back order/schema follow existing contracts.
- AC1.3 (unit): absent/`None` is disabled; zero, negative, bool or non-int raises `RandEngineError` before overwrite removes output.
- AC1.4 (integration): a counting global transformer runs once unbatched and once per row batch when enabled. Same configuration reproduces; different batch sizes need not match ordinary values. Keys keep row-index semantics.
- AC1.5 (unit): one linear cumulative-offset plan holds lazy factories, not DataFrames, and releases each generated batch after writing.
- AC1.6 (integration): when enabled and `size < numFiles`, the existing split retains `numFiles`; each zero-row partition becomes one empty typed file without a zero-length generation/transformer call or RNG draw. Validated method/dtype contracts establish one stable schema per final file before destructive overwrite; typed nullable/all-null batches are valid and cannot cause later schema drift, while a genuinely indeterminate transformed output fails before mutation.

### FR2 — Four distributions

- AC2.1 (unit): seeded outputs match literal 1,000-row golden hashes and their NumPy family; exponential/lognormal are rounded `float64`, poisson/zipf `int64`.
- AC2.2 (unit): `scale<=0`, `std<0`, `lam<0`, `a<=1`, or non-integer/negative `decimals` raises collected `SpecValidationError` before generation.
- AC2.3 (unit): existing uniform `floats` and normal `floats_normal` names, defaults, dtypes and seeded goldens are unchanged except the explicit representable-domain replacement for `floats` in AC8.3.
- AC2.4 (CI benchmark): each new method is no slower than 1.5x its closest sibling in the same official run; large loads remain CI-only.

### FR3 — Null modifier

- AC3.1 (unit): rate 0 is bit-identical to absence and consumes no RNG; rate 1 nulls every row; equal configurations have the same literal mask.
- AC3.2 (unit): only ordinary columns accept a real rate in `[0,1]`; wrong/out-of-range values and excluded methods raise collected `SpecValidationError`.
- AC3.3 (integration): `get_df` uses matching-width pandas nullable signed/unsigned integers, nullable `boolean`, `NaN` without changing float dtype, `NaT` without changing datetime dtype, and `None` for object/string. Non-null values keep the source contract.
- AC3.4 (integration): `stream_dict` returns Python `None`; JSON-lines writes `null`; CSV an empty field under existing quoting/single-column rules; Parquet a typed null retaining its non-null logical type.
- AC3.5 (unit): null selection occurs last and wins over an anomaly on the same row.

### FR4 — Anomaly modifier

- AC4.1 (unit): rate 0 is bit-identical/zero-RNG; rate 1 replaces every row from `anomaly_values`; a seeded configuration has a literal mask/value golden.
- AC4.2 (unit/integration): spec validation requires a positive rate to carry a non-empty list of structurally valid scalars and refuses wrong rates or nested values. Because arbitrary transformers make the resulting dtype unknowable at construction, value compatibility is checked after transformers and before replacement/return or any writer mutation; incompatibility raises `RandEngineError` and never silently widens.
- AC4.3 (unit): keys/correlated methods refuse modifiers. No orphan FK, duplicate PK, implicit corruption rule or exact-count promise is added.
- AC4.4 (CI benchmark): either modifier costs at most 25% over its unmodified method in the official same-runner run.

### FR5 — Optional Faker pool

- AC5.1 (unit): with Faker installed, `faker_pool("name", locale="pt_BR", pool_size=5, seed=7)` returns ordinary `distincts` with a fixed five-value pool; identical calls are deep-equal and do not alter Python, NumPy or Faker global RNG.
- AC5.2 (unit): changing helper seed can change the pool; generation samples the fixed pool only through DataGenerator's RNG.
- AC5.3 (unit): missing Faker raises `RandEngineError` naming optional installation; Faker is not a core dependency. Unknown provider/locale, invalid size or non-scalar provider output fails during helper construction.
- AC5.4 (unit): no Faker call occurs during generation and no second Faker generation engine exists. A returned legacy `distincts` spec has only its existing engine behaviour.

### FR6 — PyArrow schema starter

- `from_schema` accepts `pyarrow.Schema`, never Table/DataFrame/file/sample. Names/metadata carry no business inference; nullable permits nulls but does not invent a rate (default 0).

| Arrow type | literal default recipe | `get_df` output |
|---|---|---|
| `bool` | `booleans(true_prob=.5)` | `bool` |
| signed/unsigned integer widths | `integers(min=0,max=min(100,dtype max),int_type=<matching NumPy>)` | matching NumPy dtype |
| `float32`, `float64` | `floats(min=0,max=1,decimals=2)` | `float64` |
| `string`, `large_string` | `uuid4()` | object UUID strings |
| `date32`, `date64` | `dates(2000-01-01..2030-12-31,"%Y-%m-%d")` | object ISO date strings |
| timezone-free `timestamp` | `dates(2000-01-01..2030-12-31,"%Y-%m-%d %H:%M:%S")` | object UTC timestamp strings |
| `null` | `constant(None)` | object nulls |

- Decimal, binary/fixed binary, time, duration, interval, nested, dictionary/extension and timezone-bearing timestamp have no default; an override must replace that column completely.
- AC6.1 (unit): a schema with every supported type yields the exact literal mapping above and generates stated outputs without external reads.
- AC6.2 (unit): overrides name existing fields only and win. An override containing `method` replaces the whole generated column config and must supply a complete valid config—no default kwargs or modifiers survive. An override without `method` keeps the default method, merges `kwargs` key-by-key, and replaces any supplied modifier metadata. Unknown fields/incomplete results raise `SpecValidationError`.
- AC6.3 (unit): unsupported/duplicate fields name the field/type and remedy; Schema and overrides remain unmutated.
- AC6.4 (unit): result is only a RandSpec dict—no registry, inference service, persisted metadata or engine.

### FR7 — Constant

- AC7.1 (unit): `constant(value=x)` repeats `x` for `None`, bool, int, float, str, bytes, date, datetime and Decimal scalars; mutable containers/callables are refused.
- AC7.2 (unit): a non-null scalar has stable natural pandas dtype; `None` is object-null. Modifiers apply because constant is ordinary.
- AC7.3 (unit): constant consumes no RNG; adding/removing it does not change other seeded columns.

### FR8 — Rebuild validation/numeric families and repair five bugs

- Structure/types precede semantic rules; all issues collect in one `SpecValidationError`. One method authority supplies names, kwargs, types/defaults and engine support to validation/generation; no third registry or second path.
- Public positional `args` are removed as a 0.7.0 breaking migration: use named `kwargs`. Approval is prospective and does not retroactively authorize commit `4147b088`.
- AC8.1 (unit): `true_prob="abc"` and every wrong numeric type produce only collected `SpecValidationError`, never raw `TypeError`.
- AC8.2 (unit): every `distincts_map` pool and every required `distincts_multi_map` level is non-empty; both confirmed reproductions fail validation, not generation.
- AC8.3 (unit): rounded `floats(min,max,decimals=d)` sample integer lattice `ceil(min*10^d)..floor(max*10^d)` divided by `10^d`; an empty lattice, including `9.991..9.991` at 2 decimals, is refused. No clipping/special value branch. Spark shares the contract.
- AC8.4 (Spark integration): `int8/16/32/64` and `uint8/16/32` use exact inclusive result arithmetic, never double; min=max=`9007199254740993`, `int64`, yields that literal. Spark refuses `uint64` because signed `bigint` cannot carry its full domain; every other unsupported exact domain is refused before execution. This criterion proves bounds/representability, not exact statistical uniformity across arbitrary 64-bit spans; the technical review below must prevent a silently biased modulo implementation.
- AC8.5 (unit): duplicate NumPy test names become single collected parameter tables; useful original uniform, normal, categorical, timezone and dtype asserts remain.
- AC8.6 (integration): writer fixtures use pytest `tmp_path`, never persistent `tests/test_outputs` or recursive repo cleanup.
- AC8.7 (unit): dead validation parameters, unused imports, redundant branches, commented implementation and history comments leave; no flag/wrapper replaces them.

### FR9 — Compatibility and boundaries

- AC9.1 (unit): every legacy NumPy spec with new features disabled and batching absent matches RC1 seeded goldens byte-for-byte, except AC8.3's declared float-domain replacement. Old uniform/normal asserts are not rewritten to fit code.
- AC9.2 (integration): legacy Spark goldens remain except AC8.4 bigint correction; unsupported new method/modifier names fail naming DataGenerator, with no Python UDF.
- AC9.3 (unit): same seed/spec/batch configuration reproduces modifier masks/values; disabled modifiers and constants consume no RNG. Different batch sizes have no equality promise.
- AC9.4 (integration): public imports remain `DataGenerator`, `SparkGenerator`, `RandSpecs` and existing exceptions; no mandatory dependency, persisted relation state, database, SQL or business inference is added.

## 4. Replaces

- Whole-final-file generation, misleading DataFrame names/types for factories and quadratic offsets → FR1 linear lazy row-batch plan.
- Repeated validator ownership and semantic fallthrough after structural failure → FR8 single intake/method authority.
- Positional `args` grammar/dispatch → named `kwargs`, authorized by approval now, not retroactively.
- Uniform-then-round floats that leave bounds → representable decimal lattice/refusal.
- Spark integer result arithmetic through `double` → exact supported arithmetic/refusal.
- Spark acceptance of `uint64` despite lacking an exact carrier → explicit validation refusal.
- Empty correlated domains and raw type errors after validation → AC8.1–AC8.2.
- Overwritten NumPy tests and persistent writer-fixture output → AC8.5–AC8.6.
- Dead `validate` parameter, unused imports, redundant branches, commented implementation/history → deletion under AC8.7.

## 5. Out of scope

- Spark implementations of new distributions, constant or modifiers; Spark PK/FK parity; Python Spark UDFs.
- Byte-exact RAM caps, adaptive memory measurement, global writer settings, changed `size`/`numFiles`, or equality across different row-batch sizes.
- Applying the row-batch cap to `writeStream`; its existing one-size-row microbatch per emitted file remains unchanged.
- Persisted relations, DB sinks/lookups, SQL, event-time FK ordering, composite keys or orphan/duplicate-key anomalies.
- Faker core dependency/runtime engine; inference from data; business defaults; nested/decimal/binary/time/tz-aware Arrow defaults.
- Existing uniform/normal changes beyond AC8.3; schema registry, new engine/writer/public class or unrelated grammar.
- RC3/backlog items; PR42 admin merge/rule bypass; rewriting closed RC1.

## 6. Dependencies and risks

- Main thread owns the five bug records. Their write-once `found_in=rc-1` reflects discovery during RC1 review; this SPEC does not rewrite lineage.
- Operator override: no `wt/*` push or worktree remote CI; local task/stage/job gates and reviewer-approved local feature merges. Only final release preparation publishes `feature/0.7.0`. PR42 remains open and needs external approval; no admin bypass. Its state does not block definition.
- Project specs checks currently have only known consumer TREE-5 warnings; unrelated global workspace drift is not RC2 scope. No implementation-compliance claim precedes main-thread disposition.
- Sequence: validation/numeric rebuild → methods/modifiers/helpers → row-batch writer → reconciliation. RED precedes fixes; old asserts stay unless this SPEC explicitly replaces behaviour. Heavy performance evidence stays in CI.

| risk | mitigation |
|---|---|
| batching changes ordinary seeded values | configuration is part of reproducibility; default keeps goldens |
| nulls widen dtype | fixed DataFrame and sink contracts in AC3.3–AC3.4 |
| anomalies corrupt structure/type | compatibility validation; ordinary only; null last |
| schema name implies business meaning | literal defaults, refusal set, overrides, no inspection |
| Faker becomes global/mandatory | local instance, fixed pool, optional import |
| recurring fixes add branches | replace three units and require deletions |
| Spark bigint fix moves precision loss | exact >2^53 literal plus refusal |
| modulo of a 64-bit word can make points up to 2x likelier on spans above 2^63 | before implementation, engineer and reviewer quantify the proposed native-expression distribution across small, negative, crossing-zero and wide domains; if material bias cannot be avoided without narrowing the public domain, stop for an explicit SPEC amendment rather than silently weakening random-integer intent |
