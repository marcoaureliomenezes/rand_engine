# PLAN — Release: 0.8.0, candidate 2 (honest PyPI metadata, Python 3.13 in CI, five bugs, benchmarks in the docs)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-2/SPEC.md`

## 1. As-is review

Paths are relative to the repo root. Ledger = `specs/bugs/BUGS.jsonl` + `_archive/bugs_histo.jsonl`; `git log` was read on every unit. Measurements: §3.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `pyproject.toml` metadata (`[tool.poetry]` name/description/keywords/classifiers/urls/scripts, `python = "^3.10"`) | poetry-core derives Python classifiers 3.10–3.15 from the caret; 6 keywords; no `Typing :: Typed`; `[tool.poetry.scripts]` deprecated | 0 on metadata; the file's last 4 changes were `J2.T1/T2`, `J6.T10`, `J9.T2` (pins, script, URL), none fixed a bug of this shape | UPDATE | the contract is the same wheel with truer lines. `poetry check` under a `[project]` table also deprecates `homepage/repository/documentation/urls/extras` (measured, §3.1), so those move with it: one static table, no second path |
| `poetry.lock` | pandas 2.2.2 (no `cp313` wheel), `python-versions = "^3.10"` | `dependabot-*` ×2 resolved by lock bumps (`1518c4f`) | UPDATE | `poetry lock` after the manifest change plus the pandas pin-then-relax (§3.2); the diff is named in the commit body |
| `tests/integrations/test_public_api.py` wheel tests on `built_wheel` (:392-539) | one build, many METADATA asserts | 2 resolved on the surface (`wheel-test-subprocess-dilutes-coverage`, J4 era) | UPDATE | two asserts join the shared fixture (keywords, classifiers + `Requires-Python`); zero new builds; no assert moves |
| `tests/test_9_cli.py:221-229` dependency assert | reads `tool.poetry.dependencies`, expects `"python": "^3.10"` | 0 | UPDATE (assert moves) | the `python` entry leaves the dict and `project.requires-python == ">=3.10"` is asserted instead (operator ruling 2026-10-15, AC1.5); the other four entries stay literal. It becomes its own test so the stdlib-only import assert above it keeps running while the new one is red |
| `tests/test_docs.py:379` `_pip_installs` extras reader | reads `tool.poetry.extras` | `landing-test-reads-first-extra-only` (resolved `c78d90a`) | UPDATE (reader's key moves) | `poetry check` refuses `tool.poetry.extras` beside `[project]` (measured); the reader follows to `project.optional-dependencies`. Ruling R1 (AC1.7) |
| `rand_engine/validators/method_specs.py` `int_zfilled` rule :323 | the one catalog rule of a numeric `length` with no `semantic`; the engine's int64 limit (`10**length`, `_np_core.py:117`) and Spark's width are the only bounds | `int-zfilled-nonpositive-length-validates-then-raises`, `int-zfilled-length-above-18-validates-then-raises` (open, one cause: no bound at the decider); neighbours `7c3566b`, `85a860f` on the file | REBUILD | ≥ 2 bugs on the rule. Structural cause: the catalog is the one decider both engines consult (rc-1 `method-registry-has-five-owners`), and this rule never stated its domain. The rule becomes a semantic rule like `integers`/`floats`, `1 <= length <= 18` |
| `rand_engine/validators/common_validator.py` `_spark_width_errors` :246 | `10 ** min(kwargs["length"], 16)`: the clamp exists only because a huge `length` reaches here | rc-1 REBUILD (`d6569d4`) and `7c3566b` | DELETE (the clamp) | `validate_column` runs first (`errors or ...`), so after the catalog bound `length` is ≤ 18 here and `min(..., 16)` is dead: `10 ** kwargs["length"]`. The `<= 15` message stays; Spark's width rule is unchanged |
| `rand_engine/core/_np_core.py` `gen_ints_zfilled` :115-119 | operator-written body (invariant 12) | `NPCore` `gen_*` bodies | KEEP | the fix is at validation; the body is not touched |
| `rand_engine/__init__.py:1` docstring | "Synthetic data generation for Pandas and Spark dataframes." | `package-docstring-contradicts-pitch` (open) | UPDATE (one line) | the docstring becomes the PyPI Summary; a test ties them so they cannot drift again (one wheel-METADATA read, no new decider) |
| `rand_engine/file_handlers/_writer_stream.py:31` `trigger` | `frequency: int`; docstring says float | `stream-trigger-frequency-annotated-int` (open); `writer-options-consumed-by-use` resolved on the file | UPDATE (one token) | annotation only; no body change |
| `tests/test_docs.py:321-341` reference directive test | cases come from `_directives(reference.md)`, so a deleted `:::` removes its own case | `reference-test-self-referential` (open); `docs` surface 1 resolved | REBUILD | the case source contradicts the contract (the page must match the public surface). One test over `rand_engine.__all__`; `_resolve` leaves if nothing else calls it (its only caller is this test); net lines ≤ 0 |
| `.github/workflows/{auto_tag_publish_master,auto_tag_publish_development,pr_to_master,pr_to_development,test_on_push}.yml` matrices :77 :86 :34 :158 :45 | `['3.10','3.11','3.12']` ×5; summary literal `3.10, 3.11, 3.12` (`auto_tag_publish_master.yml:237`), a per-cell ✅ grid with Python columns 3.10–3.12 and "9 (3 OS × 3 Python versions)" (`test_on_push.yml:143-158`), a version-naming comment (`test_on_push.yml:46`) | `workflow-summary-text-stale` resolved (`af3fd67`) and 3 more on the surface | UPDATE (+ DELETE the literals and the grid) | the matrix is the one decider; no summary names a Python version or a combinations count: `auto_tag_publish_master.yml:237` keeps only the test result, and the `test_on_push.yml` grid (a fixed ✅ per cell from one aggregate `needs.test.result`) becomes one result line with no count, so a matrix change never leaves a literal stale. Evidence: `git grep -n "3\.1[0-3]" .github/workflows` shows only matrix lists and build-version settings (`3.12` envs and `matrix.python-version == '3.12'` coverage conditions) |
| `tests/fixtures/f2_spark_generator_specs_right.py:31` skip predicate, `tests/conftest.py:7-9`, `tests/AGENTS.md:9` | skips Spark on `Windows and >= (3, 12)`, a range that already includes 3.13 | 0 | KEEP (contingent UPDATE) | measured: the full suite passes on Linux 3.13 with pyspark 3.5.8 (§3.3). The predicate widens only on a CI run that shows a 3.13 Spark leg failing (J3.T1); otherwise AC2.2 holds with no code |
| `docs/2_SPARK_GENERATOR.md:3-4` | "PySpark is not a dependency … bring your own session" | 0 | UPDATE (one line) | AC2.4; states the CI-validated combinations, written after the 3.13 run and citing it (Q1 ruled) |
| `CHANGELOG.md` `## [0.8.0]` section | dated header, Added/Fixed written by rc-1 Job 11; `_changelog` check (`test_docs.py:387-395`) | `changelog-070-header-says-unreleased` resolved | UPDATE (lines only) | AC6.1; no other job writes the file; the check reads headers and the faker line, so it stays green |
| `tests/test_benchmarks.py:306-307`, `docs/BENCHMARKS.md`, `docs/benchmarks.json` | 0.7.0's record: head 5920630, base 959f890 | 0 on the file; `a911fd2` is the precedent record | UPDATE | `TERMINAL_*` move to the new run's head and base (operator demand 2026-10-16); the two docs files are the artifact byte for byte |
| `specs/memory/{QUALITY,ARCHITECTURE}.md`, `product/onboarding/documentation.md`, `product/onboarding/get-started-cli.md`, `product/quality/benchmarks.md`, rc-1 closure summary | per SPEC FR5 | rc-1 reconcile review `2026-10-16T141302Z-dd-code-reviewer-reconcile-rc1` | UPDATE | memory text only, `pe` in Reconciliation |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which Python versions the wheel supports | `pyproject.toml` `project.requires-python` (`>=3.10`) and `project.classifiers` 3.10–3.13 | the five CI matrices, the wheel test (AC1.2), `tests/test_9_cli.py` | `python = "^3.10"` in `[tool.poetry.dependencies]`, the derived 3.10–3.15 set |
| what the package is (Summary) | `pyproject.toml` `project.description` | `rand_engine.__doc__` first line, the wheel test | the old docstring sentence |
| the valid domain of `int_zfilled` `length` | the catalog rule `int_zfilled` in `method_specs.py` (`1 <= length <= 18`) | `CommonValidator.validate_column`, `validate_spark_spec`, `DataGenerator` construction | the `min(..., 16)` clamp in `_spark_width_errors` |
| which names the reference page documents | `rand_engine.__all__` | `docs/reference.md` `:::` lines, the reference test | the page-derived parametrization |
| which cases the benchmark docs hold | the CI artifact of the last measured head | `docs/benchmarks.json` (next A/B base), `TERMINAL_*`, the artifact tests | the 0.7.0 literals |
| whether Spark tests run on a platform | the one skip predicate in `f2_spark_generator_specs_right.py` | every Spark test via the session fixture | none |

### 1.2 Consumers of every changed name, format or fix line

Associated repos of the context: 0. Counts are greps on the define tree.

| changed | consumers | answered by |
|---|---|---|
| `[tool.poetry.scripts]` → `[project.scripts]` | wheel test `entry_points.txt` assert (passes unchanged, measured); `tests/test_9_cli.py` console-script test | J1 |
| `python` leaves `[tool.poetry.dependencies]` | `tests/test_9_cli.py:222-229` | J1.T2 |
| `[tool.poetry.extras]` → `[project.optional-dependencies]`; `[tool.poetry.urls]`, `homepage`, `repository`, `documentation` → `[project.urls]` | `tests/test_docs.py:379` (extras); the wheel asserts read METADATA `Project-URL`, whose five labels are identical before and after (measured) | J1.T2, J1.T3 |
| `License: MIT` + `License :: OSI Approved :: MIT License` → `License-Expression: MIT` (SPDX, forced: a License classifier beside `license = "MIT"` warns, measured) | 0 tests, 0 docs name either line; the README `pypi/l` badge reads PyPI's license field | J1.T3; Q2 |
| bare `Programming Language :: Python :: 3` | dropped by poetry-core when explicit versions are given; 0 consumers | J1 |
| `version = "0.8.0"` line | `auto_tag_publish_master.yml:36`, `auto_tag_publish_development.yml:36` (`grep '^version = "M.m.p"'`): one hit, in `[project]`; `poetry version "$RC_TAG"` and `poetry version -s` rewrite and read `[project].version` (measured) | J1 |
| faker declared in `[tool.poetry.dependencies]` (optional) and in `[project.optional-dependencies]` | the wheel prints one `Requires-Dist: faker (...) ; extra == "faker"` and one `Provides-Extra` (measured); `tests/test_9_cli.py` keeps its faker entry as written | J1 |
| `poetry.lock` `python-versions`, content-hash, pandas 2.2.3 | `verify:` installs from the lock; the five CI matrices | J1.T3, J2 |
| workflow summary grid and literals | 0 readers; the summary pages only | J2 |
| `int_zfilled` error text for `length` outside 1..18 | `tests/test_1_common_validator.py:569-575` (`length` 5000 and 10**7 assert the substring `15` from Spark's width message, which the catalog bound now preempts) | J4.T1, ruling R2 |
| `rand_engine.__doc__` | `help(rand_engine)`, mkdocstrings package page (reads the module docstring), `tests/test_docs.py` docstring-rule tests | J5 |
| `docs/benchmarks.json` `commit`/`base_commit` | `benchmarks.yml:45-47` (next run's A/B base), `tests/test_benchmarks.py` | J7 |

## 2. Rulings and decisions

Carried from the grill (`2026-10-16T150500Z-main-thread-grill-080-rc2`) and the operator rulings in the SPEC: the `kafka-python` exemption stays; the benchmark summary stays as is; the upper `length` bound joins AC3.1; AC2.4 states a Spark line.

Ruled 2026-10-16 (grill handoff, last six findings); the SPEC was amended at 5939436:

- **R1** (AC1.7, J1.T2; operator "Accept, everything into [project]"): `tests/test_docs.py:379` reads `project.optional-dependencies` instead of `tool.poetry.extras`. Reason: §3.1 shows `poetry check` warns on any `[tool.poetry.extras]` beside `[project]`, and AC1.4 needs zero warnings. SPEC §3 (non-goal "moving `[tool.poetry.extras]`") and §5 (consumer "kept") read otherwise; the SPEC owner amends them. Accepted: urls and extras move into `[project]`.
- **R2** (J4.T1; main-thread ruling): `test_int_zfilled_length_above_15_is_one_collected_error` parametrizes `[16, 5000, 10**7]` and asserts the substring `15`. The catalog bound now refuses 5000 and 10**7 first, with its own message, still one issue naming `length`. Ruled: `16` stays in that test untouched; 5000 and 10**7 move to the new AC3.1 partition test with the `Column 'c'` and `'length'` asserts; the `test(J4.T1)` commit names this ruling.
- **Q1** (AC2.4; operator "Write what CI shows"): the Spark page states the combinations CI validates, written after the 3.13 CI run, citing it; no claim CI does not back.
- **Q3** (J2.T1; main-thread ruling): the `test_on_push.yml:143-158` grid is replaced by one result line.
- **AC4.1** (operator "Yes, dispatch"): the main thread dispatches one `benchmarks.yml` run on `feature/0.8.0` after Jobs 1–6 merge.
- **AC6.1** (main-thread ruling): rc-2 adds its CHANGELOG lines to the `## [0.8.0]` section, in Job 7 (the last code job), `_changelog` check unchanged and green.

Planning rules (as in rc-1): a RED task lands its test marked `@pytest.mark.xfail(strict=True, reason=...)`, one marker per case when several implementation tasks share it; the implementation task lists the test file in its `W:` and removes only its own marker. Tasks of one job that share a test file run in sequence.

## 3. Measurements (scratch copy of the define tree outside the repo; `POETRY_VIRTUALENVS_IN_PROJECT=false`, cache under `.dadaia/tmp/poetry-cache`; Poetry 2.5.1; every venv deleted)

### 3.1 AC1.6 — the wheel with a static `[project]` table

- Today's wheel (this tree): `Requires-Python: >=3.10,<4.0`, classifiers `Programming Language :: Python :: 3`, `3.10` … `3.15`, `License :: OSI Approved :: MIT License`, 6 keywords.
- With `[project]` carrying `requires-python = ">=3.10"`, `classifiers` listing 3.10, 3.11, 3.12, 3.13 and `Typing :: Typed`, and `keywords` of 14: METADATA `Requires-Python: >=3.10`; Python classifiers exactly 3.10, 3.11, 3.12, 3.13. **poetry-core adds no 3.14+ classifier and no bare `Programming Language :: Python :: 3`.** `Keywords` is the single `project.keywords` list (no second source). The fallback `>=3.10,<3.14` is not needed.
- `License: MIT` becomes `License-Expression: MIT`; the License classifier leaves (with it `poetry check` warns). The other METADATA lines (`Requires-Dist` ×4, `Provides-Extra: faker`, five `Project-URL` labels, `Summary`, author, `console_scripts`) are identical.
- Chosen shape: `[project]` = `name`, `version`, `description`, `readme`, `requires-python`, `license = "MIT"`, `authors`, `keywords`, `classifiers`, `dynamic = ["dependencies"]`; `[project.scripts]`; `[project.optional-dependencies] faker`; `[project.urls]` (Homepage, Repository, Documentation, Issues, Changelog). `[tool.poetry.dependencies]` keeps numpy, pandas, pyarrow and the optional faker (the entries the assert at `tests/test_9_cli.py` lists), without `python`; `[tool.poetry.group.*]` and every tool table are unchanged. `poetry check` exits 0 with "All set!" and no warning; the same file with `[tool.poetry.extras]` or any `[tool.poetry.urls]` key prints one deprecation warning each.
- The existing wheel tests, `tests/integrations/test_public_api.py` whole file, pass on this shape (Python 3.13 venv). The only two tests that fail are the two consumers of §1.2: `test_9_cli.py::test_cli_imports_only_stdlib_and_rand_engine` (the deps dict) and `test_docs.py::test_landing_contract[pip-install]` (the extras key).
- `poetry install --with test --no-root --dry-run` resolves; `poetry version 0.8.0rc2.dev1` rewrites the single `version =` line in `[project]`.

### 3.2 AC2.3 — pandas and the lock

- `pip download pandas==2.2.2 --python-version 3.13 --only-binary=:all:` fails (versions with a `cp313` wheel: 2.2.3, 2.3.0, 2.3.1, 2.3.2, …); `pandas==2.2.3` downloads `cp313-manylinux`. **2.2.3 is the first release inside `^2.2.2` with `cp313` wheels.**
- `poetry lock` after the manifest change moves nothing but `python-versions` (`^3.10` → `>=3.10`), the content-hash and a merged `tomli` marker block (net −12 lines). `poetry update pandas --lock` would take 2.3.3 (also `cp313`). The smaller step is 2.2.3: set `pandas = "==2.2.3"`, `poetry lock`, restore `pandas = "^2.2.2"`, `poetry lock` again; the lock keeps 2.2.3 and `poetry check --lock` passes. Net lock diff against today: 104 lines, `version` changes: pandas 2.2.2 → 2.2.3 and one `tomli` block.
- No `[tool.poetry.dependencies]` constraint other than `python` changes.

### 3.3 AC2.2 — pyspark 3.5.8 on Python 3.13

- pyspark 3.5.8 declares `Requires-Python >=3.8` and Python classifiers up to 3.11 (its installed METADATA); no source declares 3.12 or 3.13 support, and 3.12 already runs in this repo's CI.
- Measured run (Linux, Python 3.13.13, pandas 2.2.3, pyspark 3.5.8, OpenJDK 21, `PYSPARK_PYTHON` set to the venv interpreter): `tests/test_0_spark_core.py` + `tests/test_3_spark_generator.py` pass, and the whole suite excluding `tests/integrations` passes (1 run, 47.7 s wall, 0 skips). **pyspark 3.5.8 does not fail on Linux 3.13.** The one failure seen was `PYTHON_VERSION_MISMATCH` when the Spark worker resolved a different `python` than the driver, an environment fault, not a version limit.
- The existing predicate `platform.system() == "Windows" and sys.version_info >= (3, 12)` already skips Windows 3.13. macOS 3.13 is the only combination not measured; the candidate's push CI is the measurement, and J3.T1 widens the predicate only on a failing run id.
- Consequence for AC2.4: the line "Spark needs Python <= 3.12" would be false on Linux 3.13; the operator ruled the page states what CI validates (Q1).

### 3.4 FR4 — obtaining the artifact

- `benchmarks.yml` triggers on `pull_request` to `master`/`development` and on `workflow_dispatch`; the file is on `master`, so the dispatch API accepts it with `--ref feature/0.8.0` (not exercised here: a run is a side effect). Precedent: `a911fd2` recorded run 38170880052, a `pull_request` run on `feature/0.7.0` at head 5920630; the record commit followed it and the drift check was zero.
- Duration: run 38918442801 (PR #44) took 16m45s (`gh run list`). The A/B base is the `commit` of the committed `docs/benchmarks.json`, 5920630.
- Order: PR #44 (rc-1) merges to `development` first. Every code job of rc-2 merges into `feature/0.8.0` and the main thread pushes it once. After Jobs 1–6 merge, the main thread (operator-approved) starts the run with `gh workflow run benchmarks.yml --ref feature/0.8.0` (or reads the `pull_request` run if a PR on that branch is open) and cites its run id; the rc-2 candidate PR is opened only after Reconciliation, so it cannot supply this artifact. Job 7 receives the run id, `gh run download <id> -n benchmarks` into a scratch directory, and records.
- The run's `commit` is the branch tip at dispatch; the record commit adds only `docs/` and `tests/`, so `git diff --stat <commit> HEAD -- rand_engine benchmarks pyproject.toml poetry.lock` stays at zero. Reconciliation writes `specs/` only.

### 3.5 Gate cost

No requirement applied to every task, job or deletion is added; `verify:` is unchanged. The new asserts ride the existing `built_wheel` build and cost milliseconds. One Python 3.13 full run excluding the wheel build measured 47.7 s wall.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/integrations/test_public_api.py`, `tests/test_9_cli.py`, `tests/test_docs.py`, `pyproject.toml`, `poetry.lock` |
| Job 2 | — | 1 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml` |
| Job 3 | Job 1, Job 2 | 2 | `tests/fixtures/f2_spark_generator_specs_right.py`, `tests/conftest.py`, `tests/AGENTS.md`, `docs/2_SPARK_GENERATOR.md` |
| Job 4 | — | 2 | `tests/test_1_common_validator.py`, `rand_engine/validators/method_specs.py`, `rand_engine/validators/common_validator.py` |
| Job 5 | Job 1 | 2 | `tests/integrations/test_public_api.py`, `tests/test_5_files_write_stream.py`, `rand_engine/__init__.py`, `rand_engine/file_handlers/_writer_stream.py` |
| Job 6 | Job 1 | 2 | `tests/test_docs.py` |
| Job 7 | Job 3, Job 4, Job 5, Job 6 | 3 | `tests/test_benchmarks.py`, `docs/BENCHMARKS.md`, `docs/benchmarks.json`, `CHANGELOG.md` |
| Reconciliation | Job 7 | 4 | `specs/memory/**`, `specs/releases/0.8.0/_RELEASE.json` |

Overlaps across waves are ordered by an edge: `tests/integrations/test_public_api.py` and `tests/test_docs.py` (Job 1 → Job 5, Job 6). Inside each wave the `W:` sets are disjoint. Job 1 comes first and Reconciliation last. Job 7 is the last code job (AC4.3): it waits on every other job so no later commit can touch a measured path. Jobs 1 and 2 merge before the first push; the push CI is the evidence Job 3 reads.

### Reconciliation (no job file; `reconcile` tree, `RC-FLOW.md` step 4)

| task | who | W: |
|---|---|---|
| memory pass: AC5.1–AC5.4, AC5.6 (`QUALITY.md`, `ARCHITECTURE.md` incl. `## Tech Stack`, `documentation.md`, `get-started-cli.md`, `benchmarks.md`) | pe | `specs/memory/**` |
| closure entries incl. AC5.5 (`release.py` verbs only) | pe | `specs/releases/0.8.0/_RELEASE.json` |

- Tech Stack (invariant 11, rc-1 precedent): Python `>=3.10`, CI-tested 3.10–3.13, `[project]` static metadata with Poetry dependencies.
- The memory pass reads the diff of Jobs 1 to 7: `QUALITY.md` Gates names the 3.13 legs and the Spark skip as CI shows it.
