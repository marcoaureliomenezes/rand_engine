# PLAN — Release: 0.8.0, candidate 1 (adoption: docs, CLI, agent surface, 0.7.0 leftovers)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-1/SPEC.md`

## 1. As-is review

Paths are relative to the repo root. Ledger = `specs/bugs/BUGS.jsonl` + `_archive/bugs_histo.jsonl`. Source: as-is handoff `2026-10-14T191156Z-dd-sw-engineer-sr-asis-080-rc1`, amended by the main-thread rulings of 2026-10-14.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/validators/common_validator.py` `_spark_width_errors` :239-247 (+ `_np_core.py:34`, `_spark_core.py:38`) | THREE copies of the 2**53 width rule: validator :241 `max - min > 2**53` (off by one), `SparkCore.gen_ints` :38 `max - min + 1 > 2 ** 53`, `float_lattice_bounds` `_np_core.py:34` `high - low + 1 > 2 ** 53`; plus the derived magic `length > 15` :243. Diverge: `{'min':0,'max':2**53}` -> validator `[]`, core `ValueError: width (9007199254740993) must be <= 2**53` | `spark-integers-width-2pow53-validates-then-raises` (open) + the same class fixed 4 times: `spark-bigint-precision-lost`, `spark-floats-lattice-quadratic-slowdown`, `spark-floats-int64-endpoint-crashes`, `spark-floats-int-bounds-beyond-int64-crash`, `spark-floats-normal-int-kwargs-beyond-int64-crash`; the file carries 6 records | REBUILD | >= 2 bugs. Structural cause: the validator re-derives an engine limit instead of calling it, and every earlier fix patched one more copy. ONE predicate beside `float_lattice_bounds`; the validator and `int_zfilled` (width `10**length`, deleting the `15` literal) call it; net lines <= 0 (Job 1) |
| `rand_engine/core/_spark_core.py` `SparkCore.gen_ints` :32-39 | operator-written body (invariant 12); :38 is copy #2 of the rule | 9 on the file (`spark-integers-max-exclusive`, `spark-bigint-precision-lost`, `spark-floats-*` x4, timezone, empty-date-range, inverted-range) | UPDATE (:38 only; operator-approved by name) | :38 calls the predicate and the copy is deleted |
| `tests/test_1_common_validator.py:551-552` `test_integer_width_2_53_is_accepted` | asserts `max=2**53` validates `[]`: it encodes the bug; `tests/test_0_spark_core.py:337-341` asserts the core refuses the same pair | same bug | UPDATE (assert moves to refused) | main-thread ruling under invariant 3, cited in the J1.T1 `test(...)` commit |
| `rand_engine/validators/common_validator.py` `_raise` :267-278, footer :275 | the one formatter of every `SpecValidationError`; footer is the repo-root URL | 0 | UPDATE (one string) | only the footer points at the site, from one constant; 0 tests assert it today (Job 9) |
| `rand_engine/main/data_generator.py` `DataGenerator` | 128 lines; ruff D (numpy) 9 hits; `wrapped_df_generator` :57 is public by name but internal wiring (callers :102 :111 :123 :128) | 3 resolved (`writer-size-not-from-generator`, `writer-state-shared-across-chains`, `unbatched-save-refuses-transformed-null-column`) | UPDATE (docstrings only) | the >= 2 trigger is met by count but no behaviour changes and the fixes are KEEP-clean; a REBUILD would widen scope. No rename (consumers below) |
| `rand_engine/main/spark_generator.py` `SparkGenerator` | 62 lines; 7 D hits, malformed `Raises` :18; `map_methods` :29 consumed by 2 tests | 0 on the file | UPDATE (docstrings only) | text only; `map_methods` kept (tests/test_1_advanced_validator.py:508, tests/test_3_spark_generator.py:29) |
| `rand_engine/file_handlers/writer.py` `FileWriter` | 51 lines; 3 D hits | 0 direct | UPDATE (docstrings only) | documents `mode/format/option/options` once; both writers inherit |
| `rand_engine/file_handlers/_writer_batch.py` `save`, `_writer_stream.py` `trigger`/`start` | the objects `write`/`writeStream` return; undocumented; ruff D reports 0 on both files (ruff skips `_`-prefixed modules) | 2 resolved on `_writer_batch.py`; `writer-options-consumed-by-use` also on `_writer_stream.py` | UPDATE (docstrings only) | a green ruff D that never looks at the writers diverges from the demand (dd-code-review 4a); one pytest over `inspect` of the public callables closes it (J5.T1) |
| `rand_engine/examples/common_rand_specs.py` `RandSpecs` | 375 lines; 12 D hits (D400 x10, D401, D100); `faker_pool`, `from_schema` documented | 0 on the file | UPDATE (docstrings only) | `advanced_rand_specs.py` and `templates/` are not public surface and stay untouched |
| `rand_engine/__init__.py` | 6 lines, `__all__` = 3 names, no `__version__`, no `py.typed` | 0 | UPDATE (+ `__version__`, `py.typed`, docstring) | `__version__` via `importlib.metadata` with a short fallback, out of `__all__` (invariant 1; `test_public_api.py:47` `len == 3` stays); no unit carries the version |
| `rand_engine/{main,file_handlers,core,utils}/` | 4 of 8 package dirs lack `__init__.py` | 0 | ADD 4 empty files | repro: mkdocstrings `::: rand_engine.DataGenerator` -> `AliasResolutionError`; with the files the strict build passes (2.2 s). No unit can carry it |
| `tests/test_docs.py` | executes `docs/*.md` python blocks (non-recursive), README blocks, README/`llms.txt` link rules, CHANGELOG tokens; docstrings cite AC ids | 1 (`docs-overstate-modifier-and-decimals-scope`, resolved) | UPDATE | owner of the docs contract; gains the docstring check (J5), recursive glob and tutorial rules (J8), skill (J10), README/CHANGELOG/`llms.txt` rules (J11); asserts tighten or add, none loosens; AC ids leave its docstrings (J8.T1) |
| `README.md` | 127 lines; `pip install faker` :62 contradicts the extra `faker >=28.4.1,<29`; 10 `derived-from` markers | `faker-extra-undocumented-unpinned-install` (open); `docs` surface 1 resolved | REBUILD | the purpose changes (reference -> landing); patching :62 inside the old structure is a layer. The faker bug closes inside the rebuild with its RED test (J11) |
| `docs/1_DATA_GENERATOR.md` .. `4_CONSTRAINTS.md`, `BENCHMARKS.md`, `benchmarks.json` | 5 guides executed by test_docs | 1 resolved | KEEP | already the how-to layer of the site |
| `docs/5_RECIPES.md` | 4 of 6 sections restate the CLI cases; holds the only `python no-run` | 0 | KEEP | ruling 6: deleting sections moves 2 existing asserts; the case file is the authority for CLI-case code |
| site shell (`mkdocs.yml`, `docs/getting-started.md`, `explanation.md`, `reference.md`, `docs/tutorials/*.md` x5, `docs/index.md` built from README) | nothing | 0 | ADD | no unit carries a site. Zensical writes `site/` and `.cache/` inside the tree: gitignored, built in CI only |
| `llms.txt` | root file, 7 absolute `blob/master` links, 3 `derived-from` markers, tested by `test_links_resolve[llms.txt]` | 0 | UPDATE | stays the one source; the deploy copies it to the site root (Job 8) |
| `CHANGELOG.md` :10 | `## [0.7.0] - Unreleased` while 0.7.0 is on PyPI | `changelog-070-header-says-unreleased` (open) | UPDATE | dated header + the 0.8.0 section; RED: every header carries an ISO date |
| `pyproject.toml` + `poetry.lock` | version 0.7.0; test group `pyspark ^3.5.0` (lock 3.5.7), `setuptools ^78.1.1` (lock 78.1.1); no scripts, no docs/lint group; `documentation` = tree URL | `dependabot-pyspark-357-ghsa-9437`, `dependabot-setuptools-781-ghsa-h35f` (open, test group) | UPDATE | pyspark 3.5.8 fits `^3.5.0` (lock only); setuptools 83 does not fit `^78.1.1` (manifest line changes). Writers by edge: J2 (deps, groups, version) -> J6 (scripts) -> J9 (documentation URL) |
| `.github/workflows/{auto_tag_publish_development,auto_tag_publish_master,pr_to_master,test_on_push}.yml` | no top-level `permissions:` (`benchmarks.yml:8` and `pr_to_development.yml:9` have it) | `workflow-missing-top-level-permissions` (open) + 3 resolved on the surface | UPDATE | `permissions: contents: read` x4; jobs with their own scopes keep them. The REBUILD trigger (>= 2 bugs) is met and rejected: a reusable workflow moves the PyPI publish job, whose Trusted Publisher is bound per file (ruling 10, out of scope) |
| `.github/workflows/*.yml` third-party refs | 6 mutable refs in 4 files: `codecov/codecov-action@v4` x3 (pr_to_master:79, pr_to_development:219, auto_tag_publish_development:119; each gets `secrets.CODECOV_TOKEN`), `pypa/gh-action-pypi-publish@release/v1` x2 (auto_tag_publish_master:156, auto_tag_publish_development:260; both `id-token: write`), `aquasecurity/trivy-action@master` (pr_to_development:108) | `workflow-actions-mutable-refs` (open): the record's scope (2 refs) is wrong | UPDATE | pin the 6 to full SHAs; `actions/*` and `github/*` stay tags. The repro regex misses `codecov@v4`: the sweep greps every non-`actions/`/`github/` ref |
| `.github/workflows/auto_tag_publish_master.yml` :267 :277 :335 :336, `.github/workflow_info.md` | :267 prints `rand_engine.__version__` (true after Job 4); :277 :335 :336 say `0.5.6`; `workflow_info.md` 1518 lines, 9 stale hits, 0 readers | `workflow-summary-text-stale` (open) | UPDATE (yml) / DELETE (`workflow_info.md`) | a prose mirror of the YAML whose staleness recurs; `pipeline_doc.md` (0 stale hits) stays |
| `.github/workflows/docs.yml` (new) | nothing | 0 | ADD | no workflow builds or deploys a site; born compliant with AC2.2/AC2.3 |
| `rand_engine/cli.py`, `__main__.py`, `cases/<slug>.py.txt` x5 | nothing; the 5 cases live as README/recipes snippets | 0 | ADD | no unit carries argv or packaged scaffolds; stdlib `argparse`. Cases ship as `.py.txt` so `test_every_shipped_module_imports` (`rglob("*.py")`, test_public_api.py:343-352) never executes them and the slug `test-data` need not be an identifier |
| `skills/rand-engine/SKILL.md` (new, outside the wheel) | nothing | 0 | ADD | its python blocks run through the docs fence extractor, so it cannot drift from `METHOD_CATALOG` |
| `tests/integrations/test_public_api.py` | wheel test builds with `poetry build` and reads METADATA | 0 | UPDATE | adds `py.typed`, no path outside `rand_engine/`, `__version__`, entry point, case files, documentation URL |
| `AGENTS.md` (repo) `verify:` lines, `tests/AGENTS.md` layout | `verify:` = install + pytest; no lint configured | 0 | UPDATE (repo law, in scope per ruling 4) | ruff D joins the three `verify:` lines (J5.T6); `test_9_cli.py` gets its layout line (J6.T3); Tech Stack/Gates update is a `pe` task in Reconciliation (Reconciliation) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| is an integer width exactly representable on Spark | one predicate beside `float_lattice_bounds` in `rand_engine/core/_np_core.py` | `common_validator.py` `_spark_width_errors` (integers; `int_zfilled` via width `10**length`), `float_lattice_bounds`, `SparkCore.gen_ints` :38 (only with the invariant-12 approval) | validator literal `2**53` :241 and `length > 15` :243; `_spark_core.py:38` literal (if approved); `_np_core.py:34` literal |
| which version is installed | `pyproject.toml` `version`, read by `importlib.metadata` as `rand_engine.__version__` | workflow summaries (master :267, pr_to_development :286, development :188), the wheel test | the `0.5.6` literals (master :277 :335 :336) |
| the code of get-started case N | `rand_engine/cases/<slug>.py.txt` | `rand_engine/cli.py` (copies it), the tutorial page (snippet include, not a restated fence), the case test (executes the written file) | none (`docs/5_RECIPES.md` kept) |
| what a public call accepts and returns | the docstring in source | mkdocstrings reference page, ruff D, doctest, `inspect` check | none |
| what a RandSpec method accepts | `METHOD_CATALOG` (`rand_engine/validators/method_specs.py`) | validators, docs tables, `SKILL.md` (executed blocks) | none |
| where `SpecValidationError` points the reader | one base-URL constant used by the `_raise` footer | `pyproject.toml` `documentation` (one wheel-test assert compares them) | the repo-root URL in the footer |
| what README / `llms.txt` / site say about the library | README (landing) and root `llms.txt`; the site copies both at deploy | `test_docs.py` link and block rules | the `derived-from` markers in the rebuilt README |
| which token a workflow job holds | each workflow's top-level `permissions: contents: read` + the job's own widening | `docs.yml` (born compliant) | none |

### 1.2 Consumers of every changed name, format or fix line

Associated repos of the context: 0. The counts are the as-is review's greps; no `dd-researcher` pre-mortem ran (the review was read-only), so each hit is answered here.

| changed | consumers | answered by |
|---|---|---|
| `rand_engine.__version__` added | test_public_api.py:296-312 (tolerant), 3 workflow lines, `__all__` asserts :47 :358 :375 (unchanged) | J4, J7 |
| 4 new `__init__.py` | `test_every_shipped_module_imports` (`rglob`); `test_private_module_naming_convention` skips `__*` | J4 |
| `__main__.py`, `cli.py`, console script, `cases/*.py.txt` | same import test (`main()` behind `if __name__`; `.txt` not imported); `verify:` installs `--no-root`, so tests call `main(argv)` | J6 |
| README structure | `test_readme_python_blocks_execute_in_order`, `test_links_resolve[README.md]` (the skill and the docs must exist first) | J11 after J8, J10 |
| `llms.txt` | `test_links_resolve[llms.txt]`; the site copy | J11 |
| new `docs/**/*.md` | `test_doc_python_blocks_execute_in_order` globs `docs/*.md` (made recursive in J8.T1); `python no-run` only in `5_RECIPES.md` | J8 |
| `_raise` footer | 0 tests or docs assert it | J9 |
| width message `width (max - min) must be <= 2**53` | test_1_common_validator.py:549 (`2^53` / `2**53` substring), test_0_spark_core.py:337-341 | J1 keeps the substring |
| `map_methods`, `wrapped_df_generator` (kept) | tests and data_generator.py callers | unchanged |
| `documentation` URL, README/`llms.txt`/CHANGELOG absolute GitHub links | `pyproject.toml:10`, README :120-127, `llms.txt` (7), CHANGELOG :314-316 (3) | J9, J11 |
| `.github/workflow_info.md` deleted | 0 readers in `.github`, `rand_engine`, `tests`, `docs`, `README.md`, `benchmarks` | J7 |
| 6 pinned actions | `.github/workflows` only; Trusted Publisher bound to unchanged file names | J3 |
| `derived-from` markers | the closure memory pass | J11 drops the README markers; the Reconciliation job leaves the landing page alone |

## 2. Rulings carried

- Invariant 12: the operator approved `SparkCore.gen_ints` by name ("Aprovo", 2026-10-14); `_spark_core.py:38` calls the one predicate (Job 1).
- `__version__` from `importlib.metadata` with a short fallback; a wheel test proves the value (Job 4).
- Repo-law edits are in scope: `verify:` lines (J5.T6), `tests/AGENTS.md` (J6.T3), Tech Stack and Gates (Reconciliation, `pe`).
- Workflow bugs (Jobs 3, 7): no test, no YAML-parser dependency; every commit body quotes the bug's repro grep at zero hits.
- Spark docstring examples carry `+SKIP` (Job 5). The 1.8 s CLI start-up is accepted. A reusable workflow is out of scope.
- A RED task lands its test marked `@pytest.mark.xfail(strict=True, reason=...)`; the implementation task (a separate dispatch and tree) lists that test file in its `W:` and removes only the marker line. Tasks of one job that share a test file run in sequence.

## 3. Gate costs (measured on this machine, 2026-10-14)

Baseline `verify:` pytest run: 72.2 s wall (1050 passed, excluding `poetry install`). Added by this release:

| gate | where | measured | note |
|---|---|---|---|
| ruff D on 6 modules | `verify:` lines | 0.03 s | |
| docstring `inspect` check + doctest | in the pytest run | < 1 s | 8 prototype examples; the 2.4 s standalone run includes 1.8 s package import |
| 5 CLI cases in-process | in the pytest run | 0.85 s | shares the suite's Spark session |
| 1 CLI case as a plain-python subprocess | in the pytest run | 2.4 s | the claim "runs under plain python" |
| Total added to `verify:` | | about 4.3 s, about 6% of 72.2 s | below one `verify:` run |
| Zensical strict build | `docs.yml` only | 2.2 s | MkDocs-Material fallback 0.91 s |
| 5 cases as 5 subprocesses (not adopted) | | 21.7 s | 20 s more for the same proof |

No requirement applied to every task is added by this PLAN.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/test_1_common_validator.py`, `tests/test_0_spark_core.py`, `tests/test_3_spark_generator.py`, `rand_engine/core/_np_core.py`, `rand_engine/validators/common_validator.py`, `rand_engine/core/_spark_core.py` |
| Job 2 | — | 1 | `pyproject.toml`, `poetry.lock` |
| Job 3 | — | 1 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml` |
| Job 4 | Job 2 | 2 | `tests/integrations/test_public_api.py`, `rand_engine/__init__.py`, `rand_engine/main/__init__.py`, `rand_engine/file_handlers/__init__.py`, `rand_engine/core/__init__.py`, `rand_engine/utils/__init__.py`, `rand_engine/py.typed` |
| Job 5 | Job 2 | 2 | `tests/test_docs.py`, `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `rand_engine/file_handlers/writer.py`, `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/file_handlers/_writer_stream.py`, `rand_engine/examples/common_rand_specs.py`, `AGENTS.md` |
| Job 6 | Job 2, Job 4 | 3 | `tests/test_9_cli.py`, `rand_engine/cli.py`, `rand_engine/__main__.py`, `tests/AGENTS.md`, `rand_engine/cases/test-data.py.txt`, `rand_engine/cases/lake.py.txt`, `rand_engine/cases/kafka.py.txt`, `rand_engine/cases/databricks.py.txt`, `rand_engine/cases/faker.py.txt`, `tests/integrations/test_public_api.py`, `pyproject.toml` |
| Job 7 | Job 3, Job 4 | 3 | `.github/workflows/auto_tag_publish_master.yml`, `.github/workflow_info.md` |
| Job 8 | Job 3, Job 5, Job 6 | 4 | `tests/test_docs.py`, `mkdocs.yml`, `docs/getting-started.md`, `docs/explanation.md`, `docs/reference.md`, `.gitignore`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `.github/workflows/docs.yml` |
| Job 9 | Job 1, Job 6 | 4 | `tests/test_1_common_validator.py`, `tests/integrations/test_public_api.py`, `rand_engine/validators/common_validator.py`, `pyproject.toml` |
| Job 10 | Job 6, Job 8 | 5 | `tests/test_docs.py`, `skills/rand-engine/SKILL.md` |
| Job 11 | Job 8, Job 9, Job 10 | 6 | `tests/test_docs.py`, `README.md`, `CHANGELOG.md`, `llms.txt` |
| Reconciliation | Job 7, Job 11 | 7 | `specs/memory/**`, `specs/releases/0.8.0/_RELEASE.json` |

Overlaps across waves are ordered by an edge: `pyproject.toml` (Job 2 -> Job 6 -> Job 9), `.github/workflows/auto_tag_publish_master.yml` (Job 3 -> Job 7), `common_validator.py` (Job 1 -> Job 9), `tests/test_docs.py` (Job 5 -> Job 8 -> Job 10 -> Job 11), `tests/integrations/test_public_api.py` (Job 4 -> Job 6 -> Job 9). Inside each wave the `W:` sets are disjoint. Job 1 comes first and Reconciliation last.

### Reconciliation (no job file; `reconcile` tree, `RC-FLOW.md` step 4)

| task | who | W: |
|---|---|---|
| memory pass | pe | `specs/memory/**` |
| closure entries (`release.py` verbs only) | pe | `specs/releases/0.8.0/_RELEASE.json` |

- Constitution invariant 11 (ruling 4): `ARCHITECTURE.md` `## Tech Stack` gains Zensical, mkdocstrings (numpydoc), MkDocs-Material fallback and ruff; `QUALITY.md` `## Gates` drops "No lint or type checker is configured" and states the ruff D and docstring gates with the PLAN §3 costs.
- Feature atoms follow the code diff per `MEMORY-UPDATE.md`; the rebuilt README carries no derived markers, so the pass does not rewrite it.
