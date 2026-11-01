# PLAN — Release: 0.8.2, candidate 2

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-2/SPEC.md` (7d681f8)

Sources: as-is review `.dadaia/handoff/rand-engine/2026-11-01T205713Z-dd-sw-engineer-sr-asis-0.8.2-rc2` (HEAD `9c1351e`), re-greped at `7d681f8` for the pre-mortem rulings R17-R25 (SPEC). Tree `worktrees/rand-engine/0.8.2/rc-2/wt-rc`. Every `path:line` is a `7d681f8` anchor; the Spark pool anchors move when the hotfix lane merges, so each task re-greps its own before editing. Open bugs: none in the picked set; `spark-pool-types-fail-or-corrupt` has its own lane.

## 1. As-is review

Bug history = `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>` plus the ledger. `bugs.py stats` prints no `rebuild-due` line, so no row is REBUILD by trigger; the one REBUILD is a demand-driven move.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `README.md:3`, `:39`, `:49` | "very fast"; "at NumPy speed" twice; no figure | `faker-extra-undocumented-unpinned-install` (README rebuilt as a landing page) | UPDATE | AC5.1, AC5.2: delete the adjectives, one measured figure. Landing constraints stay: `tests/test_docs.py:832-850`, `:217-226`. Net lines <= 0 |
| `llms.txt:3`, `:29` | "very fast", "at NumPy speed"; the one tracked copy is the repo root | 0 own | REBUILD (R6, R22) | the file moves to `rand_engine/llms.txt` by `git mv` and the wheel ships it; consumers in 1.1 |
| `rand_engine/cli.py:22`, `rand_engine/cases/faker.py.txt:2` | "sampled at NumPy speed" in the `list` line and the case header | 3 resolved, none on wording | UPDATE | word edit; `docs/tutorials/faker.md:20` includes the case, so it follows; `tests/test_9_cli.py:79` is the literal consumer (R4) |
| `rand_engine/__init__.py:1`, `pyproject.toml:4` | the same Summary string twice | `unused-runtime-deps-shipped` (deps only) | UPDATE | both in one commit; `tests/integrations/test_public_api.py:459-462` is the one equality decider |
| `docs/explanation.md:17`, `docs/5_RECIPES.md:10` | "Faker is slow per value" (R17 adds `5_RECIPES.md`) | 0 | UPDATE | the measured Faker figure of `docs/comparison.md:73` (0.769 s per 100,000 dicts); keep the BENCHMARKS link |
| `AGENTS.md:9` | "fast synthetic data generation" in the repo's purpose (R17) | 0 | UPDATE | one adjective deleted |
| `docs/comparison.md:20-22`, `:24`, `:87-88` | disclaims the comparison the README and Spark page now cite; "No winner is inferred" | 0 | UPDATE (R18) | the CI-run section states what it measured (workload, run 39153239357, three samples, medians, one run on one runner); `:87` loses "No winner is inferred"; the regression-table disclaimer stays, scoped. Net <= 0 |
| `mkdocs.yml:2`, `skills/rand-engine/SKILL.md:3` | "Fast ..."; "... data fast ..." | 0 | UPDATE | one word each; `SKILL.md:232` and `:8` stay (R20, R21); `tests/test_docs.py:269-273` needs "synthetic data" and "RandSpec" |
| `docs/2_SPARK_GENERATOR.md:1-7`, `:76-77` | opens with the mechanism; says Spark "coerces" any mixed pool | `docs-overstate-modifier-and-decimals-scope` (same defect class); `spark-mixed-type-pool-refused` (REBUILD `0479659`); open lane `spark-pool-types-fail-or-corrupt` | UPDATE, ADD (purpose paragraph) | the pool paragraph becomes R24's contract as the lane merged it, naming only pools `tests/test_3_spark_generator.py` pins by `dataType` and values. The purpose paragraph has no carrier, so it is the page's one ADD. Class repeat on this surface (second docs overstatement): the new text may name only pinned cases |
| `tests/test_3_spark_generator.py:728-736` (the pool cases), `:686` `arrow_conf` | the set-only case compares sets; `1` and `1.0` compare equal | `spark-mixed-type-pool-refused` | UPDATE (R24) | gains the `dataType` pin and the NaN-not-null pin under Arrow on and off; a tightening |
| `docs/errors.md:9-16`, `docs/compatibility.md:44-54` | absolute class claims; time-bound "no current library path raises it"; migration stops at 0.7 to 0.8 | 0 | UPDATE | R25's partition; one 0.8.2 paragraph pointing at the CHANGELOG `### Changed`, no list copied |
| `rand_engine/validators/exceptions.py:10-17`, `:31-37`, `:51-56`, `:88-93` | direct-raise list misses families; "A column's failure surfaces as ColumnGenerationError" and "lists every problem found" too absolute; `FileWriterError` says "raised nowhere" twice and "in this release" | 0 on these docstrings | UPDATE (DELETE the repeated sentence and the stale phrase) | four docstrings become contracts checked against `grep 'raise .*Error' rand_engine`; examples and doctests stay (`tests/test_docs.py:680-735`) |
| `rand_engine/main/spark_generator.py:48` | Portuguese comment | 0 | UPDATE | English; invariant 12, no other line |
| `pyproject.toml` keywords, classifiers, `[project.urls]` | 14 keywords, 5 URLs | 0 | UPDATE | add 3 keywords, 2 classifiers, 2 URLs; consumers `test_public_api.py:449`, `:465-473` (exact list, R3), `:476-486` |
| `tests/integrations/test_public_api.py:465` | `test_wheel_keywords_are_the_fourteen_search_terms`, exact 14-term list | 0 | UPDATE (R3, R21) | exact 17-term list; test renamed |
| `context7.json` | absent | 0 | ADD | no file carries it; about 8 lines of JSON; the registration is the operator's |
| `docs/*.md` (16 hand pages), `docs/BENCHMARKS.md`, `benchmarks/speed.py:248` `render`, `:319` | no front matter; `BENCHMARKS.md` is generated by `render()` and re-written by `.github/workflows/benchmarks.yml` | `benchmark-sibling-pairs-poisson-with-text-method` (a different unit of the file) | ADD (pages), UPDATE (`render`) | front matter is the only carrier of a page description; `BENCHMARKS.md`'s description comes from its one writer (R23); Home keeps `site_description` (Q3) |
| `scripts/docs_site.py:47`, `.github/workflows/docs.yml:47` | copies `input_root/"llms.txt"`; the workflow checks `site/llms.txt` | `docs-preview-deploy-fails-after-stable` (REBUILD, preview paths removed) | UPDATE | one source path; the published `/llms.txt` and the workflow line stay |
| `docs/1_DATA_GENERATOR.md`, `docs/4_CONSTRAINTS.md:85` | already state the net, the size rule and did-you-mean (rc-1) | `validated-specs-fail-in-generation`, `distincts-prop-negative-weight-drops-value` | KEEP | satisfied by rc-1; no task |
| `evals/tasks/e1-cold-discovery/instruction.md:1`, `specs/constitution.md` `## Direction`, `specs/memory/product/index.md:14`, `SKILL.md:232` | the simulated user's prompt; the internal north star; "Quote no speed numbers" | rc-1 FR8 | KEEP (R19, R20, AC5.5) | outside FR5's public texts or correct as written |
| memory atoms `spark-generator.md:26`, `get-started-cli.md:29`, `documentation.md:25,36`, `public-api.md`, `ARCHITECTURE.md` `## Structure` | repeat the old pool sentence, the `list` line, the root `llms.txt` | n/a | UPDATE at closure | the reconcile's memory pass (shape 9), never a job (`W:` refuses `specs/memory`) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which public texts may state speed | the `tests/test_docs.py` scan over the R4 list (AC5.1, R21: code spans and fences excluded) | the 12 files of the R4 list | the speed adjectives (grep over the list: 14 lines at `9c1351e`) |
| the wheel Summary equals the package docstring line | `test_public_api.py:459-462` | `pyproject.toml:4`, `__init__.py:1` | none |
| where `llms.txt` lives and who publishes it | `rand_engine/llms.txt` | `scripts/docs_site.py:47`, `docs.yml:47`, `tests/test_docs.py:196,201,217,230,420,641,877,892,911,936,946`, `tests/AGENTS.md:8`, the wheel | the root `llms.txt` |
| keywords, classifiers, project URLs | `pyproject.toml` | `test_public_api.py` exact asserts | none |
| the Spark pool facts | the `_spark_pool_problem` rule the lane merged, and `tests/test_3_spark_generator.py` pins | `docs/2_SPARK_GENERATOR.md`, atom `spark-generator.md:26` | the "coerces it" sentences |
| which class a failure raises | the raise sites (`grep 'raise .*Error' rand_engine`) | `exceptions.py` docstrings, `docs/errors.md`, `docs/compatibility.md:53-54` | the absolute claims |
| a page's description | its front matter `description` | `tests/test_docs.py` length and distinct check | none; Home keeps `mkdocs.yml` `site_description`; `BENCHMARKS.md` takes it from `render()` |
| the sitemap | the Zensical build (it already emits it) | none | none; nothing added |

### 1.2 Design choices the jobs carry

- The R4 scan lives in `tests/test_docs.py` as one list of files and one regex (SPEC AC5.1). It strips fenced blocks and inline code spans before matching, so "vectorized `NumPy`" facts stay.
- `cli.py:22` reads `Faker pools drawn once and sampled by NumPy through RandSpecs.faker_pool` (the literal J3.T1 pins and J3.T2 writes, one wording for both).
- The package Summary (`__init__.py:1`, `pyproject.toml:4`) drops "at NumPy speed" and keeps its other facts; both lines change in one commit.
- `context7.json`: `projectTitle` `rand-engine`, `folders` `["docs"]`, `excludeFolders` `["specs", "tests", "benchmarks", "evals"]`.
- `render()` writes a front-matter block as the first lines of its output. `docs/BENCHMARKS.md` is re-recorded as `render()` of `docs/benchmarks.json` with `absent` `{}` and `error` `None`, after the implementer proves that call reproduces the tracked file byte for byte before the change; no hand edit (R23).
- Spark purpose figures: 0.516 s dbldatagen against 1.341 s rand-engine at 1M rows, "one CI run, three samples, medians", run 39153239357 (`docs/comparison.md:72-75`).

### 1.3 Pre-mortem hits

| hit | answer | task |
|---|---|---|
| R3: the exact keyword list at `test_public_api.py:465-473` | 17 terms, test renamed, in a `test(...)` commit naming R3 and R21 | J1.T1 (impl J1.T2) |
| R4: the `cli.py:22` literal at `tests/test_9_cli.py:79` | updated to J3's literal in the `test(...)` commit naming R4 | J3.T1 (impl J3.T2) |
| R6, R22: `llms.txt` move, `docs_site.py:47`, wheel byte-equality, consumers | `git mv`, one source path, one new wheel test, the eleven `test_docs.py` consumers and `tests/AGENTS.md:8` repointed; `docs.yml:47`, `agent.md.txt:25`, `SKILL.md:8` and `CHANGELOG.md:70,77` unchanged | J2.T1, J2.T2 (impl J2.T3) |
| R17: `docs/5_RECIPES.md:10`, `AGENTS.md:9` | in the scan list; rewritten | J3.T1; J3.T3, J3.T5 |
| R18: `docs/comparison.md` | in the scan list; CI-run section states the measurement, `:87` fixed | J3.T1; J3.T4 |
| R19: `specs/constitution.md:11,14`, `product/index.md:14` | out of FR5; nothing edits `specs/`'s internal text | none |
| R20: `SKILL.md:232` | stays; J3.T2 touches line 3 only | J3.T2 |
| R21: scan excludes code spans, test renamed, `SKILL.md:8` and `agent.md.txt:25` unchanged | scan in J3.T1; rename in J1.T1; the two files have no task | J3.T1, J1.T1 |
| R23: `BENCHMARKS.md` description from `render()` | front matter in `render()`, file re-recorded | J5.T2 (impl J5.T3) |
| R24: the Spark pool contract as merged; the set-only case pin | `dataType` and NaN pins first, then the page | J4.T1; J4.T2 |
| R25: the error-class partition | `errors.md`, `exceptions.py`, `compatibility.md:53-54` | J4.T3, J4.T4 |
| `tests/test_docs.py` in four write sets | ordered by edges: Job 2, Job 3, Job 5; hunks differ (llms paths and context7, the scan, front matter) | DAG |
| consumers of `render()`: `.github/workflows/benchmarks.yml:51,57` print `docs/BENCHMARKS.md` into the step summary and the PR comment, `tests/test_benchmarks.py:193,260` read it | the front matter shows as text there; `test_benchmarks.py` is in Job 5's `W:` and stays green | J5.T2, J5.T3 |

## DAG

The SPEC puts every FR in its wave 4. The waves below are schedule waves: one per overlap of `W:`. Jobs of one wave write disjoint files.

External prerequisite, not a job: the Spark pool hotfix lane `wt/0.8.2/wt-hotfix-spark-pool-types-fail-or-corrupt` (fix `b5a2c91`, in rework) merges into `feature/0.8.2`, then the main thread runs `worktree sync` on this `wt-rc`. No rc-2 job opens before both. Job 4's tasks (the AC5.3 page and the R24 test pins) also re-read the merged rule.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `pyproject.toml`, `tests/integrations/test_public_api.py` |
| Job 4 | — | 1 | `docs/2_SPARK_GENERATOR.md`, `docs/errors.md`, `docs/compatibility.md`, `rand_engine/validators/exceptions.py`, `rand_engine/main/spark_generator.py`, `tests/test_3_spark_generator.py` |
| Job 2 | Job 1 | 2 | `llms.txt`, `rand_engine/llms.txt`, `scripts/docs_site.py`, `context7.json`, `tests/test_docs.py`, `tests/AGENTS.md`, `tests/integrations/test_public_api.py` |
| Job 3 | Job 2 | 3 | `README.md`, `rand_engine/llms.txt`, `rand_engine/cli.py`, `rand_engine/cases/faker.py.txt`, `rand_engine/__init__.py`, `pyproject.toml`, `docs/explanation.md`, `docs/5_RECIPES.md`, `docs/comparison.md`, `mkdocs.yml`, `skills/rand-engine/SKILL.md`, `AGENTS.md`, `tests/test_9_cli.py`, `tests/test_docs.py` |
| Job 5 | Job 3, Job 4 | 4 | `tests/test_docs.py`, `tests/test_benchmarks.py`, `benchmarks/speed.py`, `docs/BENCHMARKS.md`, `docs/getting-started.md`, `docs/compatibility.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md`, `docs/comparison.md`, `docs/reference.md`, `docs/errors.md`, `docs/explanation.md` |
| Job 6 | Job 5 | 5 | `CHANGELOG.md` |
| Reconciliation | Job 6 | 6 | `specs/memory/ARCHITECTURE.md`, `specs/memory/product/onboarding/documentation.md`, `specs/memory/product/generation/spark-generator.md`, `specs/memory/product/onboarding/get-started-cli.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/3_WRITING_FILES.md`, `docs/4_CONSTRAINTS.md`, `docs/5_RECIPES.md` |

Edge reasons: Job 2 after Job 1 (`test_public_api.py`); Job 3 after Job 2 (`rand_engine/llms.txt`, `tests/test_docs.py`) and so after Job 1 (`pyproject.toml`); Job 5 after Job 3 (`tests/test_docs.py`, `docs/explanation.md`, `docs/5_RECIPES.md`, `docs/comparison.md`) and Job 4 (the three docs pages). Job 1 and Job 4 run together: their write sets are disjoint.

### Schedule and sizing

- 20 tasks: Job 1 two (1 sr, 1 jr), Job 2 four (2 sr, 2 jr), Job 3 five (3 sr, 2 jr), Job 4 four (3 sr, 1 jr), Job 5 four (2 sr, 2 jr), Job 6 one (jr). By `who`: 11 sr, 9 jr. Each behaviour is a RED task then an implementation task. A text-only change whose test already exists, or that the docs run covers, is one task and its AC cell says so (J4.T2, J4.T3, J4.T4, J6.T1). The R24 pin task J4.T1 tightens an existing test and is green on arrival.
- Concurrency: tasks of one job with disjoint `W:` run together. The peak is 4 task trees: Job 3's T2 to T5 after T1, or Job 4's T1, T3, T4 beside Job 1's task.
- An implementation commit may not touch `tests/*` (`tests:` glob, `WT merge` refuses it), so `tests/AGENTS.md:8` rides J2.T1 and `tests/test_benchmarks.py` rides J5.T2.
- Net lines: every docs unit holds net lines <= 0 except the Spark purpose paragraph, `context7.json` and the front matter (SPEC FR5). Each implementation task states its net lines in its commit body.
- Test rulings reserved, each in a `test(...)` commit naming it: R3 and R21 (J1.T1), R4 (J3.T1), R24 (J4.T1). R6 and R22 change paths and add the wheel test (J2.T1, J2.T2); every other assert stays.
- Spark tests (J4.T1) run with the environment the dispatch brief names; no tracked file holds those paths.
- J5.T1's scratch Zensical build runs outside the tree under `.dadaia/tmp/`; it adds no tracked file and no dependency.
- Fix commits of an Origin bug: none (Origin is `operator-demand`).

### CHANGELOG placement

FR10's CHANGELOG entries are Job 6, not the reconcile. The reconcile's commit shape (`dd-gitflow-default` §3a, row 9: `wt-rc` reconcile writes `specs/memory/*`, `README.md`, `docs/*.md`) does not carry `CHANGELOG.md`; row 6 gives a task its `W:`. rc-1's PLAN did the same (its Job 8, T3). The closure memory pass (AC10.2) is the reconcile.

## Measured cost

- Gate law: no task adds a step to `verify:`, `verify-task` or the merge. The count is 27 runs of the job gate: 20 task merges, 6 job merges, one `wt-rc` merge. Per-run time is not re-measured for this PLAN; rc-1's PLAN (`Measured cost`) read 55.74-66.58 s of pytest per run at its own head, and that figure is not rc-2's.
- Product cost: none. No code path of `rand_engine/` changes behaviour; `render()` adds one text block per run of the benchmark script.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC5.1 | J3.T1 | J3.T2, J3.T3, J3.T4, J3.T5 |
| AC5.2 | no test (it would pin prose) | J3.T3 |
| AC5.3 | J4.T1 | J4.T2 |
| AC5.4 | the existing `tests/test_docs.py` page and doctest runs | J4.T3, J4.T4 |
| AC5.5 | no test | none (KEEP) |
| AC6.1, AC6.2 | J1.T1 | J1.T2 |
| AC6.3 | J2.T1, J2.T2 | J2.T3 |
| AC6.4 | J2.T1 | J2.T4 |
| AC6.5 | J5.T1, J5.T2 | J5.T3, J5.T4 |
| AC6.6 | J5.T1 (the scratch build) | none |
| AC10.1 | the existing `tests/test_docs.py` dated-header test | J6.T1 |
| AC10.2 | Reconciliation | — |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Memory cannot sit in a job file. Order, `dd-product-engineer`: (1) the closure memory pass of `MEMORY-UPDATE.md`: AC10.2's atoms (`spark-generator` pool contract, `get-started-cli` `list` line, `documentation` llms location, page descriptions and `context7.json`, `public-api` Project-URLs and keywords), `ARCHITECTURE.md` `## Structure` naming the `rand_engine/llms.txt` resource, `index.md`, `catalog.json`; (2) re-stamp the `derived-from` hashes in `docs/1..5` whose atoms changed, `git grep -n derived-from docs` before and after (shape 9); (3) `release.py phase CLOSURE`. `specs/constitution.md` stays (AC5.5).
