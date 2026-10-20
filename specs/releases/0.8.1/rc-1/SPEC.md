# SPEC — Release: 0.8.1, candidate 1 (fast text methods, Arrow text columns, no rc publication)

**Status:** Draft
**Release ID:** 0.8.1
**Owner:** dd-product-engineer
**Opened:** 2026-10-20
**Origin:** operator-demand

- Demand: make the slow text methods fast with the same seeded values, give every generated text column the Arrow string type, and stop publishing release candidates.
- Sources: grill handoff `2026-10-20T025547Z-main-thread-0.8.1-grill` (summary confirmed by the operator: "confirmed. go ahead. move forward."); as-is review PLAN §1 (commit `2575e30`) and its handoff `2026-10-20T035714Z-dd-sw-engineer-sr-0.8.1-rc1-as-is`.
- Operator words carried: "go with Arrow and your prototypes"; "Every text column (Recommended)"; "to pypi we only deploy closed releases. and with manual approve. I must approve . you cannot publish to pypi without my approval. And no rc can be deployed on pypi or tagged on github."; "0.8.1. And we need to delete these rc publications. We cannot deploy RCs."
- Invariant 12: approving this SPEC is the operator's by-name approval of these v0.6.4 bodies, and of nothing else: `NPCore.gen_uuid4`, `NPCore.gen_ints_zfilled`, `NPCore.gen_dates`, `NPCore.gen_distincts`, `NPCore.gen_distincts_prop`, `PyCore.gen_complex_distincts`, `PyCore.gen_distincts_map`, `PyCore.gen_distincts_multi_map`, `PyCore.gen_distincts_map_prop`, and `PyCore.gen_distincts_untyped` (deleted). `NPCore.gen_constant` (text case) is named too, though it postdates v0.6.4. `StreamHandler` and every `SparkCore` body stay untouched. New bodies keep the operator's style: 2-space indentation, one-line guards, terse NumPy.
- Done outside the repo on 2026-10-20, not redone here: the operator deleted the 26 rc versions on PyPI; the main thread deleted 26 rc GitHub pre-releases with their tags plus the tags `0.5.4rc1a1` and `0.5.5rc1a1`, set the operator as required reviewer of the `production` environment, and disabled the workflow "Development - Auto Tag and Publish".

## Bug window review

The prior candidate, 0.8.0 rc-13, resolved no record. This table judges every resolved record in `specs/bugs/BUGS.jsonl` (11, 0 open) against the units this candidate touches. Each fix was found by its `fix(bugs)`/`refactor(bugs)` id line, else by its recorded `fix_sha`, and read with `git show`.

| bug | fix | found by | pattern hit | verdict | why |
|---|---|---|---|---|---|
| `validator-engine-schema-drift` | `01ffb21` | id line | none (net −64) | KEEP | it removed `gen_uuid4`'s ignored `length`; the uuid4 REBUILD keeps that signature |
| `spark-integers-max-exclusive` | `6691fb4` | id line | none | KEEP | `SparkCore` is out of scope |
| `method-registry-has-five-owners` | `4147b08` | id line | ≥ 2 fixes on the map seam beside it (archived 19, 22, 24, 25) | KEEP | its fix, one `METHODS` map, stays. The seam next to it, the per-row split in `generate_first_level`, is REBUILT by PLAN §1 for the speed demand. Its hardened contract test `puts_category_first` is kept and reshaped from rows to columns |
| `fk-parent-args-validates` | `7c3566b` | recorded sha | a second width decider | KEEP | judged REBUILD in 0.8.0 rc-1. `d6569d4` executed that, and `_spark_width_errors` now consults `width_beyond_double` |
| `int-zfilled-nonpositive-length-validates-then-raises`, `int-zfilled-length-above-18-validates-then-raises` | `4a95036` | recorded sha | ≥ 2 bugs on `int_zfilled` | KEEP | both fixes are in the validator's catalog rule (1..18). The body REBUILD keeps the same draw and leaves those bounds to the validator |
| `package-docstring-contradicts-pitch` | `fe09f54` | recorded sha | none | KEEP | untouched |
| `stream-trigger-frequency-annotated-int` | `9cfd121` | recorded sha | none | KEEP | untouched |
| `reference-test-self-referential` | `adc66be` | recorded sha | the fix changes a test | KEEP | the test was the bug; untouched |
| `pipeline-doc-matrix-stale` | `301dd32` | id line | deleted functionality | KEEP | no consumer |
| `preview-faker-install-guidance` | `41df169` | id line | none | KEEP | untouched |

- No REBUILD verdict, so this table adds no work. The PLAN's REBUILD rows come from the demand and from the archived seam history, not from these fixes.
- `docs-preview-deploy-fails-after-stable` is registered and fixed in its own hotfix lane (`wt-backlog-docs-preview-deploy-fails-after-stable`). It is outside this candidate.

## 1. Problem

- Eight text methods are the slowest rows of the CI benchmark at commit `bbc9847`, 10M rows: uuid4 0.374, complex_distincts 0.906, int_zfilled 3.589, dates 3.650, distincts_multi_map 4.188, distincts_map 4.600, distincts_map_prop 5.014 and distincts_prop 13.796 rows/µs. The cost is a Python string per row: `uuid.UUID` per row, `np.char.zfill`, `view("<U")`, per-row tuple splits, and `<U` arrays that pandas turns into 10M Python objects.
- Text columns are NumPy `<U` or `object` with `None` nulls, so every frame pays to build those objects.
- `auto_tag_publish_development.yml` published an rc to PyPI, with a tag and a GitHub pre-release, on every PR merged into `development`. It did so after the 0.8.0 final too (`0.8.0rc7`, `0.8.0rc8`). The master workflow looks up "the latest RC", tags before it publishes, and writes "Promoted from Release Candidate". No rule forbade any of it: invariant 6 only requires Trusted Publishing.
- The benchmark A/B base is the commit of the committed `docs/benchmarks.json`, a mid-release head, not a release.

## 2. Measurable goals

- Seeded values equal 0.8.0 for every method: the 19 `test_golden_seeded_output` cases and `test_golden_multi_column_draw_order` pass with their SHA-256 literals unchanged.
- On the CI same-runner A/B against the closed 0.8.0 release, each method of FR1 is at least 2x faster at 10M rows and faster at 1M. Locally at 3M rows (PLAN M6, best of 3) the measured ratios ranged from 4.75x (distincts) to 28x (dates).
- Every generated all-text column has dtype `pd.ArrowDtype(pa.string())`. pandas shows it as `string[pyarrow]`.
- No workflow can publish, tag or GitHub-release an rc. A final is tagged only after its operator-approved publish.
- The release's net line count over `rand_engine/` and `.github/` is negative. The deleted development workflow alone is 412 lines.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law and dev loop | constitution and Tech Stack amendments; delete the rc path; rebuild the master workflow; A/B base = highest closed-release tag (the speed ACs measure against it) | FR3, FR4 |
| 2 — shared foundation | the one text-column decider, the fixed-width and pool builders, the nulls disjunct, the column-wise assembly of multi-column methods | FR2 |
| 3 — features | the ten method bodies, the `gen_distincts_untyped` deletion, the approved test changes, the Spark test | FR1, FR2, FR5 |
| 4 — promote-facing | docs, version, CHANGELOG, benchmark record | FR2, FR6 |

## 3. Non-goals

- `SparkGenerator` and every `SparkCore` body.
- Speed of `dates` with time directives (`%H %M %S %f`): the values stay identical, but no speedup is claimed. The prototype reached 1.3x–2.1x (follow-up F2).
- pandas 3. The locked pandas 2.2.3 and the checked 2.3.3 are the supported evidence.
- The Docs preview bug `docs-preview-deploy-fails-after-stable`, which has its own hotfix lane.
- `comparison.yml`'s pin to the published 0.8.0 wheel, with its four sibling files. The pin stays until 0.8.1 ships (follow-up F1).
- Any new runtime dependency: pyarrow `^23.0.1` and pandas `^2.2.2` are already runtime dependencies.
- Any new gate, or any change to the 1.3 regression limit or the modifier limits.

## 4. Requirements

### FR1 — The same values, faster

For each method below, the same seed gives the same values as 0.8.0. The guard is the method's golden SHA-256 case (integration, `tests/test_2_data_generator.py` `test_golden_seeded_output`), with its literal unchanged. The speed proof is its row on the CI same-runner A/B against base `0.8.0` (E2E, `benchmarks.yml`): head at least 2x faster at 10M rows and faster at 1M, recorded in `docs/BENCHMARKS.md`.

| AC | method | scope of the claim |
|---|---|---|
| AC1.1 | `gen_uuid4` | RFC 4122 version and variant bits unchanged; the `rng.bytes(16 * size)` draw is consumed identically |
| AC1.2 | `gen_ints_zfilled` | lengths 1..18 (the validator's bounds); the same `rng.integers(0, 10**length, size, int64)` draw |
| AC1.3 | `gen_dates` | speedup for date-only formats only (the benchmark row is `%Y-%m-%d`). Values stay identical for every format, time directives, `%f`, UTC and years past 3000 included: the existing per-row `strftime` oracle tests (unit, `tests/test_0_np_core.py`) stay green |
| AC1.4 | `gen_complex_distincts` | the CI IP pattern; integer, float, bool and big-int template parts render the same text as 0.8.0 |
| AC1.5 | `gen_distincts` | text pools; numeric pools keep their numeric dtype and values |
| AC1.6 | `gen_distincts_prop` | the drawn indexes equal `rng.choice`'s bit for bit (PLAN M5) |
| AC1.7 | `gen_distincts_map` | category first, then value; the column order equals 0.8.0 |
| AC1.8 | `gen_distincts_multi_map` | category followed by one column per level; `test_golden_multi_column_draw_order` unchanged |
| AC1.9 | `gen_distincts_map_prop` | weights and column order equal 0.8.0 |
| AC1.10 | `gen_constant` | the text case. The benchmark `constant` sample becomes a text value, because its numeric case is unchanged code; numeric and `None` constants keep their dtype and draw nothing |

- AC1.11 (no test; a deleted unit needs none): `PyCore.gen_distincts_untyped` is deleted, and a grep of `rand_engine/` and `tests/` for it returns 0 hits.
- AC1.12 (unit): a map-family level whose pool is not all text, e.g. mixed int and str, keeps pandas' own inference (`object`), as in 0.8.0.

### FR2 — Every generated text column is Arrow

Decision: `pd.ArrowDtype(pa.string())`, shown as `string[pyarrow]`. Evidence (PLAN M1): `StringDtype("pyarrow")` writes `large_string`, which the CSV, JSON and Parquet writers refuse as schema drift against the catalog's `pa.string()` (3 of 3 formats). `ArrowDtype(pa.string())` writes `string` and passes all three, so invariant 3 and the writers stay untouched.

- AC2.1 (integration): through `DataGenerator.get_df`, a column is `string[pyarrow]` when every generated value is text. That covers `uuid4`, `int_zfilled`, `dates`, `complex_distincts`, the three map methods, `distincts`/`distincts_prop`/`constant` with text values, `pk`/`fk` with a text `format`, and the text, large_text, day32, day64 and moment columns of `RandSpecs.from_schema`. Numeric, boolean, datetime and mixed-type columns keep their 0.8.0 dtype.
- AC2.2 (integration): `null_rate` on a text column writes `pd.NA` and the column stays `string[pyarrow]`. In 0.8.0 the column became `object` with `None`. Nulls of other dtypes are unchanged. No fallback to `object` exists (ruling R1).
- AC2.3 (integration): `anomaly_rate` on a text column keeps `string[pyarrow]`.
- AC2.4 (integration, existing tests): `stream_dict` records carry `None` for a text null. The JSON writer writes `null`. SQLite stores `NULL`.
- AC2.5 (integration): for one seeded spec covering every FR1 method, the CSV and JSON files hash to SHA-256 literals recorded from 0.8.0, so their bytes are unchanged.
- AC2.6 (integration): Parquet values and the BYTE_ARRAY/String logical type are unchanged. The embedded pandas/Arrow schema metadata bytes differ (PLAN M2). Read back with `read_parquet(..., dtype_backend="pyarrow")`, a text column equals the frame in values and dtype. Under the default read, the values alone are equal. `docs/3_WRITING_FILES.md:44` is narrowed to that statement.
- AC2.7 (no new test; the result is pandas' `Series.apply`, not a rand-engine contract): the docs state that an embedded transformer's output dtype is whatever the transformer returns.
- AC2.8 (integration, on CI's Temurin 17 JVM; ruling R1, §6): `spark.createDataFrame` of a frame whose text column holds `pd.NA` yields a string column with SQL NULLs when Spark's Arrow option (`spark.sql.execution.arrow.pyspark.enabled`) is on. With it off, a frame without text nulls converts as in 0.8.0, and a frame with `pd.NA` text nulls raises the error the docs name. The docs (AC2.9) and the databricks starter `rand_engine/cases/databricks.py.txt` tell the user to enable Spark's Arrow option.
- AC2.9 (integration, `tests/test_docs.py` executes every block): the docs state the type once, in the method table or the null-rate section. They cover `string[pyarrow]`, `pd.NA` nulls, Arrow booleans from `.str.*`, the Parquet read-back rule and the note to enable Spark's Arrow option before `spark.createDataFrame`, across `docs/1_DATA_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/5_RECIPES.md`, `README.md`, `llms.txt`, `skills/rand-engine/SKILL.md` and the `data_generator.py` docstrings PLAN §1 lists.

### FR3 — Only closed releases reach PyPI, each approved by the operator

- AC3.1 (no test; a deleted file): `.github/workflows/auto_tag_publish_development.yml` is deleted. A grep of `.github/`, `docs/`, `README.md` and `tests/` for its name returns 0 hits.
- AC3.2 (source review; a test that mirrors `needs:` text would test YAML, not behaviour): `auto_tag_publish_master.yml` is changed as follows.
  - `find_rc`, the `latest_rc` outputs and every "Promoted from Release Candidate"/RC text are deleted.
  - The no-rc-suffix guard stays.
  - Jobs run in this order: build, then `publish_pypi` (environment `production`), then `create_tag`, then `create_github_release`.
- AC3.3 (E2E, CI): the `benchmarks.yml` A/B base is the highest bare `M.m.p` tag, which resolves to `0.8.0` today. The job summary names the base commit of `0.8.0`.
- AC3.4 (integration, `tests/test_docs.py`): the rc-wheel clause of `docs/getting-started.md:53` is gone; the rest of that paragraph stays. No rc version string remains in `docs/`, `README.md`, `llms.txt` or `skills/`.
- AC3.5 (E2E observation): merging this candidate into `development` creates no tag, no PyPI version and no GitHub release.

### FR4 — Constitution and memory amendments

The text below lands verbatim, in the same change as the code it governs, as a `pe` task of that job.

- AC4.1 (no test; law text) — invariant 10 reads: "The core generates data with Python, NumPy, pandas and PyArrow alone: Spark, Faker, a message broker or a database server is never required to generate data."
- AC4.2 (no test; memory text) — per invariant 11, two lines of `specs/memory/ARCHITECTURE.md` `## Tech Stack` change:
  - PyArrow: "PyArrow `^23.0` — the generated text column type (`pd.ArrowDtype(pa.string())`) and its builders, CSV and Parquet conversion/output, and Arrow-schema RandSpec construction."
  - GitHub Actions: "GitHub Actions — test matrix, advisory security scans, same-runner A/B regression benchmarks against the latest closed release, a non-gating isolated cross-library observation, publishing of closed releases through PyPI Trusted Publishing after the operator approves the `production` environment, and an isolated docs build with a guarded GitHub Pages deploy."
- AC4.3 (no test; law text) — new invariant 13: "PyPI receives only closed releases, each published after the operator approves it through the GitHub environment `production`; no release candidate is published to PyPI, tagged or released on GitHub, and a release's tag is created only after its approved publish. The required-reviewer setting lives outside the repo and is held by the operator."
- AC4.4 (no test; law text): invariant 12's by-name approval is the Origin block of this SPEC. The invariant's text is unchanged.
- AC4.5 (closure memory pass): `QUALITY.md` loses the development publish gate line; its master line becomes publish after operator approval, then tag, then GitHub release. The atoms PLAN §1 lists state the Arrow text type and `pd.NA` text nulls, and give the benchmark base as the latest closed-release tag. The constant atom's "natural pandas dtype" sentence names `string[pyarrow]` for text.

### FR5 — Product-contract test changes the operator approves with this SPEC

- AC5.1 (reviewer diff check): only these tests change, each per its row in PLAN §1 "Tests that pin the old text type":
  - the tests that pin ndarray, `np.str_`, `object`, `None` or row tuples, 48 failing on the prototype across `tests/test_0_np_core.py`, `tests/test_0_py_core.py`, `tests/test_2_data_generator.py` and `tests/test_4_rand_specs_helpers.py`;
  - the five `gen_distincts_untyped` tests (`tests/test_0_py_core.py:131,141,150,315,323`), which are deleted with that unit;
  - `tests/test_benchmarks.py:307-316`, re-pinned at the final benchmark record.
- AC5.2 (reviewer diff check): every literal value assert is kept. A changed assert swaps the container or type only, and nothing is skipped. The golden SHA-256 literals do not change.

### FR6 — Version 0.8.1 and its changelog

- The operator chose a patch knowingly. The question offered 0.9.0 as recommended, citing the visible column type change, and the operator answered verbatim: "0.8.1. And we need to delete these rc publications. We cannot deploy RCs."
- AC6.1 (no test; a test of the literal would only mirror `pyproject.toml`): `pyproject.toml` version is `0.8.1`, and `poetry version -s` prints it.
- AC6.2 (no test; prose): `CHANGELOG.md` gains `## [0.8.1]`.
  - Under **Changed**: text columns are `string[pyarrow]`; text nulls are `pd.NA`; Parquet metadata bytes and the default read-back dtype differ; the text methods are faster with the same seeded values.
  - Under **Removed**: release-candidate publication to PyPI, tags and GitHub pre-releases.
  - No behaviour change is listed under Fixed. The 0.8.0 section is not edited.

## Replaces

- `auto_tag_publish_development.yml`: rc publication on every merge into `development` is removed.
- `PyCore.gen_distincts_untyped`: the row-list draw is removed.
- `docs/getting-started.md:53`: the public reference to the `0.8.0rc4` wheel is removed.
- `generate_first_level`: the per-row split `[val[i] for val in values]` is replaced by one column per level.
- The map family: tuple rows indexed per drawn row are replaced by one index draw and a take per level.
- `gen_complex_distincts`: per-row 1-char lists and pairwise `astype(str)` adds are replaced by one join pass.
- `gen_uuid4`: `str(uuid.UUID(...))` per row is replaced by one hex pass into a fixed-width Arrow column.
- `gen_ints_zfilled`: `astype(str)` plus `np.char.zfill` is replaced by integer-math digits into an Arrow buffer.
- `gen_dates`: the `uint32` code matrix with `view("<U")` is replaced by fixed-width UTF-8 rows; date-only formats get a per-day table.
- `auto_tag_publish_master.yml`: the RC lookup, the "Promoted from RC" text and tag-before-publish are replaced by publish, then tag, then release.

## 5. Constraints and risks

| risk | control |
|---|---|
| R2 pandas 2.3.x and pyarrow range: `is_string_dtype(ArrowDtype(string))` differs across versions | after the `_assign_nulls` edit nothing depends on it; 2.2.3 and 2.3.3 were run |
| R3 Arrow's 2 GiB offset limit on huge text columns | the fixed-width builder chunks below it; a RED test pins a multi-chunk case through a small chunk size |
| R4 publish succeeds, then the tag push fails | agent default, unruled: recover with GitHub's "Re-run failed jobs", which reruns only the tag and release jobs; the publish job is never rerun |
| the benchmark `constant` sample turns text | its numeric case is unchanged code; the A/B must measure the changed case (AC1.10) |
| sequencing | the Docs hotfix lands in its own lane; the comparison pin moves only at the 0.8.1 publication (F1) |

Operator acts outside the repo (R5), never done by an agent:

- the operator removes the PyPI Trusted Publisher entry that names `auto_tag_publish_development.yml`;
- once the file is gone, the main thread deletes the GitHub environment `development`.

## 6. Open questions

None. The ruling on R1 is recorded below.

- **R1, ruled (a) by the operator, 2026-10-20.** A text column with `null_rate` holds `pd.NA`. `spark.createDataFrame(pdf)` fails with `CANNOT_MERGE_TYPE` when Spark's Arrow option is off (pyspark 3.5.8, PLAN M4); 0.8.0 worked, with `None`. Options offered: (a) keep `pd.NA` and Arrow, docs and the databricks starter say to enable Spark's Arrow option, a Java-17 CI test proves both paths; (b) fall back to `None`/`object` on nulled text; (c) only the databricks starter converts `pd.NA` to `None`. The operator, verbatim: "Accept + document + CI proof (Recommended)". AC2.2, AC2.8 and AC2.9 carry it.
