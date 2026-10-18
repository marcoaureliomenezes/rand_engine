# SPEC — Release: 0.8.0, candidate 2 (honest PyPI metadata, Python 3.13 in CI, five bugs, benchmarks in the docs)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-16
**Origin:** backlog:pypi-metadata; bugs:int-zfilled-nonpositive-length-validates-then-raises,int-zfilled-length-above-18-validates-then-raises,package-docstring-contradicts-pitch,stream-trigger-frequency-annotated-int,reference-test-self-referential

- Backlog `pypi-metadata`: 14 keywords, `Typing :: Typed`, CI matrices gain Python 3.13 and Spark tests skip where pyspark 3.5 cannot run. `python` reads `>=3.10` with no cap, and the explicit classifiers 3.10–3.13 make the wheel advertise only the tested set. The fallback `>=3.10,<3.14` applies only if poetry-core cannot keep those classifiers. Sources: the entry's provenance, which holds the operator rulings of 2026-10-15 ("Widen CI to 3.13", then "No cap, honest classifiers", which supersedes the cap), and handoff `2026-10-16T013009Z-main-thread-adoption-resume-grill`.
- Folded in, same file and same table: `poetry check` warns that `[tool.poetry.scripts]` is deprecated. The script moves to `[project.scripts]`, in the PEP 621 `[project]` table that the static classifiers need. Beside `[project]`, `poetry check` also warns on `[tool.poetry.extras]`, the License classifier and `[tool.poetry.urls]` (PLAN §3.1, measured). Operator ruling (grill): the urls and the faker extra move to `[project.urls]` and `[project.optional-dependencies]`, and `License: MIT` becomes `License-Expression: MIT`.
- The five bugs open on `feature/0.8.0` (`specs/bugs/BUGS.jsonl`), each fixed RED → GREEN per `specs/bugs/AGENTS.md` §2; `int-zfilled-length-above-18-validates-then-raises` was confirmed in the grill with "Confirm, same fix".
- Grill: handoff `2026-10-16T150500Z-main-thread-grill-080-rc2`. Operator rulings:
  - The benchmark Job summary and PR comment stay as they are.
  - The Spark page states the combinations CI validates, written after the 3.13 CI run. This supersedes the earlier "<= 3.12" line, since pyspark 3.5.8 was measured green on Linux 3.13.
  - The `kafka-python` exemption is kept, and the upper `length` bound joins AC3.1.
  - Everything moves into `[project]`.
  - The main thread dispatches one `benchmarks.yml` run on `feature/0.8.0` after Jobs 1–6, which feeds Job 7.
- Main-thread rulings (same handoff):
  - R2: `test_int_zfilled_length_above_15` keeps `16`, and `5000` and `10**7` move to the new AC3.1 partition test.
  - Q3: J2.T1 replaces the stale result grid at `test_on_push.yml:143-158` with one result line.
  - rc-2 adds its lines to the CHANGELOG 0.8.0 section (FR6).
- Operator demand, 2026-10-16, verbatim: «eu ver testes de benchmark de CI funcionando e publicando um summary no actions que me é mandado que posso ver + merge de benchmarks na documentação». State of play: `benchmarks.yml:48-56` already publishes the Job summary and a PR comment (PR #44 run 38914408354, 46/46 rows). `docs/BENCHMARKS.md` and `docs/benchmarks.json`, served as the site's Benchmarks page (`mkdocs.yml:23`), were last recorded at a911fd2 (2026-10-11, head 5920630).
- Operator ruling, 2026-10-16 (grill): the landing test keeps its `kafka-python` exemption (`tests/test_docs.py:382`). It is recorded below as a Term.
- Closure-memory claims that the rc-1 reconcile review (handoff `2026-10-16T141302Z-dd-code-reviewer-reconcile-rc1`) found untrue are carried as FR5.

## Bug window review

This table judges rc-1's 12 resolved records (10 fix commits), each read with `git show <fix_sha>` against the overfitting patterns. Two fixes edit tests (c78d90a, 77f5c4c): both are bugs in the tests themselves, and no assert was loosened.

| bug | fix_sha | pattern hit | verdict | why |
|---|---|---|---|---|
| `spark-integers-width-2pow53-validates-then-raises` | `d6569d4` | ≥ 2 fixes on `_spark_width_errors` (with `7c3566b`) | KEEP | this fix is rc-1's REBUILD: one predicate `width_beyond_double`, net −3. The open `int-zfilled-nonpositive-length-…` is not its child: at `d6569d4^`, `10 ** -1` also validated |
| `workflow-actions-mutable-refs` | `948bfe8` | none (6/−6) | KEEP | SHA pins, tag in a comment |
| `workflow-missing-top-level-permissions` | `b150df5` | none | KEEP | declarations only, +14 |
| `workflow-summary-text-stale` | `af3fd67` | none | KEEP | the same kind of literal remains at `auto_tag_publish_master.yml:237` (`3.10, 3.11, 3.12`) and `test_on_push.yml:143-158` (version grid, `9 (3 OS × 3 Python versions)`); AC2.1 deletes them |
| `changelog-070-header-says-unreleased` | `a993de3` | none | KEEP | dated header |
| `faker-extra-undocumented-unpinned-install` | `3410c4d` | none (net −74) | KEEP | README rebuilt |
| `dependabot-pyspark-357-ghsa-9437`, `dependabot-setuptools-781-ghsa-h35f` | `1518c4f` | none | KEEP | lock bumps |
| `get-started-scaffold-shadows-package` | `16e8fc1` | none (net 0; `caused_by` J6.T2) | KEEP | one naming rule for every slug; no child bug |
| `landing-test-regex-unmatchable-dollar`, `landing-test-reads-first-extra-only` | `c78d90a` | a special case on a test value (`kafka-python`, `tests/test_docs.py:382`) | KEEP | the special case is the operator's 2026-10-16 ruling (Terms). The tomllib shim it added copies `tests/test_9_cli.py:11-14`; FR1 moves the extras reader's key (§5) |
| `wheel-test-subprocess-dilutes-coverage` | `77f5c4c` | none (+3/−1; `caused_by` J4.T1) | KEEP | one env filter on the wheel child |

- No REBUILD verdict, so Job 1 carries no Bug-window work.

## 1. Problem

- PyPI advertises versions CI never tests. `python = "^3.10"` (`pyproject.toml:29`) makes poetry-core derive Python classifiers 3.10 through 3.15 (wheel built on 7e12958, backlog entry), while every test matrix runs only 3.10–3.12 (`auto_tag_publish_master.yml:77`, `auto_tag_publish_development.yml:86`, `test_on_push.yml:45`, `pr_to_master.yml:34`, `pr_to_development.yml:158`). The 6 keywords (`pyproject.toml:11`) miss the terms users search for, and the wheel ships `py.typed` but does not say `Typing :: Typed`.
- `poetry check` warns on `[tool.poetry.scripts]` (`pyproject.toml:25-26`).
- `poetry.lock` pins pandas 2.2.2, which has no `cp313` wheel, so installing on Python 3.13 builds pandas from source.
- Five open bugs:
  - `int_zfilled` with `length` < 1 or > 18 validates and then fails or emits one-character strings, which breaks invariant 3.
  - `rand_engine.__doc__` (`rand_engine/__init__.py:1`) contradicts the constitution's Purpose.
  - `FileStreamWriter.trigger(frequency: int)` (`_writer_stream.py:31`) takes a float.
  - The reference-page test draws its cases from the page it checks (`tests/test_docs.py:333-335`).
- The docs' benchmark table describes 0.7.0's head (5920630), not this release.

## 2. Measurable goals

- The wheel METADATA carries the 14 keywords and `Typing :: Typed`; its Python classifiers are exactly 3.10–3.13, the set CI tests; `Requires-Python` is `>=3.10`.
- Every CI test matrix includes 3.13 and is green; `poetry check` prints no warning.
- The five bugs are resolved, each with a RED test that the fix turns green.
- `docs/BENCHMARKS.md` and `docs/benchmarks.json` are the CI artifact of this candidate's last measured head.

## 3. Non-goals

- Any core `gen_*` body or `StreamHandler` (invariant 12): `NPCore.gen_ints_zfilled` (`_np_core.py:115-119`) is untouched, since validation carries the `int_zfilled` fix.
- A pyspark 4 upgrade, or any other runtime or test dependency version beyond the lock moves FR2 needs; any new dependency.
- A new workflow, workflow permission, secret or bot commit; any automation of the benchmark record; a change to `benchmarks.yml` or `benchmarks/speed.py`.
- The `documentation-excellence` backlog entry, which is the rc-3 demand.
- Moving the runtime constraints of `[tool.poetry.dependencies]` into `[project]`; they stay dynamic.
- Rewriting the rc-1 `summary` log entry: the log is append-only (`RELEASE-EVENTS.md`), so AC5.5 handles it.

## 4. Requirements

### Terms

- **Advertised Python set:** the wheel's `Programming Language :: Python :: 3.<n>` classifiers. It equals the CI test matrix: 3.10, 3.11, 3.12, 3.13.
- **Measured paths:** `rand_engine/`, `benchmarks/`, `pyproject.toml`, `poetry.lock`, the paths whose diff a911fd2's drift check reads. A candidate's **last measured head** is its last commit that touches one of them.
- **Benchmark record:** the procedure of a911fd2 (0.7.0 rc-2 J8.T4).
  - A successful `Benchmarks` run (`benchmarks.yml`) on the last measured head uploads the `benchmarks` artifact.
  - A task copies `docs/benchmarks.json` and `docs/BENCHMARKS.md` from that artifact byte for byte.
  - Its commit body names the run id, head, base and the two sha256 values, and quotes the drift check `git diff --stat <head> HEAD -- rand_engine benchmarks pyproject.toml poetry.lock` at zero lines.
  - The committed JSON's `commit` becomes the A/B base of the next run (`benchmarks.yml:45-47`).
- **Landing-test exemption (operator ruling, 2026-10-16):** `pip install kafka-python` is the one install line `_pip_installs` (`tests/test_docs.py:377-384`) exempts. The `kafka` case's producer needs a client that no declared extra provides. The exemption stays, and this Term is its authority.

### FR1 — Honest PyPI metadata

- AC1.1 (integration, a wheel test on the shared `built_wheel` fixture, `tests/integrations/test_public_api.py:392`): the METADATA `Keywords` are exactly the 6 of today plus `faker`, `fake-data`, `pyspark`, `spark`, `pandas`, `kafka`, `parquet`, `data-generator` (14 in all). It is RED on today's wheel.
- AC1.2 (integration, same fixture): the `Classifier` lines include `Typing :: Typed`. The set of `Programming Language :: Python :: 3.<n>` classifiers is exactly {3.10, 3.11, 3.12, 3.13}, and `Requires-Python` reads `>=3.10`. It is RED on today's wheel.
- AC1.3 (integration, existing tests): `[tool.poetry.scripts]`, `[tool.poetry.extras]` and `[tool.poetry.urls]` are gone, along with the `homepage`, `repository` and `documentation` keys. `[project.scripts]` declares `rand-engine = "rand_engine.cli:main"`, `[project.optional-dependencies]` declares `faker`, and `[project.urls]` holds the five labels. The wheel asserts at `tests/integrations/test_public_api.py:418-539` stay unchanged and pass. The METADATA is identical to today except for AC1.1, AC1.2, the dropped bare `Programming Language :: Python :: 3` classifier, and `License: MIT` → `License-Expression: MIT` (the License classifier leaves), which the operator accepted.
- AC1.4 (no test, build-tool output; reason: the verify line runs no `poetry check`, and no gate is added): `poetry check` exits 0 and prints no warning. The commit body quotes its output.
- AC1.5 (unit): the `"python": "^3.10"` entry leaves the dependency assert at `tests/test_9_cli.py:223-229`, and `project.requires-python == ">=3.10"` is asserted instead. The operator ruled this on 2026-10-15 ("No cap, honest classifiers"), and the `test(...)` commit cites that ruling. The other four entries stay as written.
- AC1.7 (unit, existing landing test): `_pip_installs` (`tests/test_docs.py:379`) reads the extras from `project.optional-dependencies`, and its allowed set is still `{"faker"}`.
- AC1.6 (no test, a measurement in PLAN §1): the as-is review builds the wheel with static `[project]` classifiers and shows the Python classifiers are exactly 3.10–3.13. If poetry-core adds any 3.14+ classifier, the operator's fallback applies: the constraint reads `>=3.10,<3.14`, and AC1.2 asserts `Requires-Python` `<3.14,>=3.10`.

### FR2 — CI tests Python 3.13

- AC2.1 (no test; reason: workflow YAML has no seam in the suite, as rc-1 ruling 9 held, and CI is the check): the five matrices (`auto_tag_publish_master.yml:77`, `auto_tag_publish_development.yml:86`, `test_on_push.yml:45`, `pr_to_master.yml:34`, `pr_to_development.yml:158`) list `3.10`, `3.11`, `3.12`, `3.13`. No workflow summary holds a Python-version list or a combinations count, the literal class of `workflow-summary-text-stale`. `auto_tag_publish_master.yml:237` keeps only the test result. The `test_on_push.yml:143-158` grid becomes one result line with no count (ruling Q3). The commit body quotes `git grep -n "3\.1[0-3]" .github/workflows`, which shows only matrix lists and build-version settings. Every leg of the candidate's push CI is green, and the run id is cited at review.
- AC2.2 (integration, the Spark fixture): the outcome depends on the 3.13 CI run.
  - Only if a 3.13 Spark leg fails does the one skip predicate (`tests/fixtures/f2_spark_generator_specs_right.py:31`) widen to that platform. Its skip reason names pyspark 3.5 and Python 3.13, and its commit cites the failing run.
  - Otherwise the predicate is unchanged, and the green run id is the evidence.
- AC2.3 (no test, lock): `poetry.lock` installs on Python 3.13 from wheels. pandas moves to a release inside `^2.2.2` that ships `cp313` wheels; no `[tool.poetry.dependencies]` constraint changes except `python` (FR1). The lock diff is named in the commit body.
- AC2.4 (no test; reason: prose, a text assert tests no behaviour): the Spark page's requirement line (`docs/2_SPARK_GENERATOR.md:3-4`) states the Python × OS combinations on which CI runs the Spark tests. It is written after the 3.13 CI run, cites that run in the commit body and makes no claim CI does not back (grill ruling, 2026-10-16). No other page changes.

### FR3 — The five open bugs

- AC3.1 (unit, `tests/test_1_common_validator.py`): `int_zfilled` with `length` outside 1..18 (0, −1, 19) yields one collected issue naming `length` from `CommonValidator.validate_column` and from Spark validation. `DataGenerator` with that spec raises `SpecValidationError` at construction, and `length` 1, 8 and 18 still validate. One bound, `1 <= length <= 18`, lives in the method catalog's `int_zfilled` rule (`rand_engine/validators/method_specs.py:323`), the one decider both engines consult; Spark's `<= 15` width check is unchanged. Bugs `int-zfilled-nonpositive-length-validates-then-raises` and `int-zfilled-length-above-18-validates-then-raises`.
- AC3.2 (unit): the first line of `rand_engine.__doc__` equals the package `description` that `pyproject.toml` declares, which is the PyPI Summary. It is RED on today's `"Synthetic data generation for Pandas and Spark dataframes."` Bug `package-docstring-contradicts-pitch`.
- AC3.3 (unit): `typing.get_type_hints(FileStreamWriter.trigger)["frequency"] is float`. It is RED on `_writer_stream.py:31`. Bug `stream-trigger-frequency-annotated-int`.
- AC3.4 (unit, `tests/test_docs.py`): the reference test takes its cases from `rand_engine.__all__`. The set of `:::` directives in `docs/reference.md` equals the set of `f"{obj.__module__}.{obj.__qualname__}"` over those names, and each object carries a docstring. Deleting the `SparkGenerator` `:::` line turns it red, which is the reviewer's revert check. Bug `reference-test-self-referential`.

### FR4 — The release's benchmark table in the docs

- AC4.1 (no test; reason: CI evidence): once Jobs 1–6 are merged, the main thread dispatches one `Benchmarks` run (`workflow_dispatch`) on `feature/0.8.0` at the last measured head. It concludes `success`, and its Job summary holds the table (`benchmarks.yml:48-50`). Job 7's record commit names the run id.
- AC4.2 (unit, `tests/test_benchmarks.py`): `docs/benchmarks.json` and `docs/BENCHMARKS.md` are that run's artifact byte for byte, recorded as the Benchmark record Term states.
  - `TERMINAL_HEAD` and `TERMINAL_BASE` (`tests/test_benchmarks.py:306-307`) move to that run's head and base. The authority is the operator demand of 2026-10-16, named in their `test(...)` commit.
  - The existing artifact tests (`:315-333`) pass on the new file: every inventory row at 10^6 and 10^7, and every repo decider.
- AC4.3 (no test; reason: git evidence): at the candidate's closure head, `git diff --stat <recorded head> HEAD -- rand_engine benchmarks pyproject.toml poetry.lock` prints nothing. The recording job is therefore the last job before Reconciliation.

### FR5 — Closure memory truth (Reconciliation, `pe`)

All of FR5 is no test: it is memory text, checked at review against the cited `path:line`.

- AC5.1: each gate cost in `specs/memory/QUALITY.md:36-38` (0.03 s, under 1 s, 0.85 s, 2.4 s, 4.3 s on 72.2 s, 2.2 s) names a measured source, a CI run id or a handoff, or is deleted. The matrix ranges at `QUALITY.md:30` and `:34` read 3.10–3.13.
- AC5.2: the MkDocs-Material bullet at `specs/memory/ARCHITECTURE.md:29` and the fallback clause at `product/onboarding/documentation.md:18` are deleted, because nothing in the repo uses them. `## Tech Stack` (`ARCHITECTURE.md:20`) states Python `>=3.10` and the CI-tested 3.10–3.13, as invariant 11 requires.
- AC5.3: `documentation.md:36` names the three `python no-run` uses the suite allows: the Kafka producer in `docs/5_RECIPES.md`, the tutorials' case includes, and the skill's Spark blocks (`skills/rand-engine/SKILL.md:140`). These are the rules at `tests/test_docs.py:51-60` and `:114-117`.
- AC5.4: `get-started-cli.md:18` narrows to what the code does. An unknown or missing slug exits 2 with usage listing the five slugs (`rand_engine/cli.py:20`). A bare `rand-engine` exits 2 with usage listing the subcommands (`cli.py:17`).
- AC5.5: the rc-2 closure `summary` states that the rc-1 summary's item "llms.txt:7 public-api derived-from marker stale" was fixed by 1505737. The rc-1 entry stays as written: `release.py` has no verb that corrects a log entry, and `RELEASE-EVENTS.md` keeps history unrewritten.
- AC5.6: the `benchmarks` atom (`product/quality/benchmarks.md`) states the Benchmark record: a candidate that touches a measured path records its CI artifact into `docs/`, and the site serves it.

### FR6 — Release notes

- AC6.1 (unit, existing `_changelog` landing check `tests/test_docs.py:387-395`, which stays green; the lines themselves are prose): the `## [0.8.0]` section of `CHANGELOG.md` gains rc-2's user-visible changes.
  - Added: Python 3.13 tested and advertised in the classifiers; the PyPI keywords and `Typing :: Typed`.
  - Fixed: `int_zfilled` `length` refused outside 1..18 at validation; the `rand_engine` docstring; the `trigger(frequency)` annotation.
  - Reconciliation never writes `CHANGELOG.md`.

## 5. Replaces

- `[tool.poetry.scripts]` → `[project.scripts]`. The derived Python classifiers 3.10–3.15 → explicit 3.10–3.13. `python = "^3.10"` (a caret range, capped below 4.0) → `>=3.10`, uncapped. The 6 keywords → 14 (FR1).
- `[tool.poetry.extras]`, `[tool.poetry.urls]` and the URL keys → `[project.optional-dependencies]` and `[project.urls]`; `License: MIT` and its classifier → `License-Expression: MIT` (AC1.3).
- The `"python": "^3.10"` entry of the assert at `tests/test_9_cli.py:224` → a `project.requires-python == ">=3.10"` assert (AC1.5).
- The CI matrices 3.10–3.12 and the summary literal `3.10, 3.11, 3.12` → with 3.13. pandas 2.2.2 in the lock → a release with `cp313` wheels (FR2).
- The unchecked `int_zfilled` `length` → refused outside 1..18 at validation (AC3.1).
- The package docstring "for Pandas and Spark dataframes" → the package description (AC3.2).
- `trigger(frequency: int)` → `float` (AC3.3).
- The reference test parametrized from `docs/reference.md` itself → parametrized from `rand_engine.__all__` (AC3.4).
- The benchmark record of 0.7.0 (head 5920630, base 959f890) and its `TERMINAL_*` literals → this candidate's record (FR4).
- Untrue memory claims: the MkDocs-Material fallback, the unsourced gate costs, the no-run reservation, the CLI usage (FR5).
- Consumers of the changed `pyproject.toml` shape, for the PLAN to answer:
  - `tests/test_docs.py:379` reads `project.optional-dependencies` instead of `tool.poetry.extras` (AC1.7), and `tests/test_9_cli.py:222` reads `tool.poetry.dependencies` (kept, without `python`).
  - `auto_tag_publish_master.yml:36` and `auto_tag_publish_development.yml:36` grep one `^version = "M.m.p"` line, so the version stays a single line of that shape.
  - `auto_tag_publish_development.yml:152` runs `poetry version`.

## 6. Constraints, risks and open questions

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 dev loop and foundation | packaging metadata, lock, CI matrices, Spark skip predicate (one write set: `pyproject.toml`, `poetry.lock`) | FR1, FR2 |
| 2 bugs | the five bugs (four fixes), each a RED task then its fix | FR3 |
| 3 promote-facing | the benchmark record, after every measured-path job; the CHANGELOG lines | FR4, FR6 |
| 4 Reconciliation | memory, Tech Stack, summary | FR5 |

### Constraints

- No new dependency (invariant 10); the Python range and Tech Stack change together inside this candidate (invariant 11), the Tech Stack line in the Reconciliation `pe` task as rc-1 did.
- `pyproject.toml` keeps one version literal; the wheel's `Requires-Dist` lines are unchanged (AC1.3).
- Every moved assert (AC1.5, AC4.2) lands in its own `test(...)` commit naming its authority.
- Benchmarks run in CI only; the record is a copy, never a local run.

### Risks

| risk | mitigation |
|---|---|
| poetry-core adds 3.14+ classifiers from a static `[project]` | AC1.6 measures first; the operator's fallback cap |
| PyPI shows `License-Expression: MIT` instead of the License classifier | operator-accepted; the README `pypi/l` badge reads PyPI's license field |
| skipping Spark on 3.13 drops a leg under `--cov-fail-under=60` (`pr_to_development.yml`) | AC2.1 needs every leg green; the Windows 3.12 legs already run with Spark skipped |
| a later candidate touches a measured path after FR4 | AC4.3; that candidate records again |

### Open questions

None; the grill (`2026-10-16T150500Z-main-thread-grill-080-rc2`) answered both.
