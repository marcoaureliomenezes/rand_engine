# PLAN — Release: 0.8.2, candidate 1

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-sw-engineer-sr
**SPEC:** `rc-1/SPEC.md` (ac40864)

Sources: as-is review `.dadaia/handoff/rand-engine/2026-10-31T160733Z-dd-sw-engineer-sr-asis-0.8.2-rc1` (measured at `ac30edb`), SPEC handoffs `2026-10-31T164430Z` and `2026-10-31T170039Z`, the pre-mortem rulings R1-R11 as the SPEC records them. Tree `worktrees/rand-engine/0.8.2/rc-1/wt-rc`. The hotfix lanes `85e819d` and `bb6afc9` have landed; FR5 and FR6 (rows for the public texts, `llms.txt`, `pyproject.toml` urls, `context7.json`, `docs/errors.md`) are rc-2's and have no row here.

## 1. As-is review

Bug history = `git log -E --grep '^(fix|refactor)\(bugs\): ' -- <file>` plus the ledger. `bugs.py stats` prints no `rebuild-due` line, so each REBUILD below is a judgement trigger, named in `why`.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `validators/method_specs.py` `METHOD_CATALOG` and the `semantic` rules (`_distincts_prop`, `_distincts`, `_dates`; `unix_timestamps` and `distincts_map_prop` have none) | 21 methods, one hand-kept `semantic` per method copying a `gen_*` precondition; the engine and the Spark core are the other copies | open `distincts-prop-negative-weight-drops-value`, `validated-specs-fail-in-generation`; 18 archived correlates; task fixes `ea3f0ec`, `7c3566b`, `85a860f`; REBUILDs `4a95036`, `572ee4e` | UPDATE (REBUILD in 0.9.0) | the `semantic` slot carries every new rule, so no second path; this is rule 19 of a class closed by one more rule each time, and the structural cause (hand copies) is the 0.9.0 catalog REBUILD. Net lines positive, reason: rules the net cannot see (negative weight, Spark has no net) |
| `validators/method_specs.py` date rule (`_dates`) and `main/spark_generator.py` dispatch of `unix_timestamps` and `dates` (`:103-106`, `:175`) | validators accept any bound string; NumPy parses through `_parse_date_bound` with a `%Y-%m-%d` fallback, Spark through bare `strptime` | open `date-bound-parse-diverges-numpy-spark`; 6 archived on `_np_core`/`_spark_core` dates; feature task `0.7.0-rc2/J4.T2` (`1b116d8`) | REBUILD | two deciders of one fact (repro in the as-is handoff: `d/m/Y` format with an ISO bound generates on NumPy, raises on Spark, both validators accept); `caused_by` a feature task makes the fix the unit's REBUILD |
| `validators/advanced_validator.py` `validate` :44, `_complex_errors` :240 | per-column loop, no cross-column check; `pattern.count(replacement)` counts substrings, the engine counts characters | open `correlated-cols-overwrite-existing-column`, `validated-specs-fail-in-generation`; archived `distincts-multi-map-*`, `fk-parent-args-validates`, `validator-engine-schema-drift` | UPDATE | one added step in `validate` for output-name uniqueness; `_complex_errors` takes the one-character rule; the file's 43 message literals stay (error format is 0.9.0) |
| `AdvancedValidator.validate_with_warnings` :429, `CommonValidator.validate_spark_with_warnings` :250 | print-and-return-bool twins with the 80-character banner | 0 | DELETE | `git grep with_warnings` outside `specs/` and `CHANGELOG.md`: only the two definitions; deleting shrinks both files before Jobs 3-7 edit them (R10) |
| `validators/common_validator.py` `_validate_method_parameters` :64, `unknown_key_errors` :113, spark column check :180, `_raise` :262 | typed parameter check; three hand-built name-list messages; banner raise shared by both engines | archived `validator-warnings-raised-as-errors`, `probability-wrong-type-escapes-validation`, `validator-engine-schema-drift`, `method-registry-has-five-owners`, 2 more | UPDATE | the name-list sites consult one new helper; `_raise` KEEP (format is 0.9.0); the helper is the only ADD, since no unit holds a suggestion rule (stdlib `difflib`, about 8 lines) |
| `validators/exceptions.py` | Portuguese docstrings with stale examples; `FileWriterError` raised nowhere | 0 | REBUILD docstrings; KEEP `FileWriterError` (D1) | docstrings rewritten in English from the raise sites; deleting the class breaks an import in a patch release, and it is documented (`docs/errors.md:15,61`, `public-api.md:36`, `tests/test_docs.py:795`) |
| `main/data_generator.py` `__validate_spec` :69, `__evaluate_spec` :63 | validates once at construction; a callable is re-evaluated unvalidated at every `get_df`, microbatch and writer seam | archived `writer-size-not-from-generator`, `writer-state-shared-across-chains`, `unbatched-save-refuses-transformed-null-column` | UPDATE | static validation at every callable evaluation; the net once at construction. It sits here because `main` imports `validators`, and the reverse would cycle |
| `main/data_generator.py` `_resolve_size` :187 | checks only `None` | `writer-size-not-from-generator` | UPDATE | becomes the one size decider (a module function it and Spark call); all consumers reach it |
| `file_handlers/_writer_batch.py` `_resolved_size` :55, calls :230, :395 | second size rule, reached only by `write.save` | `writer-numfiles-rows-per-file`, `writer-size-not-from-generator`, `writer-options-consumed-by-use` | DELETE | a copy of the decider above; its test (`tests/test_5_files_write_batch.py:538-551`) asserts only the error and the destination bytes, so it stays green |
| `main/spark_generator.py` unset check :160-161 | its own `None`-only size rule | 0 | DELETE | third size decider (R1) |
| `main/data_generator.py` `_file_seam` :88 `cache(partial(...))` | memo of the catalog schema | introduced by `ffdb0d1` | DELETE | consulted only when a table has an Arrow-null field; the uncached call is 0.019 ms (the grill's "never hits" was wrong; the delete stands on cost) |
| `file_handlers/file_handler.py` `handle_path`, `_writer_stream.py`, `_writer_batch.py` destination join | one decider, both writers consume the stem | `writestream-bare-name-targets-filesystem-root`, `writestream-drive-relative-targets-drive-root` (REBUILT by `85e819d`, `bb6afc9`, net -3 lines) | KEEP | landed on the work branch; no task; the CHANGELOG names it |
| `core/_np_core.py` gen_distincts :219, gen_distincts_prop :225, `_parse_date_bound` :16, gen_unix_timestamps :231, gen_dates :239 | the engine; the fallback parse | 6 archived | KEEP | invariant 12: every rule lands in the catalog or the validator, none in a `gen_*`; `_parse_date_bound` is the date authority |
| `core/_spark_core.py` gen_distincts_prop :69, gen_unix_timestamps, gen_dates | pool expansion copy; plain `strptime` | 9 archived | KEEP | invariant 12 and ADR 0003; the dispatch passes bounds the authority parsed (R9), so it needs no edit; `git diff` of `rand_engine/core/` stays empty |
| `core/_py_core.py` `METHODS` :71-91, `main/_rand_generator.py` `map_methods`, `generate_first_level`, `apply_modifiers`, `main/spark_generator.py` `map_methods` | key sets equal the catalog today; `apply_modifiers` runs `_validate_modifiers` on every call | `method-registry-has-five-owners`, `distincts-map-column-order-reversed` | KEEP | the net calls `generate_first_level` and `apply_modifiers` as they are; the duplicate-name overwrite becomes unreachable by the validator step; folding the bindings is 0.9.0 |
| `rand_engine/cases/test-data.py.txt`, `tests/test_9_cli.py:161-180` | the starter opens with `# Databricks notebook source` and holds three `# COMMAND ----------` lines; the test asserts both for every runnable slug | `get-started-scaffold-shadows-package` (archived) | UPDATE | only `databricks.py.txt` is a notebook; the assert narrows to that slug under D5 and R11 (a `test(…)` commit names the rulings) |
| `tests/test_docs.py` `_surface` :700, doctest list :730 | the exceptions module is outside both | 0 | UPDATE | R5: the in-suite check covers it, a new case and no loosened assert |
| `docs/1_DATA_GENERATOR.md` date section | the `%Y-%m-%d` fallback is undocumented (`:66-67`) | `date-format-required-but-docs-omit-it` (archived) | UPDATE | AC4.3; the page's fenced blocks run in `tests/test_docs.py` |
| `pyproject.toml` test group, `poetry.lock`, `benchmarks/comparison-requirements.txt` | setuptools 83.0.0 (GHSA-xmj3-9gf7-h52w) | `unused-runtime-deps-shipped`, two dependabot records | UPDATE | AC7.6; the lock is the check |
| `pyproject.toml` version, `tests/integrations/test_public_api.py:558`, `CHANGELOG.md` | 0.8.1 | 0 | UPDATE | AC9.1, AC9.2 |
| `evals/` (new) | absent | 0 | ADD | no unit carries an agent eval; stays out of `tests/`, of `verify:` and of CI |
| `utils/stream_handler.py`, `cli.py`, `templates/`, `examples/`, `core/_keys.py` | untouched by the picked set | cli 2, examples 2 | KEEP | `StreamHandler` is operator code (invariant 12) |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which methods exist, their engines and parameters | `METHOD_CATALOG` `method_specs.py:312` | both validators, `data_generator.py` `_catalog_schema`, `spark_generator.py` | none in rc-1: the engine bindings fold in 0.9.0 |
| is this parameter value acceptable | the catalog's `semantic` functions (`method_specs.py:152-300`); new rules join them | `CommonValidator._validate_method_parameters` for both engines | none. Only the date bound has a callable engine decider; the pool type, the weights and the replacement mirror an inline precondition (`_np_core.py:220`, `:226`, `_py_core.py:32-36`), and the net is the drift detector |
| does a date bound parse | `_parse_date_bound` `_np_core.py:16` | the catalog date rule, `NPCore.gen_unix_timestamps`, the Spark dispatch | validators accepting any bound string; the Spark dispatch handing raw bounds to `SparkCore` |
| do two output columns share a name | `AdvancedValidator.validate` (new step) | none | none (`_rand_generator.py` keeps its assignment, now unreachable) |
| is the size usable | `resolve_size` in `data_generator.py`, called by `DataGenerator._resolve_size` | `get_df`, `stream_dict`, both writers through `size_def`, `SparkGenerator.get_df` | `_writer_batch._resolved_size`; the Spark unset check |
| does an accepted spec generate | the one-row net in `DataGenerator.__validate_spec`; a detector of rule gaps, never a rule source | construction only; each callable evaluation takes static validation | none |
| where does a write land | `FileHandler.handle_path` | both writers | landed (`85e819d`, `bb6afc9`) |
| which close name to suggest | one helper in `CommonValidator` over `difflib.get_close_matches` | method, kwarg, column-key sites of both validators | none |
| which exception and text a bad spec raises | `CommonValidator._raise` | `validate_and_raise`, `validate_spark_and_raise`, `SparkGenerator.__init__`, the net's refusal | the two `*_with_warnings` printers |
| does a starter carry notebook markers | the slug: `databricks` only | `tests/test_9_cli.py`, the tutorial snippet | the markers in `test-data.py.txt` |

### 1.2 Design choices the jobs carry

- Net: `RandGenerator(spec).generate_first_level(1, np.random.default_rng(0), key_seed=0)` then `apply_modifiers` on its own generator. Embedded transformers run in `apply_embedded_transformers`, never called, so no transformer runs by construction. A `RandEngineError` or `ColumnGenerationError` becomes `SpecValidationError` through `CommonValidator._raise`.
- Callable: `__evaluate_spec` validates its result when the spec is callable; a dict is validated once at construction (D3).
- Dates: the catalog rule calls `_parse_date_bound` and catches its `ValueError`; the Spark dispatch re-renders the parsed bound with `strftime(date_format)`; the engine files stay untouched (R9). The rule is `start < end` on parsed values, the engine's own precondition (`start == end` is refused too, since NumPy raises on it).
- Size: one module function `resolve_size(size)` in `data_generator.py`. The rejected alternative, a new shared module, is an ADD; `spark_generator.py` importing it stays inside `main/`, with no reverse import.
- Names: output names are a column's `cols`, else its key; the refusal names the name and both definitions.
- Did-you-mean: a `CommonValidator` helper, no new module; `difflib` is stdlib, no dependency.
- TREE-5 (six superseded `specs/**/AGENTS.md` templates, a warning): not a task. `W:` refuses `specs/memory/AGENTS.md`, and no commit shape of the `wt-rc` carries the other five (`dd-gitflow-default` §3a rows 8-9). It is the precondition P0 below, a lane of the main thread.

### 1.3 Pre-mortem hits that stay in rc-1

| hit | answer | task |
|---|---|---|
| R1: `_writer_batch._resolved_size` (callers :230, :395), Spark unset check (`spark_generator.py:160-161`); `tests/test_5_files_write_batch.py:538-551`, `tests/test_8_consistency.py:377-380` | the two copies deleted; both tests pass unchanged; no test asserts the Spark unset text (grep 0 hits) | J4.T2 (red J4.T1) |
| R2: `tests/test_8_consistency.py:188-197` asserts `RandEngineError` and not `SpecValidationError` | flipped to `SpecValidationError` at construction in a `test(…)` commit naming R2; `docs/4_CONSTRAINTS.md:85` is rc-2's | J7.T2, J7.T4 |
| R5: exceptions outside `_surface` and the doctest list | added | J2.T3 (impl J2.T4) |
| R7: `tests/test_docs.py:858-862` wants a dated header | `## [0.8.2] - <closure date>` | J8.T3 |
| R9: `spark_generator.py:103-106`, `:175`; `_spark_core.py:92`, `:98-105` | dispatch passes parsed bounds; `core/` untouched; `tests/test_0_spark_core.py` unchanged | J3.T4 (red J3.T2) |
| R10: `with_warnings` consumers | grep 0 hits outside `specs/` and `CHANGELOG.md` | J2.T1 |
| R11 and D5: `tests/test_9_cli.py:161-172` | renamed and narrowed in the same `test(…)` commit | J2.T5 (impl J2.T6) |
| D1: `FileWriterError` consumers (`docs/errors.md:15,61`, `public-api.md:36`, `tests/test_docs.py:795`) | stay; they pass unchanged | J2.T4 |
| `cache` removal: `tests/test_5_empty_schema.py`, `tests/test_5_files_write_batch.py` | pass unchanged | J2.T2 |
| setuptools consumers: `pyproject.toml:48`, `benchmarks/comparison-requirements.txt:5`, the workflows install it unpinned | pins moved; the lock resolves | J1.T4 |

R3, R4, R6, R8 and their consumers are rc-2's.

## DAG

Waves follow the SPEC ranking. The SPEC's wave 3 (FR7 hygiene) runs as wave 2 because it is the DELETE and REBUILD set: it shrinks `advanced_validator.py`, `common_validator.py` and `data_generator.py` before the ADD jobs edit them, and the rank is not a dependency. SPEC wave 2 (the foundation) is waves 3-6, one wave per overlap of `W:` (all jobs of a wave write disjoint files). Job 1 is first: its merge is followed by barrier B1, the 0.8.1 baseline, before any behaviour merges.

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `benchmarks/comparison-requirements.txt`, `evals/README.md`, `evals/run.py`, `evals/tasks/e1-cold-discovery/instruction.md`, `evals/tasks/e1-cold-discovery/task.toml`, `evals/tasks/e1-cold-discovery/tests/check.py`, `evals/tasks/e2-named-related-tables/instruction.md`, `evals/tasks/e2-named-related-tables/task.toml`, `evals/tasks/e2-named-related-tables/tests/check.py`, `evals/tasks/e3-fix-by-error/environment/spec.py`, `evals/tasks/e3-fix-by-error/instruction.md`, `evals/tasks/e3-fix-by-error/task.toml`, `evals/tasks/e3-fix-by-error/tests/check.py`, `poetry.lock`, `pyproject.toml`, `tests/integrations/test_public_api.py` |
| Job 2 | Job 1 | 2 | `rand_engine/cases/test-data.py.txt`, `rand_engine/main/data_generator.py`, `rand_engine/validators/advanced_validator.py`, `rand_engine/validators/common_validator.py`, `rand_engine/validators/exceptions.py`, `tests/test_9_cli.py`, `tests/test_docs.py` |
| Job 3 | Job 2 | 3 | `docs/1_DATA_GENERATOR.md`, `rand_engine/main/spark_generator.py`, `rand_engine/validators/method_specs.py`, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`, `tests/test_3_spark_generator.py` |
| Job 4 | Job 3 | 4 | `rand_engine/file_handlers/_writer_batch.py`, `rand_engine/main/data_generator.py`, `rand_engine/main/spark_generator.py`, `tests/test_2_data_generator.py`, `tests/test_3_spark_generator.py` |
| Job 5 | Job 3 | 4 | `rand_engine/validators/advanced_validator.py`, `rand_engine/validators/method_specs.py`, `tests/test_1_advanced_validator.py` |
| Job 6 | Job 5 | 5 | `rand_engine/validators/advanced_validator.py`, `rand_engine/validators/common_validator.py`, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py` |
| Job 7 | Job 4, Job 6 | 6 | `rand_engine/main/data_generator.py`, `tests/test_1_advanced_validator.py`, `tests/test_2_data_generator.py`, `tests/test_8_consistency.py` |
| Job 8 | Job 7 | 7 | `CHANGELOG.md`, `pyproject.toml`, `tests/integrations/test_public_api.py` |
| Reconciliation | Job 8 | 8 | `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/spec/rand-spec-grammar.md`, `specs/memory/product/generation/data-generator.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/onboarding/documentation.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json`, `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md` |

### Schedule and sizing

- 30 tasks: Job 1 four (3 sr, 1 jr), Job 2 six (2 sr, 4 jr), Job 3 five (4 sr, 1 jr), Job 4 two (2 sr), Job 5 four (4 sr), Job 6 two (2 sr), Job 7 four (4 sr), Job 8 three (3 jr). By `who`: 21 sr, 9 jr. Each behaviour is a RED task then an implementation task, each its own `wt-task-<kkk>`; the new-behaviour implementations are sr (design in the task), jr only where the AC and `W:` state the outcome.
- Concurrency: tasks of one job with disjoint `W:` run together; the peak is 4 task trees (Job 1; Job 2's first four tasks). Wave 4 runs Jobs 4 and 5 together (peak 3). Every RED to implementation pair and every same-file pair is an edge written in the job file.
- Net lines: `rand_engine/` deletes (two printers, the cache, `_resolved_size`, the Spark unset check, the starter markers) against adds (the rules, the net, the helper, `resolve_size`); the product side is net positive by the rules the net cannot see, and each implementation task states its net lines. `evals/` (about 400 new lines outside the package and the tests) is new by demand.
- Test rulings reserved: D5 and R11 (J2.T5), R2 (J7.T2), each in a `test(…)` commit naming it. Every other assert stays; a fixture a new rule refuses is a finding for the main thread.
- Spark tests run with the environment the dispatch brief names; no tracked file holds those paths.
- Fix commits of an Origin bug carry the lineage block (`caused_by:`, `evidence:`, `prior diffs read:`, `rebuild:`); the date unit is a REBUILD under `refactor(bugs)`.

### Barrier B1 and ledger steps (the main thread, no repo task)

- P0, before Job 1 opens: the main thread runs `dadaia doctor --fix --specs-dir <wt-rc>/specs` as a `wt-backlog-<slug>` lane on the operator's order (shape 8), then `WT sync <wt-rc path>`; if the operator rules otherwise, memory's one file rides the Reconciliation and the five others stay warnings.
- B1, after Job 1 merges and before Job 2 opens: the main thread runs `evals/run.py` k=3 on the three tasks against `rand-engine==0.8.1` from PyPI with the operator's `claude` auth, `--out` outside the repo, and reports passes out of 3 per task, tokens and cost in `.dadaia/reports/rand-engine/` (AC8.5). It installs from PyPI and reads no 0.8.2 code, so the main thread may overlap it with Job 2 on its own ruling. A round on the 0.8.2 build runs before promote.
- L1 after Job 3: `bugs.py resolve date-bound-parse-diverges-numpy-spark --caused-by 0.7.0-rc2/J4.T2` on `wt-main` (shape 4).
- L2 after Job 5: resolve `distincts-prop-negative-weight-drops-value` and `correlated-cols-overwrite-existing-column`, each naming its fix commit.
- L3 after Job 7: resolve `validated-specs-fail-in-generation` and `anomaly-values-dtype-validates-then-raises`, naming the net and the Job 3 and Job 5 rule commits; the "one source of the method rules" clause of the first record is the 0.9.0 catalog's.
- After the push of the work branch, Dependabot alerts 19 and 20 read `fixed` (`dependabot_check`).

## Measured cost

- Gate law: no task adds a step to `verify:`, `verify-task` or the merge. A task's merge runs the repo `verify:` line (poetry install, ruff `D` on six files, `pytest tests/`); the last measured pytest is 55.74-66.58 s per run. The rc runs it 39 times (30 task merges, 8 job merges, the `wt-rc` merge): 2,174-2,597 s, 36.2-43.3 min of pytest at the measured range, install and ruff unmeasured. That is one run of the job gate per merge, the law's own count.
- Product cost (AC1.5), measured at `ac30edb` on this host, 20 bundled no-argument specs (10 Common, 10 Advanced), medians of per-spec medians, from the as-is handoff: static validation `AdvancedValidator.validate` 0.026 ms median, 0.050 ms maximum; the 1-row net 0.539 ms median, 0.904 ms maximum (`Adv.healthcare`), 4.98 ms worst single run; `DataGenerator(spec)` construction today 0.055 ms median, 0.082 ms maximum. Per construction: static plus net about 0.57 ms (sum of medians), about 10 times today's construction; per callable evaluation after the first: static validation alone, 0.026 ms median, 0.050 ms maximum. The net costs what generation costs for a pool-expanding method: `distincts_prop` weights of 2x10^4 take 6.7 ms, 2x10^6 take 290 ms, 2x10^7 take 3.1 s, once per `DataGenerator` (D3). The figures are host-bound (the grill read 0.89 ms on the same ten specs), so no test asserts a time; J7.T4 re-measures on the final code and quotes it in its commit body.
- The eval: 3 tasks x 3 trials is 9 headless agent runs per round, outside `verify:`, CI and every merge; its tokens, cost and duration are unmeasured until B1 records them per trial (AC8.2). The J1.T2 smoke run is one trial.

## Acceptance map

| AC | owner task | implementation task |
|---|---|---|
| AC1.1 | J7.T1, J7.T2 | J7.T4 |
| AC1.2 | J7.T3 | J7.T4 |
| AC1.3 | J7.T4 | — |
| AC1.4 | J7.T1 | J7.T4 |
| AC1.5 | J7.T4 (and Measured cost) | — |
| AC1.6 | ledger step L3 | — |
| AC2.1, AC2.3 | J5.T1 | J5.T2 |
| AC2.2, AC2.4 | J5.T3 | J5.T4 |
| AC2.5 | J4.T1 | J4.T2 |
| AC2.6 | ledger step L2 | — |
| AC3.1, AC3.2 | J6.T1 | J6.T2 |
| AC4.1 | J3.T1 | J3.T3 |
| AC4.2 | J3.T2 | J3.T4 |
| AC4.3 | J3.T5 | — |
| AC4.4 | ledger step L1, the REBUILD commit subjects of J3.T3 and J3.T4 | — |
| AC7.1 | J2.T5 | J2.T6 |
| AC7.2 | J2.T3 | J2.T4 |
| AC7.3 | J2.T4 | — |
| AC7.4 | J2.T2 | — |
| AC7.5 | J2.T1 | — |
| AC7.6 | J1.T4 | — |
| AC8.1, AC8.3 | J1.T1 | — |
| AC8.2 | J1.T2 | — |
| AC8.4 | J1.T3 | — |
| AC8.5 | barrier B1 (no repo path to write) | — |
| AC9.1 | J8.T1 | J8.T2 |
| AC9.2 | J8.T3 | — |
| AC9.3 | Reconciliation | — |

### Reconciliation (the rc's last commits, `RC-FLOW.md` step 4)

Memory cannot sit in a job file. Order, `dd-product-engineer`: (1) the closure memory pass of `MEMORY-UPDATE.md`: AC9.3's atoms, `ARCHITECTURE.md` `## Structure` naming `evals/`, `QUALITY.md` `## Test architecture` stating the eval runs on demand outside pytest and CI, `index.md`, `catalog.json`; (2) re-stamp the `derived-from` hashes at `docs/1_DATA_GENERATOR.md:21,36` and `docs/5_RECIPES.md:7,8,39,100,131,151`, `git grep -n derived-from docs` before and after (shape 9); (3) `release.py phase CLOSURE`, then rc-2's `release.py new`. The Origin names bugs only, so no backlog entry exits.
