# SPEC — Release: 0.8.1, candidate 2 (installs on today's stacks and CI proves it; Spark refuses the NULL methods; direction rulings)

**Status:** Draft
**Release ID:** 0.8.1
**Owner:** dd-product-engineer
**Opened:** 2026-10-24
**Origin:** backlog:compat-current-ecosystem,spark-refuse-null-methods,constitution-direction-rulings

- Demand, operator verbatim: "Todos esses pontos devem ser tratados imediatamente ... COMO ASSIM NÃO INSTALA ... COMO PODE ENTREGAR ALGO ASSIM SEM TESTAR". Meaning: 0.8.1 installs and passes on today's stacks, and CI proves it on every push with a fresh resolve, not only the lock.
- Sources (`.dadaia/handoff/rand-engine/`): release grill `2026-10-24T170504Z-main-thread-grill-rc2`, as-is review `2026-10-24T165850Z-dd-sw-engineer-sr-rc2-as-is-review`, roadmap grill `2026-10-24T160915Z-main-thread-grill-roadmap`.
- Operator words carried: compatibility "Cobrir o que está em uso (Recomendado)"; Spark "Nada além disso (Recomendado)"; north star "Velocidade e nicho (Recomendado)"; roadmap home "Backlog + página pública (Recomendado)"; the 2026-10-11 rulings "Confirmo todas (Recomendado)"; dtype "uai, se possivel ns. See if for pyarrow is faster. If it is, we use it. if no, we use pandas."; version "0.8.1 (Recomendado)".
- Invariant 12, by-name approval, operator verbatim: "Apagar os 4 métodos NULL, Unificar o cálculo de epoch, You've mentined v0.6.4. Don't forget we are in 0.8.0." It approves, and nothing else:
  - deleting `SparkCore.gen_distincts_map`, `SparkCore.gen_distincts_multi_map`, `SparkCore.gen_distincts_map_prop` and `SparkCore.gen_complex_distincts`;
  - changing `NPCore.gen_unix_timestamps` and `SparkCore.gen_unix_timestamps` so both call one shared epoch-bounds function;
  - changing `SparkCore.gen_dates`, for its one comment line only (FR4, AC4.4), operator verbatim, 2026-10-24: "Aprovo (Recomendado)".
- The same two `gen_unix_timestamps` bodies were REBUILT in the hotfix lane on the operator's approval, verbatim: "Aprovo os dois (Recomendado)".
- `StreamHandler` and every other `gen_*` body stay untouched. Changed bodies keep the operator's style: 2-space indentation, one-line guards, terse NumPy.
- The "v0.6.4" remark: the invariant names the release whose bodies it protects; its text stays unchanged unless the operator orders otherwise.

## Bug window review

The prior candidate is rc-1. `specs/bugs/BUGS.jsonl` holds 2 resolved records and 0 open ones. Each fix was found by its id line, read with `git show`.

| bug | fix | found by | pattern hit | verdict | why |
|---|---|---|---|---|---|
| `benchmark-sibling-pairs-poisson-with-text-method` | `a76abde` (RED `65f878a`) | id line | none: it only changes the `METHOD_SIBLINGS` mapping, +2/−2 | KEEP | `benchmarks/speed.py` is outside this candidate, and no child bug followed |
| `dates-before-1970-validate-then-raise` | `1c3ddc2` (RED `7014bc0`; resolved `ade02f5`, ledger tip `a061404`) | id line | the epoch line stays duplicated in two bodies (predates it: `97abd63` + `896cd3d`); its test commit moved the Spark empty-range case to reversed pre-1970 bounds, partition kept | KEEP | below |

- `dates-before-1970-validate-then-raise` is KEEP: the dates unit (`NPCore.gen_unix_timestamps`, `SparkCore.gen_unix_timestamps`) was REBUILT by the hotfix lane (ledger tip `a061404`, verdict `2026-10-24T165442Z` APPROVED); the REBUILD deletes the 1970 clamp at its cause in both bodies, and no child bug followed. This candidate unifies the duplicated line on the operator's ruling (FR4), hardens the Spark 1969–1970 case that passes on the reverted fix (AC4.3), and corrects the record (AC4.5).

- The as-is review traced every touched unit's history: 13 ledger bugs, all resolved, `caused_by: none`, no REBUILD due. KEEP all; this table adds no work.
- The Spark CORRELATED branch went hard error -> warning (`ef1356c`) -> refusal by ruling. The cause is a validator accepting what no engine runs; the catalog's `engines` field already decides it, so FR3 deletes the special case.

## 1. Problem

- 0.8.0 cannot be installed beside today's libraries: the carets of `pyproject.toml:14-17,36-40` cap `pandas<3.0.0`, `pyarrow<24.0.0`, `faker<29.0.0`, and `uv pip compile` proves it unsatisfiable with `pandas>=3`, `pyarrow>=24` or `faker>=30`. Current: pandas 3.1.0, pyarrow 26.0.0, Faker 40.43.0, pyspark 4.2.0.
- CI never tests what a user installs: every leg runs `poetry install` from `poetry.lock` (pandas 2.2.3 only) (`.github/workflows/test_on_push.yml:42-80`).
- On pandas 3.1.0 the suite fails 20 cases (1130 pass). Product breaks: one datetime `constant` spec declares `timestamp[ns]` and writes `timestamp[us]` (`method_specs._constant_arrow_type` hard-codes the pandas-2 coercion); a transformer's output dtype depends on the input backend (`apply_embedded_transformers` applies on an Arrow column); a str+None level becomes `str`/NaN where 0.8.0 gave `object`/`None`. The rest are test assumptions: a Python datetime column is `datetime64[us]`, and string subclasses are replaced before the stream sees them.
- One break hides outside the 20 failures. On pandas 3.1.0, a `dates` column with a `pd.Timestamp` transformer becomes `timestamp[us][pyarrow]`. `StreamHandler.convert_dt_to_str` (`rand_engine/utils/stream_handler.py:12`) matches only `datetime64`, so `stream_dict` yields a `pd.Timestamp` where pandas 2.2 yields text.
- On Spark, `distincts_map`, `distincts_multi_map`, `distincts_map_prop` and `complex_distincts` validate with a warning, then return NULL columns from dummy bodies (`rand_engine/core/_spark_core.py:111-144`). That breaks invariant 3.
- The two `gen_unix_timestamps` bodies compute epoch seconds with the same duplicated line. So every date defect needed two fixes: `97abd63` + `896cd3d`, then the hotfix pair.
- The 2026-10-11 direction rulings and the north star are not in the law.

## 2. Measurable goals

- The built 0.8.1 package resolves with a clean `pip install`, and the full suite passes, on two stacks:
  - the floor: Python 3.11, pandas 2.2.0, numpy 1.26.0, pyarrow 19.0.0, faker 28.4.1;
  - the latest: Python 3.14, pandas 3.1.x, pyarrow 26, Faker 40.
- Every push CI test leg installs by a fresh resolve of the bounds; all 12 legs are green.
- The dtype ruling rests on a measurement of 2026-10-24 (pandas 3.1.0, pyarrow 26.0.0, numpy 2.4.5, Python 3.12, 10M rows, median of 5 interleaved reps, load 5.3/8 cores; `.dadaia/tmp/main-thread/20261024/ns-vs-us/result.txt`), `us` against `ns`:

  | step | `us` | `ns` |
  |---|---|---|
  | from_pandas | 29.0 ms | 27.7 ms |
  | parquet | 257.1 ms | 280.1 ms |
  | csv | 846.2 ms | 841.2 ms |
  | to_pandas | 8.9 ms | 20.2 ms |
  | cast pass | none | 29.7 ms |
  | total | 1184.7 ms | 1190.4 ms |

  `ns` is not faster, so by the operator's rule the contract follows pandas (FR2).
- A SparkGenerator spec naming any of the four correlated methods is refused at validation, with one fix line. The four bodies are gone, and the net line count over `rand_engine/` is negative.
- Epoch seconds are computed once in `rand_engine/core/`.
- `specs/constitution.md` states the north star and the 2026-10-11 rulings with the operator's words.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law and dev loop | the constitution amendment; package bounds, classifiers and the minimal relock | FR6, FR1 |
| 2 — features | the pandas dtype contract; the Spark refusal; the epoch unification and the hotfix follow-ups | FR2, FR3, FR4 |
| 3 — promote-facing | the CI legs, which land only after waves 1–2 are green; compatibility docs and CHANGELOG; closure memory | FR5, FR7 |

## 3. Non-goals

- Next release (0.9.0 per the roadmap), right after 0.8.1 ships: `hardware-chunk-study` (runs when the machine is quiet: load 29.6/8 cores at 16:36Z), `memory-budget-chunked-output`, `stream-rate-per-microbatch`, `public-benchmark-page`, `docs-restructure`, `randspec-json-schema-generate-cli`, `adoption-measured`, the `native-core-research` staged plan (`.dadaia/tmp/main-thread/20261024/native-core-research.md`), and the `benchmarks/speed.py` peak, whose `tracemalloc` around `get_df` misses Arrow memory and writers (with the chunk study).
- The portfolio page stays in its own context (`library-pages-in-motion`).
- Python 3.10, and CI legs beyond the 12.
- Any new feature, method, key or runtime dependency.
- A pyarrow floor below 19.0.0. It would need test skips, which only the operator can order.
- Relocking `poetry.lock` to pandas 3. `verify:` keeps the lock stack.
- A reusable CI workflow. It would delete three matrix copies but rename the required checks, so it becomes a backlog proposal.
- Implementing the four correlated methods on Spark, seeding ordinary Spark columns, or any new Spark method or key.
- Any change to `StreamHandler`.
- Copying any ruling into the `## Principles` of `QUALITY.md` or `ARCHITECTURE.md`. That needs an accepted ADR.
- Rewording constitution text the rulings do not touch, invariant 12's "v0.6.4" included.

## 4. Requirements

### FR1 — 0.8.1 installs on today's stacks

Operator: "Cobrir o que está em uso (Recomendado)".

- AC1.1 (integration, the wheel METADATA test `tests/integrations/test_public_api.py`):
  - `Requires-Python` is `>=3.11`.
  - The Python classifiers are exactly 3.11, 3.12, 3.13 and 3.14.
  - `Requires-Dist` carries `numpy>=1.26` (no cap), `pandas>=2.2,<4` and `pyarrow>=19.0.0` (no cap).
  - The `faker` extra is `>=28.4.1`, with no cap.
- AC1.2 (unit, `tests/test_9_cli.py`): `project.requires-python == ">=3.11"`, and the asserted `tool.poetry.dependencies` literals are the FR1 bounds (`numpy`, `pandas`, `pyarrow`, and `faker` optional at `>=28.4.1`), changed under "Cobrir o que está em uso (Recomendado)".
- AC1.3 (no test; the command is the check): `poetry lock` on the widened bounds keeps faker 28.4.1, numpy 2.1.1, pandas 2.2.3, pyarrow 23.0.1 and pyspark 3.5.8; `poetry check --lock` passes. `verify:` is unchanged (no gate-cost ruling); the test group keeps `pyspark ^3.5.0` and `faker ^28.4.1`.
- AC1.4 (E2E, CI, proven by FR5): the floor and latest stacks of §2 install and pass.

### FR2 — The pandas dtype contract follows pandas

Operator: "uai, se possivel ns. See if for pyarrow is faster. If it is, we use it. if no, we use pandas." The §2 measurement shows `ns` is not faster, so the contract follows pandas:
- generated text columns are `string[pyarrow]` on every pandas;
- numeric columns keep the NumPy dtypes the methods return;
- datetime columns and transformer outputs take the dtype the installed pandas infers from plain Python values;
- the declared Arrow schema comes from the same pandas -> Arrow conversion the writer uses.

The deciders are `method_specs._constant_arrow_type`, `RandGenerator._column` and `RandGenerator.apply_embedded_transformers`.

- AC2.1 (integration, existing tests): text columns are `string[pyarrow]`, and numeric columns keep their 0.8.0 dtypes, on pandas 2.2 and 3.x.
- AC2.2 (integration, `tests/test_5_empty_schema.py`): for a datetime `constant`, naive and UTC-aware, the Arrow type of the size-0 Parquet equals the type written at size 4. That is `timestamp[ns]` on pandas 2.x and `timestamp[us]` on pandas 3.x. The hard-coded `ns` branch (`method_specs.py:87-93`) is gone.
- AC2.3 (unit and integration): a datetime column built from Python datetimes has the installed pandas' natural unit: `ns` on 2.x and `us` on 3.x. Four expected literals become per-pandas values:
  - the `constant` case `value7` in `tests/test_0_np_core.py`;
  - the `null_rate=1` `dates` case in `tests/test_2_data_generator.py`;
  - the two empty-schema cases.
- AC2.4 (unit, `tests/test_0_py_core.py`): a map-family level that is not all text, such as mixed types or text with `None`, is an `object` column holding its Python values, so `None` stays `None` on pandas 2.2 and 3.x. `test_distincts_map_non_text_level_keeps_object_dtype_and_values_as_080` passes unchanged.
- AC2.5 (integration, `tests/test_6_stream_objects.py`, a new RED case): a `dates` column with a `pd.Timestamp` transformer gives a datetime dtype, not `timestamp[us][pyarrow]`, and `stream_dict` yields it as text, on pandas 2.2 and 3.x. The fix is at the source, in `apply_embedded_transformers`, and `StreamHandler` is untouched.
- AC2.6 (integration, arrange steps only, asserts unchanged):
  - the seven datetime writer cases of `tests/test_5_files_write_batch.py` build their frames with an explicit `datetime64[ns]` unit;
  - the three string-subclass cases of `tests/test_6_stream_objects.py` build theirs from `object`, `StringDtype("python")` or object-category inputs.
- AC2.7 (integration, `tests/test_docs.py` runs every block):
  - `docs/3_WRITING_FILES.md:144-146` states that the CSV fraction follows the column's unit, with no "`ns` (the pandas default)".
  - `docs/1_DATA_GENERATOR.md:252` states the transformer dtype contract of AC2.5. Its executed `dtype == object` assert becomes the installed pandas' inference, never deleted.
- AC2.8 (no new test): `verify:` runs the lock's pandas 2.2.3, so each pandas-3 RED and GREEN step is a named scratch run on pandas 3.1.0, recorded in the job file; FR5 proves it on CI.

### FR3 — Spark refuses the four NULL methods

Operator: "Nada além disso (Recomendado)" and "Apagar os 4 métodos NULL". Ground: invariant 3.

- AC3.1 (unit, `tests/test_1_common_validator.py`, `tests/test_1_advanced_validator.py`): a SparkGenerator spec naming `distincts_map`, `distincts_multi_map`, `distincts_map_prop` or `complex_distincts` raises `SpecValidationError`. The message's fix line says to use `DataGenerator`.
  - The refusal is the existing `engines` check (`common_validator.py:227`); the CORRELATED warning branch (`:220-226`) is deleted.
  - `expected_spark` excludes CORRELATED.
- AC3.2 (no test; a deleted unit needs none): the four `SparkCore` bodies and their four `SparkGenerator.map_methods` entries are deleted. A grep of `rand_engine/` for `SparkCore.gen_distincts_map`, `gen_distincts_multi_map`, `gen_distincts_map_prop` and `SparkCore.gen_complex_distincts` returns 0 hits.
- AC3.3 (integration, `tests/test_docs.py`): the four rows of `docs/2_SPARK_GENERATOR.md` and `skills/rand-engine/SKILL.md` read `refused`.
  - The NULL paragraph, `:46-47` and `:82-83`, is deleted with its executable block.
  - The NULL sentence of `skills/rand-engine/SKILL.md:99` is deleted too.
  - No "NULL + warning" text remains in `docs/`, `skills/`, `README.md` or `llms.txt`.
- AC3.4 (unit, `tests/test_1_common_validator.py`; main-thread ruling): the NumPy-only refusal (`common_validator.py:229`), which the four methods now reach, names the method and the engine only. Its `in 0.7.0` text is deleted, and no version is added.

### FR4 — One epoch computation, and the hotfix follow-ups

Operator: "Unificar o cálculo de epoch". The intake items (a)–(d) of the release grill are requirements here.

- AC4.1 (unit and integration, existing tests): `NPCore.gen_unix_timestamps` and `SparkCore.gen_unix_timestamps` call one shared function that turns the two parsed bounds into epoch seconds. A grep of `rand_engine/core/` finds the epoch arithmetic once. Each engine keeps its own parsing, so no parsing behaviour changes.
- AC4.2 (integration, existing tests): the golden SHA-256 cases `unix_timestamps` and `dates` of `test_golden_seeded_output` pass with their literals unchanged, and so do the hotfix's pre-1970 and 1970-crossing cases on NumPy and Spark.
- AC4.3 (unit, `tests/test_0_spark_core.py:82`, intake (d)): the `1969-12-31..1970-01-02` Spark case also asserts that some value is negative (`t < 0`), as its NumPy twin does. It goes red on the reverted `1c3ddc2`.
- AC4.4 (no test; comment text, intake (c)): the comment at `rand_engine/core/_spark_core.py:102` in `SparkCore.gen_dates` no longer claims "years 1970..9999" (by-name approval in the Origin).
- AC4.5 (no test; ledger verb, intake (a)): `bugs.py update dates-before-1970-validate-then-raise` makes two changes:
  - `cause` no longer says `timestamp()` read naive values, since the base was UTC-aware;
  - `caused_by` becomes `none`, since the clamp is the operator's body `bf4b12d`.
  `bugs.py check` exits 0.
- AC4.6 (no test; record of invariant 4): this SPEC records the seed-contract revision of the hotfix. A `dates` or `unix_timestamps` range that crosses 1970 now draws over the whole `[start, end)`; 0.8.0 clamped it to 1970. A range wholly before 1970 generates; 0.8.0 raised `ValueError: high <= 0`. A range wholly after 1970 keeps its seeded values (AC4.2).

### FR5 — CI proves it on every push

- AC5.1 (E2E, CI; workflow YAML has no seam in the suite): `test_on_push.yml`, `pr_to_development.yml` and `pr_to_master.yml` each run 12 legs, 3 OS × Python 3.11–3.14. `auto_tag_publish_master.yml` runs Ubuntu × 3.11–3.14.
  - Every test leg installs by `pip install ".[faker]"` plus its test tools and pins, a fresh resolve of the package bounds. `poetry` stays for the build, docs, benchmarks and `verify:`.
  - The matrices are edited in place. Master branch protection requires no status check, operator verbatim: "Remover os 3 checks mortos (Recomendado)"; the main thread applied it via the GitHub API on 2026-10-24, and protection keeps 1 required review. The three removed contexts, `Run Tests (Python 3.10/3.11/3.12)`, came only from `auto_tag_publish_master.yml` (`pull_request: closed`), so they never reported on a PR. The PR test jobs and CI on push stay the nets. `--cov-fail-under=60` stays on `pr_to_development.yml`.
- AC5.2 (E2E, CI): the legs install these stacks.

  | leg | install |
  |---|---|
  | Ubuntu Python 3.11, the floor | `pandas==2.2.0 numpy==1.26.0 pyarrow==19.0.0 faker==28.4.1 "pyspark>=3.5,<4"` |
  | Python 3.11 on macOS and Windows | latest, with `pyspark>=3.5,<4` |
  | Python 3.12–3.14 | latest, with `pyspark>=4` |

  Spark tests keep skipping on Windows with Python 3.12 or later.
- AC5.3 (E2E, CI): on the first push carrying FR5, every leg is green. The floor leg's log prints the pinned versions, and a Python 3.14 leg prints pandas 3.x, pyarrow 26 and Faker 40.x. The run id is cited at review.
- AC5.4 (cost): measured base run `39472852277`: 12 legs, 2200 s sum, slowest 450 s (Python 3.10 Windows). Estimate with 3.10 gone: about 1849 s, slowest about 349 s. The runner's pip resolve of pandas 3, pyarrow 26 and pyspark 4.2 is unmeasured; the first push measures it and the review cites it.

### FR6 — The direction rulings in the constitution

Operator: "Confirmo todas (Recomendado)" (the 2026-10-11 rulings), "Velocidade e nicho (Recomendado)" and "Backlog + página pública (Recomendado)".

- AC6.1 (no test; law text): this is a direct amendment, whose writer per `specs/AGENTS.md:42` is `dd-product-engineer` under this approved SPEC. A new section lands verbatim between `## Purpose` and `## Invariants`, and no other line changes:

  ```markdown
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
  ```

- AC6.2 (no test): `## Principles` in `QUALITY.md` and in `ARCHITECTURE.md` gain no line, because a principle there needs an accepted ADR.

### FR7 — Version 0.8.1, compatibility docs, changelog and closure memory

Operator: "0.8.1 (Recomendado)". The version stays 0.8.1, though it drops Python 3.10 and refuses the four Spark NULL methods.

- AC7.1 (integration, `tests/test_docs.py`): `docs/compatibility.md` states:
  - Python 3.11–3.14, pandas `>=2.2,<4`, pyarrow `>=19`, numpy `>=1.26` and Faker uncapped;
  - Spark 3.5 and 4.x, with the Windows Spark skip;
  - the four correlated methods as refused on Spark, not NULL (`:31`, `:69`).

  `docs/2_SPARK_GENERATOR.md:7` names the same Python range.
- AC7.2 (integration, `tests/test_docs.py` dates every numeric header): the `## [0.8.1]` section of `CHANGELOG.md` gains three groups.
  - **Changed**: the supported bounds; and that a datetime column's unit follows the installed pandas, `us` on pandas 3, so the CSV fraction is six digits there.
  - **Removed**: Python 3.10; and the four correlated methods on Spark, now refused at validation where they returned NULL.
  - **Fixed**: `dates` and `unix_timestamps` before 1970 on NumPy and Spark, with the AC4.6 seed note.
- AC7.3 (closure memory pass, `pe`; invariant 11 in the same release):
  - `ARCHITECTURE.md` `## Tech Stack`: Python `>=3.11`, CI 3.11–3.14; NumPy `>=1.26`; pandas `>=2.2,<4`; PyArrow `>=19`; Faker `>=28.4.1`; PySpark 3.5 and 4.x on CI.
  - `QUALITY.md` `## Gates`: the matrix words and the fresh-resolve legs.
  - The atoms `generation-methods`, `spark-generator`, `rand-spec-grammar`, `writers-and-streaming` and `public-api`, stated as FR2–FR4 leave them.
- AC7.4 (closure, `pe`, shape 2 in the `wt-rc` reconcile, before the backlog exit sweep): the pyspark clause of the `compat-current-ecosystem` description becomes the PyPI fact: pyspark 4.2.0/4.1.x declare `pandas>=2.2.0`, 4.0.x `>=2.0.0`, 3.5.8 none (https://pypi.org/pypi/pyspark/4.2.0/json).

### Test changes the operator's rulings carry

- Under the compatibility ruling, the literals of AC1.1 and AC1.2 replace the 3.10 and caret values.
- Under the Spark ruling ("Nada além disso" + "Apagar os 4 métodos NULL"):
  - `test_validate_and_raise_advanced_method_only_warns` (from `ef1356c`) is replaced by the refusal test;
  - the NULL-column docs test is deleted, along with the `spark_outcome` "NULL + warning" vocabulary;
  - `expected_spark` excludes CORRELATED.
- Under the dtype ruling, the four datetime literals of AC2.3 become per-pandas values. The docs assert of AC2.7 follows the same ruling, and the main thread names it in that `test(...)` commit.
- Each `test(...)` commit names its ruling. Every other assert is kept, and nothing is skipped.

## Replaces

- `CommonValidator._validate_spark_column`: the CORRELATED warn-and-return branch is replaced by the existing `engines` refusal, whose `in 0.7.0` text is removed.
- The four `SparkCore` NULL bodies and their `SparkGenerator.map_methods` entries are removed.
- `_constant_arrow_type`: the hard-coded `timestamp("ns")` is replaced by the pandas -> Arrow conversion's type.
- `apply_embedded_transformers`: `apply` on the Arrow column is replaced by `apply` on a plain-object view.
- `RandGenerator._column`: a non-text Python list no longer passes to pandas' re-inference; it is an `object` column.
- The epoch line, duplicated in two `gen_unix_timestamps` bodies, is replaced by one shared function.
- CI test legs: `poetry install` from the lock is replaced by a fresh pip resolve with a floor leg and latest legs.
- `pyproject.toml`: the caret caps (`numpy<3`, `pandas<3`, `pyarrow<24`) and `faker<29` are replaced by the FR1 bounds, and Python 3.10 support is removed.
- Docs and skill: the "NULL + warning" vocabulary and "`ns` (the pandas default)" are removed.

## 5. Constraints and risks

| risk | control |
|---|---|
| The latest-stack legs are red until FR2 lands, and a red push CI on the work branch blocks every non-bug commit | FR5 lands last, after FR1–FR4 merge green; its pandas-3 proofs run first as named scratch runs (AC2.8) |
| Textual overlap: FR3 and FR4 both edit `_spark_core.py`, and FR2 and the hotfix tests share `tests/test_0_np_core.py` | the PLAN sequences them in one job or orders the edges |
| Renamed public text ("NULL + warning", dtype docs) | a read-only `dd-researcher` pre-mortem on the as-is consumer list precedes SPEC approval; the PLAN answers each hit |
| The same seeded spec writes `.000000000` on pandas 2 and `.000000` on pandas 3 for datetime columns | a documented consequence of following pandas (AC2.7, AC7.2); values are equal, so it is no seed change (invariant 4) |
| pyspark 4.2.0 warns `FutureWarning: PySpark does not yet fully support pandas >= 3` the 121 Spark tests passed on pyspark {3.5.8, 4.2.0} × pandas {2.2.3, 3.1.0}; the latest legs re-prove it on every push |

- The operator acts at promote: approving the PyPI publish in the GitHub environment `production` (invariant 13).

## 6. Open questions

none. Q1 (invariant 12 for the `SparkCore.gen_dates` comment line) is resolved: the operator answered "Aprovo (Recomendado)" on 2026-10-24, recorded in the Origin.
