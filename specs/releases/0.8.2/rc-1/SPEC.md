# SPEC — Release: 0.8.2, candidate 1 (a spec that validates generates; agent eval baseline)

**Status:** In review
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-10-31
**Origin:** bugs:validated-specs-fail-in-generation,distincts-prop-negative-weight-drops-value,correlated-cols-overwrite-existing-column,anomaly-values-dtype-validates-then-raises,date-bound-parse-diverges-numpy-spark

- Sources: grill `.dadaia/handoff/rand-engine/2026-10-31T155739Z-main-grill-randspec-contract` (summary "Confirmo tudo (Recomendado)"); as-is review `2026-10-31T160733Z-dd-sw-engineer-sr-asis-0.8.2-rc1` and the main thread's rulings D1–D5; the `dd-researcher` consumer pre-mortem of `fb41854` and the main thread's rulings R1–R11.
- Version ruling, operator verbatim: "0.8.2 → 0.9.0 → 1.0 (Recomendado)". 0.8.2 carries bug fixes, docs and discovery; every grammar, seed, error-format or default change is 0.9.0's.
- Grill: Spark: "Manter como o ADR 0003 (Recomendado)"; "evals/ no repo, sob demanda (Recomendado)".
- Split, main-thread ruling (size law): FR5 (public texts, doc drift) and FR6 (discovery metadata), with R3, R4, R6, R8 and their Replaces rows, move to rc-2, born by `release.py new` at this candidate's CLOSURE. FR numbers stay stable.
- R12, operator ruling in IMPLEMENTATION (`.dadaia/handoff/rand-engine/2026-11-01T022537Z-main-ruling-eval-in-ci.handoff.json`): "this eval should be an CI eval, stupid"; rc-1 takes it by amendment, overriding the releases law's "never amended" for this change only: "Amend rc-1 by my order (Recommended)"; the CI credential: "Subscription OAuth token (Recommended)". FR8 and the lines it reaches follow.
- Invariant 12: no `gen_*` body and no `StreamHandler` change; the grill's by-name approvals (`gen_distincts_prop`, `StreamHandler`, `gen_dates`) are 0.9.0's.

## Bug window review

Prior candidate: 0.8.1 rc-2 (archived): 3 resolved records, plus this Origin's 5 open ones. Each fix was read with `git show`; lineage per the verdicts 2026-10-31T161722Z, 162638Z, 163328Z.

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| `spark-pre-1970-negative-assert-flaky` | `224f8b2` (resolved `f5a0035`) | a fixture grew (10 → 100 rows); every assert kept | KEEP | the random miss falls from 2^-10 to 2^-100; no child bug |
| `writestream-bare-name-targets-filesystem-root` | `aa6f0b0` (RED `e6af657`, resolved `ac30edb`) | symptom patch: `handle_path` gained `or "."`, the stream kept its own join (two deciders) | REBUILD, done | a child bug followed on the same join; `85e819d`, `bb6afc9` rebuilt the unit |
| `writestream-drive-relative-targets-drive-root` (CRITICAL) | `85e819d`, `bb6afc9` (RED `e9525c7`, `ba82e34`; asserts `fca7685`, `1a1558f`; resolved `a5df708`) | none: one decider, two re-joins deleted, `rand_engine/` net −3 | KEEP | below |

- Lineage: `85e819d` made `handle_path` return the stem both writers consume; `bb6afc9` replaced the leftover part-file join (`_writer_stream.py:60`) and deleted `or "."`; `1a1558f` asserts by `glob` over `ntpath.join`, red with the old join. The chain ends in a deletion.
- The `bare-name` record's "Present since 828cd86" is a rename; the join dates from `7c707a5`, the overwrite loop from `543017c`. Its `expected` (overwrite removes only the stream's files) contradicts the documented contract; per-file ownership enters through intake only.

## 1. Problem

- Invariant 3 ("A spec that validates generates") is broken. Of 36 wrong specs probed on 0.8.1, 25 are refused at construction, 6 validate then fail in generation, 2 generate wrong data silently.
  - The six: a bad date format, start after end, an invalid unix date, all-zero `distincts_prop` weights, a mixed-type `distincts` pool, a multi-character `complex_distincts` replacement.
  - The two silent ones: a negative `distincts_prop` weight drops its value; a `cols` name repeating an existing column overwrites it.
- Siblings: a negative `distincts_map_prop` weight drops its value; `cols: ['a', 'a']` yields one column; `anomaly_values` that cannot keep the column dtype validate, then `get_df` raises.
- An unparsable date bound generates on NumPy, where `_parse_date_bound` (`_np_core.py:16-20`) falls back to `%Y-%m-%d`, and raises on Spark (`_spark_core.py:92`). Both validators accept it.
- The class repeats: 19 of 64 ledger bugs. Cause: the validators (1,260 lines) copy by hand what the NumPy core (535 lines) accepts; its REBUILD is the 0.9.0 catalog. In the grill, one trial row caught 5 of 5 late failures.
- A callable spec is validated once; each later evaluation (`data_generator.py:74`) generates unvalidated.
- Size has three deciders: `DataGenerator` fails `size(-5)`, `size(2.5)`, `size('3')`, `size(True)` as raw NumPy errors; `write.save` has its own rule (`_writer_batch.py:55-58`); `SparkGenerator` checks only "not set" (`spark_generator.py:160-161`).
- A typo gets the full list, no suggestion: `'integerz'` lists 21 methods.
- Hygiene (FR7): Databricks markers in the `test-data` starter; Portuguese exception docstrings citing dead APIs; a `cache` that rarely hits; two uncalled `*_with_warnings` printers; Dependabot GHSA-xmj3-9gf7-h52w on setuptools 83.0.0.
- Nothing measures whether an agent finds rand-engine, uses it, or fixes a spec from its error.

## 2. Measurable goals

- No spec `DataGenerator` accepts fails in generation for a reason the spec states: every shape above is refused at construction with `SpecValidationError` naming the column.
- One decider per question: date-bound parsing, size, output-name uniqueness.
- Seeded output is unchanged: the golden SHA-256 literals stay.
- Each typo of a method name, kwarg or column key with a close match gets one "did you mean" suggestion.
- The eval baseline on PyPI 0.8.1 exists (passes out of 3 per task, measured tokens and cost).

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the eval harness and its 0.8.1 baseline (the grill's first job); the setuptools bump | FR8, FR7 (AC7.6) |
| 2 — shared foundation | the static rules, the date-bound decider, the size decider, did-you-mean, the one-row net | FR2, FR4, FR3, FR1 |
| 3 — features and bugs | dead code, exception docstrings, the starter | FR7 |
| 4 — promote-facing | version, CHANGELOG, closure memory | FR9 |

## 3. Non-goals

- Everything ruled for 0.9.0: the catalog REBUILD of `rand_engine/validators/`, the conformance corpus, structured errors, the renames, removing `FileWriterError`, ADR 0004 and 0005, TypedDict `RandSpec`, the JSON Schema, the gaps (fractional weights, native dates, nullable fk, decimal).
- Any change to `SpecValidationError`'s type, banner or footer.
- A net for `SparkGenerator` (a Spark job per construction; ADR 0003): Spark gets the static rules only.
- Any `gen_*` body or `StreamHandler` change; any new runtime dependency (`difflib` is stdlib).
- Per-file overwrite ownership for streams; Databricks markers in the other starters.
- Running the eval as any gate (a required check, the `verify:` line or a merge check); any change to the repo `verify:` line (gate law).

## 4. Requirements

### FR1 — A spec that validates generates: the one-row net (`validated-specs-fail-in-generation`, HIGH; `anomaly-values-dtype-validates-then-raises`, MEDIUM)

- D3, main-thread ruling, within the version ruling: a dict spec gets the net once, at construction; a callable spec gets static validation at every evaluation and the net only at construction. The net measured 0.539 ms median; per evaluation it would add about 65% to `get_df(1000)`.
- D4, main-thread ruling, within the version ruling: the net runs the library pipeline (first level and modifiers) on a separate generator, never user transformers.
- R2, main-thread ruling (pre-mortem): an fk `born_before` spec whose first row has no eligible parent is a spec error, caught at construction (invariant 3). Eligibility is nondecreasing in the row index (`core/_keys.py` `_eligible_parent_counts`), so row 0 is the worst row and the one-row net sees every such spec.

- AC1.1 (integration, `tests/test_2_data_generator.py`): the six repro specs of `validated-specs-fail-in-generation`, the repro of `anomaly-values-dtype-validates-then-raises`, and an fk `born_before` spec with no eligible parent at row 0 (R2) each raise `SpecValidationError` at `DataGenerator(spec, seed=1)`, naming the column.
- AC1.2 (unit, `tests/test_1_advanced_validator.py`): after static validation, `DataGenerator` generates one row of every column through its method and modifiers, on a generator the instance's seed and key seed never feed. No transformer runs: a counting transformer, embedded or global, reads 0 after construction. A net refusal names the column, the method and the engine's error type and text.
- AC1.3 (integration, existing tests): `test_golden_seeded_output` and the seeded pk/fk tests pass with their literals unchanged; the bundled `RandSpecs` and `AdvancedRandSpecs` all construct.
- AC1.4 (integration, `tests/test_2_data_generator.py`): a callable returning a valid spec, then one of the six, raises `SpecValidationError` at the `get_df`, `write` or `stream_dict` call that evaluates it, before any row.
- AC1.5 (no test; a measurement): the PLAN states the cost of static validation and of the net, per construction and per callable evaluation, median and maximum over the bundled specs, measured on its host. No test asserts a time.
- AC1.6 (no test; ledger verbs): both bugs resolve naming the net and the FR2/FR4 rules; the record's "one source of the method rules" clause is the 0.9.0 catalog's ("Catálogo declarativo + rede (Recomendado)").

### FR2 — Static rules, swept by class

The rules sit in the catalog's `semantic` slot (`method_specs.py`) and `AdvancedValidator.validate`, the last hand rules before the 0.9.0 catalog. Callables rely on them (D3): each of the six shapes has one (dates: FR4).

- AC2.1 (unit, `tests/test_1_advanced_validator.py`; `distincts-prop-negative-weight-drops-value`): a negative weight is refused naming the column and the value in every `*_prop` method, `distincts_prop` and `distincts_map_prop`; so is an all-zero weight set. `{'a': -1, 'b': 2}` names `'a'` and `-1`.
- AC2.2 (unit, same file; `correlated-cols-overwrite-existing-column`): a spec producing one output name twice is refused, within one `cols` (`['a', 'a']`) and across columns (a top-level key repeated in another column's `cols`), naming the name and both definitions; the record's repro names `'a'`, `'a'` and `'m'`.
- AC2.3 (unit, same file): a `distincts` pool whose values are not all one Python type is refused naming the column and the types found: `['a', 1]`, `[1, 2.5]`, `['a', None]`. The rule is the engine's own precondition (`type(x)` identity, `_np_core.py:220`).
- AC2.4 (unit, same file): a `complex_distincts` replacement longer than one character is refused naming the column.
- AC2.5 (unit, `tests/test_2_data_generator.py`): R1, main-thread ruling (pre-mortem): one size decider at resolution, `DataGenerator._resolve_size` (`data_generator.py:187-190`), consulted by `get_df`, `stream_dict`, both writers and `SparkGenerator.get_df` (`spark_generator.py:111-133`, `:160-163`; not invariant-12 code). `size()` checks nothing: a callable size is known only at resolution. It accepts a `numbers.Integral` other than `bool`, `>= 0` (`np.int64` passes), and refuses `-5`, `2.5`, `'3'`, `True` with `RandEngineError` naming the value, at resolution, before any row. An unset size keeps the "No size set ... `.size(n)`" text; `size(0)` gives an empty frame. `tests/test_5_files_write_batch.py:538-551` and `tests/test_8_consistency.py:377-380` pass unchanged.
- AC2.6 (no test; ledger verbs): both MEDIUM bugs resolve naming their fix commits.

### FR3 — Did-you-mean in validation messages

Grill, errors: "você quis dizer"; in 0.8.2, one more text line.

- AC3.1 (unit, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`): an unknown method name, an unknown kwarg of a known method, or an unknown column key gets one added line, `Did you mean '<name>'?`, `<name>` the closest candidate by `difflib.get_close_matches` at its default cutoff, on `DataGenerator` and `SparkGenerator` alike: `'integerz'` → `'integers'`, `'mni'` → `'min'`, `'null_rat'` → `'null_rate'`.
- AC3.2 (unit, same files): a name with no close match gets no suggestion line. Every existing message line stays, with the same type, banner and footer.

### FR4 — One date-bound decider (`date-bound-parse-diverges-numpy-spark`, MEDIUM)

D2, main-thread ruling, within the version ruling: `_parse_date_bound` is the one bound-parse decider; no `gen_*` body changes. R9, main-thread ruling (pre-mortem): the validator calls it and catches its `ValueError` (`_np_core.py:20`), reporting bound and format; the Spark dispatch (`spark_generator.py:103-106`, `:175`) passes bounds parsed by it, re-rendered as strings in `date_format`; `SparkCore`'s `strptime` (`_spark_core.py:92`, `:98-105`) is untouched.

- AC4.1 (unit, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`): a `dates` or `unix_timestamps` bound that `_parse_date_bound` cannot parse, or a start after its end, is refused naming the column, the bound and the format, on `DataGenerator` and `SparkGenerator` alike. No validator parses a date by any other path.
- AC4.2 (integration, `tests/test_3_spark_generator.py`): the record's repro (`start='2020-01-01'`, `date_format='%d/%m/%Y'`) generates on `SparkGenerator` within the same bounds as `DataGenerator`; `git diff` of `rand_engine/core/` is empty.
- AC4.3 (integration, `tests/test_docs.py` runs the page): `docs/1_DATA_GENERATOR.md` states that a bound which does not parse under `date_format` is read as `%Y-%m-%d`.
- AC4.4 (no test; ledger verbs): the fix is a REBUILD, `refactor(bugs)`, `caused_by` the feature task `0.7.0-rc2/J4.T2` (`1b116d8`).

### FR7 — Hygiene: starter, exception docstrings, dead code, setuptools

- AC7.1 (integration, `tests/test_9_cli.py`): `rand-engine get-started test-data` writes a file with no `# Databricks notebook source`, `# COMMAND ----------` or `# MAGIC` line; run with plain `python`, it exits 0; the tutorial includes the same bytes. D5, main-thread ruling, within the version ruling: the marker assert at `tests/test_9_cli.py:171-172` narrows to the `databricks` slug, covered by the operator's "Confirmo tudo (Recomendado)". R11, main-thread ruling (pre-mortem): its test (`:161-172`) is renamed to what it asserts, in the same commit.
- AC7.2 (unit, `tests/test_docs.py`): the module and class docstrings of `rand_engine/validators/exceptions.py` are English, numpy style; each states its class's contract; every example runs as a doctest or is removed. R5, main-thread ruling (pre-mortem): the in-suite check covers the module, added to `_surface` (`:700`) and the doctest module list (`:730`).
- AC7.3 (integration, existing tests): D1, main-thread ruling, within the version ruling: `FileWriterError` stays, since deleting it breaks an import; its consumers (`docs/errors.md:15,61`, `public-api.md:36`, `tests/test_docs.py:795`) stay. It leaves with the structured errors in 0.9.0.
- AC7.4 (integration, existing tests): `cache(partial(...))` at `data_generator.py:88` (it hits 9 of 10 batches only when a column is Arrow-null) becomes the plain partial, its `cache` import going; the empty-schema and writer tests pass unchanged. The uncached call costs 0.019 ms.
- AC7.5 (no test; a grep): `validate_with_warnings` (`advanced_validator.py:430`) and `validate_spark_with_warnings` (`common_validator.py:250`) are deleted. R10, main-thread ruling (pre-mortem): a repo grep for `with_warnings`, excluding `specs/` and `CHANGELOG.md`, returns 0 hits.
- AC7.6 (no test; the lock is the check): the test group pins `setuptools >= 84.1.0`, `poetry lock` resolves it, `poetry check --lock` passes; `benchmarks/comparison-requirements.txt` pins `setuptools==84.1.0` or later; after the push, Dependabot alerts 19 and 20 read `fixed` (`dependabot_check`).

### FR8 — Agent eval harness and its 0.8.1 baseline

The eval runs in GitHub Actions, in its own non-blocking workflow (R12). E1: an agent finds rand-engine cold. E2: given the name, it generates correct related tables. E3: it fixes a wrong spec from the error alone.

- AC8.1 (no test; a tree): `evals/tasks/{e1-cold-discovery,e2-named-related-tables,e3-fix-by-error}/` follow `repos/dadaia-workspace/evals/tasks/*`: `instruction.md`, `task.toml` (`schema_version`, `[metadata] description`, `[verifier]`, `[agent] timeout_sec`), `tests/` with the deterministic check.
- AC8.2 (no test; the baseline exercises it): `evals/run.py` (stdlib) runs each task k=3 times by default, each trial in a fresh temporary directory and virtual environment holding the rand-engine under test (`--rand-engine <requirement or wheel>`). The agent is headless `claude -p` with none of the host's `CLAUDE.md`, settings, skills, plugins, hooks or MCP servers (the init event lists none), one pinned model id recorded per result. Results go only to a caller-named `--out`, one JSON per trial: task, trial, passed, input and output tokens, cost, duration. The trial agent authenticates with the repository secret `CLAUDE_CODE_OAUTH_TOKEN`, passed only through the environment and never printed, persisted or copied. A trial whose auth or isolation fails is a harness error (exit 1).
- AC8.3 (no test; the checks are the tests): E1 records whether the agent installed or imported `rand-engine`, never a pass target. E2 passes when parent and child tables have the requested row counts and every fk value is in the parent pk set. E3 passes when the fixed spec generates the requested rows and columns.
- AC8.4 (integration, `tests/test_docs.py` or the wheel test): no workflow but `.github/workflows/eval.yml` names `evals/`; `pytest --collect-only -q` at the repo root collects no `evals/` path; the built wheel lists no `evals/` entry.
- AC8.5 (E2E, the first CI run of `eval.yml`): that run is the baseline. Its PyPI round is 0.8.1, the latest release at that run; its build round is the rc-1 build. Its artifact makes the report in `.dadaia/reports/rand-engine/`, with passes out of 3 per task and measured tokens and cost; the closure summary quotes it. The 0.8.2 build round before promote is the run on the PR to `development`.
- AC8.6 (no test; integration-free, the first run exercises it): `.github/workflows/eval.yml` runs on push to `feature/**` touching `evals/**` or the workflow, on pull_request to `development`, and on workflow_dispatch with `model` and `k` inputs. Each run evaluates E1 once (cold), and E2 and E3 on the latest PyPI release and on the wheel built from the checkout, k=3. The model id is pinned (default `claude-sonnet-5-5`, overridable on dispatch), and so is the CLI version. A trial with passed=false never fails the job; a harness error does. Each trial's JSON is a run artifact, and the job summary carries a table. It is never a required check.

### FR9 — Version, changelog and closure memory

- AC9.1 (no test; the literal mirrors `pyproject.toml`): the version is `0.8.2`; the built-wheel literal in `tests/integrations/test_public_api.py` follows.
- AC9.2 (integration, `tests/test_docs.py:858-862` requires a dated header): R7, main-thread ruling (pre-mortem): `## [0.8.2] - <closure date>` is written at this candidate's closure with its entries; rc-2 adds its own under the same header and re-dates it at its closure; corrected at ship if the publish date differs. This candidate's groups:
  - **Fixed**: the five Origin bugs; the Windows drive-relative stream target that landed on the work branch;
  - **Changed**: did-you-mean lines, size refused at resolution, the newly refused specs;
  - **Removed**: `validate_with_warnings`, `validate_spark_with_warnings`.
- AC9.3 (closure memory pass, `pe`): the atoms `rand-spec-grammar`, `data-generator`, `writers-and-streaming`, `documentation` and `public-api` state FR1–FR4 and FR7 as they leave them; `ARCHITECTURE.md` `## Structure` names `evals/`; `QUALITY.md` `## Test architecture` states that the eval runs in its own non-blocking workflow, outside pytest and the gating checks. The same pass re-stamps the derived-from sha256 markers in `docs/1_DATA_GENERATOR.md:21,36` and `docs/5_RECIPES.md:7,8,39,100,131,151`.

### Test changes the rulings carry

D5+R11 and R2 each change asserts in a `test(...)` commit naming the ruling. Their lines are in Replaces. Every other assert is kept, nothing skipped; a fixture that now fails a rule is a finding for the main thread, never a silent edit.

## Replaces

- `DataGenerator.__validate_spec`: static validation becomes static validation plus the net; a callable's later evaluations become statically validated. An fk `born_before` spec with no eligible parent at row 0 moves from `RandEngineError` in generation to `SpecValidationError` at construction: `tests/test_8_consistency.py:188-197` (R2); its doc consumer `docs/4_CONSTRAINTS.md:85` (R8) is rc-2's.
- Size: `_writer_batch._resolved_size` (`:55-58`, callers `:230`, `:395`) and `SparkGenerator`'s own unset check (`spark_generator.py:160-161`) are deleted for `_resolve_size` (R1).
- Dates: validators accepting any bound string, and the Spark dispatch handing raw bounds to `SparkCore` (`spark_generator.py:103-106`, `:175`), go for `_parse_date_bound` (R9).
- Deleted: the two `*_with_warnings` printers, the `cache` wrapper at `data_generator.py:88`, the Portuguese exception docstrings.
- The `test-data` starter's Databricks markers (`tests/test_9_cli.py:161-172`, D5+R11); setuptools 83.0.0 becomes 84.1.0 or later.

## 5. Constraints and risks

| risk | control |
|---|---|
| The net's cost (0.539 ms median; 3.1 s for `distincts_prop` weights of 2×10^7) | once per `DataGenerator` (D3); AC1.5 measures it; no test asserts a time |
| The trial shifts seeded values | its own generator (AC1.2); AC1.3's goldens |
| A spec 0.8.1 accepted is refused | each failed or lost data on 0.8.1; the CHANGELOG states it |
| FR2 adds hand rules the 0.9.0 catalog REBUILDs | ruled ("Catálogo declarativo + rede (Recomendado)"); they become catalog data |
| FR1–FR4 share `rand_engine/validators/`; FR4, FR7 and FR8 share `tests/test_docs.py` | the PLAN orders or edges those jobs |
| Deleted names | Replaces lists the pre-mortem's consumers; the PLAN answers each |
| the CI eval needs the operator's subscription token | a repository secret the operator sets; the workflow passes it as env; never printed, persisted or copied |

- At promote the operator approves the PyPI publish in the GitHub environment `production` (invariant 13).

## 6. Open questions

- None. D1–D5 answer the as-is review's decisions, R1–R11 the pre-mortem's hits (R3, R4, R6, R8 with rc-2), R12 the operator's FR8 order.
