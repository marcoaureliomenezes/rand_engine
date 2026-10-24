# PLAN — Release: 0.8.1, candidate 2

**Status:** Draft
**Release ID:** 0.8.1
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-2/SPEC.md` (ac54c6d)

Sources: as-is review `.dadaia/handoff/rand-engine/2026-10-24T165850Z-dd-sw-engineer-sr-rc2-as-is-review`, release grill `2026-10-24T170504Z-main-thread-grill-rc2`, SPEC handoff `2026-10-24T171457Z-dd-product-engineer-rc2-spec`. Tree `worktrees/rand-engine/0.8.1/rc-2/wt-rc`; the hotfix `1c3ddc2` has landed.

## 1. As-is review

Bug history = `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>`. Every bug named is `resolved`, `caused_by: none`, so the ledger makes no REBUILD due. A unit with no id-line commit has a coarse trail (squashed history).

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `pyproject.toml:8,14-17,36-40,25` | `requires-python >=3.10`; classifiers 3.10-3.13; carets `numpy ^2.1.1`, `pandas ^2.2.2`, `pyarrow ^23.0.1`; extra `faker >=28.4.1,<29` | 1 (`unused-runtime-deps-shipped`, KEEP) | UPDATE | the caps make 0.8.0 unresolvable with pandas>=3, pyarrow>=24, faker>=29 |
| `poetry.lock` | faker 28.4.1, numpy 2.1.1, pandas 2.2.3, pyarrow 23.0.1, pyspark 3.5.8 | same 1 | UPDATE (minimal) | `poetry lock` on the widened bounds keeps all five versions, so `verify:` keeps its stack |
| `.github/workflows/test_on_push.yml:42-80` | 3 OS x py 3.10-3.13, every leg `poetry install` from the lock | 1 (`ci-summary-commit-message-shell-injection`, KEEP) | REBUILD (matrix + install step) | the unit's contract (one locked stack) contradicts the demand: no leg resolves the `pyproject.toml` bounds |
| `.github/workflows/pr_to_development.yml:150-215` | same matrix + `--cov-fail-under=60`; `test_package_build` :226-300 already does a fresh wheel resolve | 2 (+`codecov-upload-blocks-ci`, KEEP) | REBUILD test job; KEEP `test_package_build` | the wheel job only could not reach pandas 3 because of the caps |
| `.github/workflows/pr_to_master.yml:29-100` | same matrix + coverage | 2 (same ids) | REBUILD test job | copy of the two above |
| `.github/workflows/auto_tag_publish_master.yml:57-78` | publish gate ubuntu x py 3.10-3.13 from the lock | 0 | UPDATE | only the Python list and install step move |
| `rand_engine/validators/method_specs.py:82-92` `_constant_arrow_type` | for a datetime `constant` returns the hard-coded `pa.timestamp("ns")` | 0 id-line commits | REBUILD (net negative) | pandas 3 builds `datetime64[us]`, so declared (ns) and written (us) schemas differ: size 0 `timestamp[ns]`, size 4 `timestamp[us]` |
| `rand_engine/main/_rand_generator.py:35-41` `_column` | all-str list/array becomes `string[pyarrow]`; other lists pass to pandas | 1 (`method-registry-has-five-owners`, a REBUILD, no child bug) | UPDATE | pandas 3 re-infers `str`/NaN for str+None; 0.8.0 gave `object`/`None` |
| `_rand_generator.py:62-70` `apply_embedded_transformers` | `df[col].apply(transformer)` on the Arrow text column | same 1 | UPDATE (one expression) | pandas 3 returns Arrow-backed results for Arrow input; on an object view both majors agree |
| `_rand_generator.py:101-122,164-180` `_scalar_preserves_dtype`, `_assign_nulls` | dtype-driven nulls | same 1 | KEEP | handle ArrowDtype and NumPy dtypes; the `null_rate=1` failure is only an expected literal |
| `rand_engine/file_handlers/file_handler.py:56-70,90-92,186-191` | pandas -> Arrow by `pa.Table.from_pandas`; CSV fraction by the column unit | 0 id-line commits | KEEP | `docs/3_WRITING_FILES.md:144-146` documents the unit-driven fraction; the 9 writer failures are test inputs |
| `rand_engine/utils/stream_handler.py:8-17` `convert_dt_to_str` (operator code, invariant 12) | `'datetime64' in str(dtype)` | 0 | KEEP | misses `timestamp[us][pyarrow]`; Job 4 removes the library's own source of such a column; never edited |
| `rand_engine/validators/common_validator.py:176-234` `_validate_spark_column`, branch :220-226; message :229 | CORRELATED: warn and `return []`; refusal text carries `in 0.7.0` | 3 (`date-format-required-but-docs-omit-it`, `validator-engine-schema-drift`, `validator-warnings-raised-as-errors`) | UPDATE = DELETE the 7-line branch and `in 0.7.0` | invariant 3; the four methods carry `engines=(NUMPY,)` (`method_specs.py:452-493`), so the existing refusal at :227 catches them. The branch went error -> warning (`ef1356c`) -> refusal by ruling: its cause is a validator accepting what no engine runs |
| `rand_engine/main/spark_generator.py:107-110` | four `map_methods` entries | 1 (`validator-engine-schema-drift`) | DELETE 4 entries | unreachable once validation refuses |
| `rand_engine/core/_spark_core.py:111-144` | four `F.lit(None)` bodies | 5 file-level, none on these four | DELETE (by-name approval, invariant 12) | SPEC FR3 |
| `rand_engine/core/_np_core.py:231`, `_spark_core.py:93` `gen_unix_timestamps` | the same epoch line twice | 3 (`97abd63`+`896cd3d` before, `dates-before-1970-validate-then-raise` `1c3ddc2` after) | UPDATE = DELETE one copy | duplicated decider: every date defect needed two fixes. The copies diverged between `97abd63` (NumPy fixed) and `896cd3d` (Spark fixed); today they are equal. By-name approval, invariant 12 |
| `rand_engine/core/_spark_core.py:102` comment in `gen_dates` | "years 1970..9999", false since the hotfix | 0 | UPDATE, conditional | needs the by-name approval of SPEC §6 Q1 |
| `tests/test_0_spark_core.py:82` | the 1969-12-31..1970-01-02 case passes on the reverted `1c3ddc2` | 1 (same hotfix) | UPDATE (one assert, tighter) | NumPy twin asserts `t < 0` |
| `specs/bugs/BUGS.jsonl` `dates-before-1970-validate-then-raise` | cause says `timestamp()` read naive values; `caused_by` names a task | — | UPDATE by `bugs.py update` | the base was UTC-aware; the clamp is the operator's body `bf4b12d` |
| 20 failing cases on pandas 3.1.0 across `test_0_np_core`, `test_0_py_core`, `test_2_data_generator`, `test_5_files_write_batch`, `test_6_stream_objects`, `test_docs`, `test_1_common_validator`, `test_5_empty_schema` | see the classification below | ids in the ledger slice | UPDATE | arrange steps and per-pandas literals; no assert loosened |
| `docs/1_DATA_GENERATOR.md:252`, `docs/3_WRITING_FILES.md:144-146`, `docs/2_SPARK_GENERATOR.md:7,44-47,66-69,82-83`, `docs/compatibility.md:5-6,16,28-31,69`, `skills/rand-engine/SKILL.md:89-92,99`, `CHANGELOG.md` | pandas-2 dtype claim; "`ns` (the pandas default)"; "NULL + warning"; Python 3.10-3.13 | `1_DATA_GENERATOR` 2, `3_WRITING_FILES` 1 | UPDATE | consumers of the changed vocabulary |
| `specs/constitution.md` | invariants 1-13 | 0 | UPDATE (direct amendment) | AC6.1 |

The 20 failures by cause: C1 datetime unit (9 writer cases, 1 `constant` literal: test assumptions); C1b declared schema (2 empty-schema cases: product); C2 `apply` on Arrow input (1 `null_rate` case + 5 docs cases through one assert: product); C3 `str` dtype (1: product); C4 string subclass (3: test assumptions). One break hides outside the 20: the `pd.Timestamp` transformer through `StreamHandler`.

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| declared Arrow type of a datetime `constant` | `method_specs._constant_arrow_type`, asking the pandas -> Arrow conversion the writer uses (`file_handler._arrow_table`) | `data_generator._file_seam`, empty-table writers | the hard-coded `pa.timestamp("ns")` branch (`method_specs.py:87-93`) |
| dtype of a generated Python-object column | `RandGenerator._column` | `generate_first_level` | none |
| dtype of a transformer's output | `RandGenerator.apply_embedded_transformers`: pandas' own inference on a plain Python return | `docs/1_DATA_GENERATOR.md` | the docs claim `dtype == object` (:252) |
| unit of a naive timestamp in written text | the column's own dtype unit; `file_handler.py` writes what the frame holds | tests, `docs/3_WRITING_FILES.md` | the words "`ns` (the pandas default)" |
| does SparkGenerator accept method M | `METHOD_CATALOG[M].engines` read by `CommonValidator._validate_spark_column` | `SparkGenerator.__init__`, docs table, SKILL.md table | the CORRELATED warn branch, 4 `map_methods` entries, 4 `SparkCore` bodies |
| epoch seconds of two parsed bounds | one function in `rand_engine/core/_np_core.py` beside `_parse_date_bound` (the module `_spark_core.py` already imports from) | `NPCore.gen_unix_timestamps`, `SparkCore.gen_unix_timestamps` | the duplicated line `_np_core.py:231` / `_spark_core.py:93` |
| supported Python and dependency range | `pyproject.toml` | wheel METADATA test, `tests/test_9_cli.py`, ARCHITECTURE Tech Stack, `docs/compatibility.md` | the carets and the `<29` cap |
| which stacks CI proves | the matrices of the four workflows (four copies, already divergent) | QUALITY Gates | the lock as the only tested stack |
| north star and direction rulings | `specs/constitution.md` | `QUALITY.md`, `tests/AGENTS.md` | none |

### 1.2 Design choices the jobs carry

- Epoch: the new function takes the two parsed `datetime` bounds and returns the two integer epoch seconds, the exact expression of today's line. Parsing stays in each engine (`_parse_date_bound` on NumPy, `strptime` on Spark). `timedelta` leaves `_spark_core.py`'s import when it becomes unused. Net lines over both files at most 0.
- `_constant_arrow_type`: only the timestamp branch changes (ask pandas -> Arrow for the type); the `pa.scalar(value).type` path of every other value stays. The branch shrinks.
- `_column`: the narrowest pin. A list or array pandas 3 would re-infer as `str` while `infer_dtype(skipna=False)` is not `"string"` (a str+None or mixed list) becomes an `object` array; numeric, boolean and datetime lists keep pandas' own inference (AC2.1: numeric dtypes unchanged).
- `apply_embedded_transformers`: `apply` runs on a plain-object view of the column; the result takes pandas' inference on both majors.

### 1.3 Pre-mortem hits (read-only `dd-researcher`, HEAD ac54c6d)

| hit | answer | task |
|---|---|---|
| C1 `_spark_core.py:111-144`, `spark_generator.py:107-110` deleted together | two tasks, one job, serial: entries then bodies; no commit leaves a map entry without its body | J3.T4 |
| C1 warn branch `common_validator.py:220-226`; refusal `:227-229` loses `in 0.7.0` | deleted; message names method and engine only | J3.T3 (tests J3.T1) |
| C1 `tests/test_1_common_validator.py:226-228` asserts `UserWarning` | replaced by a `SpecValidationError` test; `test(...)` commit names the Spark ruling | J3.T1 |
| C1 `tests/test_1_advanced_validator.py:559-564` `expected_spark` | excludes CORRELATED | J3.T1 |
| C1 `tests/test_docs.py:109-138,347-348` `spark_outcome` | vocabulary yes/refused | J3.T2 |
| C1 `tests/test_docs.py:410-445` NULL-column docs test | deleted under the ruling, named in the commit | J3.T2 |
| C1 `docs/2_SPARK_GENERATOR.md:42-47,66-69,82-98` | rows read `refused`; the NULL paragraph goes; the executable block becomes a refusal example that `test_docs` runs | J3.T5 |
| C1 `docs/compatibility.md:29-31,69`, `skills/rand-engine/SKILL.md:89-92,99` | rows `refused`, NULL sentence deleted | J3.T5 |
| C1 memory atoms `spark-generator.md:24`, `index.md:109`, `catalog.json:95`, `rand-spec-grammar.md:23` | closure memory pass | Reconciliation step 1 |
| C1 `derived-from` hashes (`2_SPARK_GENERATOR.md:29,42,43,149`, `4_CONSTRAINTS.md:133`, `1_DATA_GENERATOR.md:53`, `5_RECIPES.md:7`); nothing checks them | explicit closure item: re-stamp them after the atom edits, grep every `derived-from` in `docs/` | Reconciliation step 2 |
| C2 `method_specs.py:82-93` ns branch (consumer `:447`) | branch deleted; consumer re-read in the task | J4.T4 |
| C2 literals `test_5_empty_schema.py:213-218`, `test_0_np_core.py:714`, `test_2_data_generator.py:489` | per-pandas values via one helper in `tests/conftest.py` | J4.T3 |
| C2 `_rand_generator.py:36-41,51-53,62-70` (caller `data_generator.py:81`); `test_0_py_core.py:396-399` unchanged | `_column` and the object view; that test is a pass-unchanged gate on 2.2.3 and 3.1.0 | J4.T5 |
| C2 `stream_handler.py:8-12` (caller `data_generator.py:279`) | RED case first, fix at the source; `StreamHandler` untouched | J4.T1, J4.T5 |
| C2 `docs/1_DATA_GENERATOR.md:252`, `docs/3_WRITING_FILES.md:144` | assert replaced (never deleted); wording reworded | J4.T6 |
| C2 7 writer cases `test_5_files_write_batch.py` | explicit `datetime64[ns]` in the arrange step | J4.T2 |
| C3 `pyproject.toml:8,14,28,38-40`, `test_public_api.py:474-478`, `test_9_cli.py:299`, `poetry.lock` | the lock is relocked in J2.T2 with `poetry check --lock` | J2.T1, J2.T2 |
| C3 "3.10–3.13" claims in `docs/compatibility.md:5-6,16`, `docs/2_SPARK_GENERATOR.md:7` | rewritten | J5.T2 |
| C3 `public-api.md:41`, `spark-generator.md:16`, `ARCHITECTURE.md:20`, `QUALITY.md:32,36` | closure, invariant 11 | Reconciliation step 1 |
| C3 root `requirements.txt` (pandas==2.2.2, pyarrow==23.0.1) | no task regenerates it: `pr_to_development.yml:94` rewrites it in CI with `poetry export`, nothing reads the tracked copy, and it was already stale against the lock (pandas 2.2.3). Reported as an intake finding, out of scope | none |
| C4 workflows `test_on_push.yml:45,86-88`, `pr_to_development.yml:156,195`, `pr_to_master.yml:34,73`, `auto_tag_publish_master.yml:57,63,77` | matrices edited in place; coverage at `pr_to_master.yml:83` is keyed on 3.12, so every matrix keeps a 3.12 leg | J5.T4 |
| C4 master branch protection requires `Run Tests (Python 3.10)`, `(3.11)`, `(3.12)`, which only `auto_tag_publish_master.yml:57` emits, after the merge (`pull_request: closed`); the gate is dead today | operator act before the master PR, ruling pending; AC5.1's words "required-check names unchanged" are reworded to match the ruling at the SPEC approval. J5.T4 keeps names `Run Tests (Python 3.11)` and `(3.12)` and drops `(3.10)` | operator, then J5.T4 |
| C5 `_np_core.py:229-236` (caller `:240`), `_spark_core.py:81-98` (caller `:101`), `spark_generator.py:103`, `_py_core.py:83` | the shared function keeps both signatures; the callers are not edited; the seeded identity proof covers them | J3.T7 |
| C5 `_spark_core.py:102` | waits on Q1 | J3.T8 |
| C5 asserts `test_0_np_core.py:166-176,385-390,437,478,500`, `test_0_spark_core.py:73,84-117` | kept as they are; AC4.3 adds `t < 0` | J3.T6, J3.T7 |

No external dependent of the Spark methods or of Python 3.10 was found.

## DAG

Waves follow the SPEC ranking: 1 law and dev loop, 2 features, 3 promote-facing. Jobs in one wave write disjoint files. Job 3 holds FR3 and FR4 together because both write `rand_engine/core/_spark_core.py`; its tasks are serial. Job 5 is last: its CI legs go green only after Jobs 2, 3 and 4, and a red push CI on the work branch blocks every non-bug commit.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `specs/constitution.md` |
| Job 2 | — | 1 | `tests/integrations/test_public_api.py`, `tests/test_9_cli.py`, `pyproject.toml`, `poetry.lock` |
| Job 3 | — | 2 | `tests/test_1_common_validator.py`, `tests/test_1_advanced_validator.py`, `tests/test_docs.py`, `tests/test_0_spark_core.py`, `rand_engine/validators/common_validator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/core/_spark_core.py`, `rand_engine/core/_np_core.py`, `docs/2_SPARK_GENERATOR.md`, `skills/rand-engine/SKILL.md`, `docs/compatibility.md`, `specs/bugs/BUGS.jsonl` |
| Job 4 | — | 2 | `tests/test_6_stream_objects.py`, `tests/test_5_files_write_batch.py`, `tests/test_0_np_core.py`, `tests/test_2_data_generator.py`, `tests/test_5_empty_schema.py`, `tests/conftest.py`, `rand_engine/validators/method_specs.py`, `rand_engine/main/_rand_generator.py`, `docs/1_DATA_GENERATOR.md`, `docs/3_WRITING_FILES.md` |
| Job 5 | Job 2, Job 3, Job 4 | 3 | `tests/test_docs.py`, `docs/compatibility.md`, `docs/2_SPARK_GENERATOR.md`, `CHANGELOG.md`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/auto_tag_publish_master.yml` |
| Reconciliation | Job 5 | 4 | `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/generation/generation-methods.md`, `specs/memory/product/generation/spark-generator.md`, `specs/memory/product/spec/rand-spec-grammar.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json`, `specs/backlog/BACKLOG.json`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md` |

### Schedule and sizing

- 22 tasks: Job 1 one, Job 2 two, Job 3 nine, Job 4 six, Job 5 four. Each behaviour is a RED task then an implementation task, each its own `wt-task-<kkk>`. DELETE and REBUILD tasks precede ADD ones; this candidate adds one function (the epoch) and no method.
- Agent count: wave 1 runs Jobs 1 and 2 (2 agents, one task each at a time); wave 2 runs Jobs 3 and 4 (2 agents); wave 3 runs Job 5 (1 agent). Peak 2. Tasks inside a job are serial (shared files).
- Net lines: deletions (the CORRELATED branch, four map entries, four bodies, one epoch copy, the `ns` branch, the NULL docs paragraph and test) outweigh the additions (one function, one object view, the tests).
- `verify:` is unchanged. A task's Definition of done is the repo `verify:` line plus the test files its change reaches, never a new gate. Spark tests run with the null keyring backend and the Temurin 17 JRE first on `PATH` that the dispatch brief gives; no tracked file holds those paths.
- Pandas-3 proofs: `verify:` runs the lock's pandas 2.2.3, so a pandas-3 RED or GREEN step is a named scratch run (`uv run --no-project --with pandas==3.1.0 --with pyarrow==26.0.0 …`, Job 4 file). Their output goes in the commit body.
- Job 3's reverts-red evidence (AC4.3) and Job 3's seeded-identity evidence (AC4.2) are scratch runs too.

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Memory cannot sit in a job file (`W:` refuses `specs/memory`). Order:

1. `dd-product-engineer`, the closure memory pass (`MEMORY-UPDATE.md`): AC7.3 (`ARCHITECTURE.md` Tech Stack, `QUALITY.md` Gates, the atoms named in the DAG row, `index.md`, `catalog.json`).
2. `dd-product-engineer`, re-stamp every `derived-from` hash in `docs/` after the atom edits (shape 9), `git grep -n derived-from docs` before and after.
3. `dd-product-engineer`, shape 2, before the backlog exit sweep: AC7.4, the pyspark clause of `compat-current-ecosystem`.
4. Operator act before the master PR: the branch-protection edit of the dead required contexts (C4), per the ruling.
5. Review evidence: AC5.3 and AC5.4 are read from the first Job 5 push run (id cited at review).

### Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC1.1, AC1.2 | J2.T1 | J2.T2 |
| AC1.3 | J2.T2 | — |
| AC1.4 | J5.T4 | — |
| AC2.1 | J4.T5 | — |
| AC2.2, AC2.3 | J4.T3 | J4.T4 |
| AC2.4 | J4.T5 | — |
| AC2.5 | J4.T1 | J4.T5 |
| AC2.6 | J4.T2 | — |
| AC2.7 | J4.T6 | — |
| AC2.8 | J4.T5 | — |
| AC3.1, AC3.4 | J3.T1 | J3.T3 |
| AC3.2 | J3.T4 | — |
| AC3.3 | J3.T2 | J3.T5 |
| AC4.1, AC4.2 | J3.T7 | — |
| AC4.3 | J3.T6 | — |
| AC4.4 | J3.T8 (conditional on Q1) | — |
| AC4.5 | J3.T9 | — |
| AC4.6 | J5.T3 | — |
| AC5.1, AC5.2, AC5.3, AC5.4 | J5.T4 | — |
| AC6.1, AC6.2 | J1.T1 | — |
| AC7.1 | J5.T1 | J5.T2 |
| AC7.2 | J5.T3 | — |
| AC7.3, AC7.4 | Reconciliation | — |
