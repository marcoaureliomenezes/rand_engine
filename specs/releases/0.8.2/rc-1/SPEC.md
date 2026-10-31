# SPEC — Release: 0.8.2, candidate 1 (a spec that validates generates; measured public claims; agent eval baseline)

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-10-31
**Origin:** bugs:validated-specs-fail-in-generation,distincts-prop-negative-weight-drops-value,correlated-cols-overwrite-existing-column,anomaly-values-dtype-validates-then-raises,date-bound-parse-diverges-numpy-spark

- Sources: grill `.dadaia/handoff/rand-engine/2026-10-31T155739Z-main-grill-randspec-contract` (summary "Confirmo tudo (Recomendado)"); as-is review `2026-10-31T160733Z-dd-sw-engineer-sr-asis-0.8.2-rc1`; the main thread's rulings D1–D5 on its decisions.
- Version ruling, operator verbatim: "0.8.2 → 0.9.0 → 1.0 (Recomendado)". 0.8.2 carries bug fixes, docs and discovery only. Every grammar, seed, error-format or default change belongs to 0.9.0.
- Discovery scope (grill, external acts): README/PyPI top, `project_urls` with `llms.txt` and the skill, keywords, `context7.json`, sitemap, `llms.txt` in the wheel. Slogan "Norte interno, público só o medido (Recomendado)". Spark: "Manter como o ADR 0003 (Recomendado)". Eval: "evals/ no repo, sob demanda (Recomendado)".
- Invariant 12: no `gen_*` body and not `StreamHandler` change; the grill's by-name approvals (`gen_distincts_prop`, `StreamHandler`, `gen_dates`) belong to 0.9.0.

## Bug window review

Prior candidate: 0.8.1 rc-2 (archived). `BUGS.jsonl` holds 3 resolved records and this Origin's 5 open ones. Each fix was found by its id line and read with `git show`; the lineage is the reviewers' (verdicts 2026-10-31T161722Z, 162638Z, 163328Z).

| bug | fix | pattern hit | verdict | why |
|---|---|---|---|---|
| `spark-pre-1970-negative-assert-flaky` | `224f8b2` (resolved `f5a0035`) | an assert's fixture changed (10 → 100 rows); every assert kept | KEEP | the random miss falls from 2^-10 to 2^-100; no child bug |
| `writestream-bare-name-targets-filesystem-root` | `aa6f0b0` (RED `e6af657`, resolved `ac30edb`) | symptom patch: `handle_path` gained `or "."`, the stream kept its own f-string join (two deciders) | REBUILD, done | a child bug (`caused_by` this id) followed on the same join; `85e819d`, `bb6afc9` rebuilt the unit |
| `writestream-drive-relative-targets-drive-root` (CRITICAL, data loss) | `85e819d`, `bb6afc9` (RED `e9525c7`, `ba82e34`; asserts `fca7685`, `1a1558f`; resolved `a5df708`) | none: one decider, two re-joins deleted, `rand_engine/` net −3 | KEEP | below |

- Lineage: `85e819d` made `handle_path` return the joined stem both writers consume, deleting both re-joins. Review 161722Z refused the leftover part-file string join (`_writer_stream.py:60`); `bb6afc9` uses the overwrite loop's `os.path.join` and deletes the dead `or "."`. Review 162638Z refused drive tests pinning posix-host names; `1a1558f` asserts by `glob` over `ntpath.join`, red with the old join. The chain ends in a deletion, not a layer.
- The `bare-name` record's immutable lineage is wrong: "Present since 828cd86" is a rename; the join dates from `7c707a5` (2025-10-12), the overwrite loop from `543017c` (2025-10-23).
- Its `expected` says overwrite removes only the stream's files; the documented contract clears the target. Per-file ownership enters through intake only.

## 1. Problem

- Invariant 3 ("A spec that validates generates") is broken. Of 36 wrong specs probed on 0.8.1, 25 are refused at construction, 6 validate then fail in generation, 2 generate wrong data silently.
  - The six: a bad date format, start after end, an invalid unix date, all-zero `distincts_prop` weights, a mixed-type `distincts` pool, a multi-character `complex_distincts` replacement.
  - The two silent ones: a negative `distincts_prop` weight drops its value; a `cols` name that repeats an existing column overwrites it.
- Siblings (as-is review): a negative `distincts_map_prop` weight drops its value; `cols: ['a', 'a']` yields one column; `anomaly_values` that cannot keep the column dtype validate, then `get_df` raises (the check runs in the modifier step).
- A date bound that does not parse under `date_format` generates on NumPy, where `_parse_date_bound` (`_np_core.py:16`) silently falls back to `%Y-%m-%d`, and raises on Spark, whose core runs a plain `strptime` (`_spark_core.py:92`). Both validators accept it. Two parse deciders; the fallback is undocumented.
- The class repeats: 19 of 64 ledger bugs. Its structural cause is the validators (1,260 lines) copying by hand what the NumPy core (535 lines) accepts; its REBUILD is the 0.9.0 catalog. In the grill, one trial row caught 5 of 5 late failures.
- A callable spec is validated once, at construction; each later evaluation (`data_generator.py:74`) generates unvalidated.
- Size has two deciders: `size(-5)`, `size(2.5)`, `size('3')` and `size(True)` fail in generation as raw NumPy errors, while `write.save` checks its own rule (`_writer_batch.py:55`).
- A typo gets the full list, no suggestion: `'integerz'` lists 21 methods.
- Public texts claim unmeasured speed ("very fast", "Fast", "at NumPy speed"; the AC5.1 sites). "Fastest" is unproven: dbldatagen is 2.6× faster on Spark at 1M rows. The measured fact is 4.8× Faker on the 100,000-dict workload (CI run 39153239357, medians 0.159 s vs 0.769 s).
- Discovery gaps: `project_urls` lack `llms.txt` and the Agent skill; no `llms.txt` in the wheel; no `context7.json`; no per-page docs description; the keywords miss 3 of 14 GitHub topics.
- Hygiene:
  - The `test-data` starter, a plain pytest helper, carries Databricks notebook markers.
  - The exception docstrings are Portuguese, with examples of dead APIs (`Core.gen_ints`).
  - `cache(partial(...))` at `data_generator.py:88` hits 9 of 10 batches only when a column is Arrow-null; the uncached call costs 0.019 ms.
  - `validate_with_warnings` (`advanced_validator.py:430`) and `validate_spark_with_warnings` (`common_validator.py:250`) have no caller.
  - Two open low Dependabot alerts, GHSA-xmj3-9gf7-h52w on setuptools 83.0.0 (`poetry.lock`, `benchmarks/comparison-requirements.txt`); the fix is 84.1.0.
- Nothing measures whether an agent finds rand-engine, uses it, or fixes a spec from its error.

## 2. Measurable goals

- No spec `DataGenerator` accepts fails in generation for a reason the spec states: every shape above is refused at construction with `SpecValidationError` naming the column.
- One decider per question: date-bound parsing, size, output-name uniqueness.
- Seeded output is unchanged: the golden SHA-256 literals stay.
- Each typo of a method name, kwarg or column key with a close match gets one "did you mean" suggestion.
- Every public text states only measured facts, and the one speed figure cites its run.
- The eval baseline on PyPI 0.8.1 exists (passes out of 3 per task, measured tokens and cost).

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the eval harness and its 0.8.1 baseline (the grill's first job); the setuptools bump | FR8, FR7 (AC7.6) |
| 2 — shared foundation | the static rules, the date-bound decider, the size decider, did-you-mean, the one-row net | FR2, FR4, FR3, FR1 |
| 3 — features and bugs | dead code, exception docstrings, the starter | FR7 |
| 4 — promote-facing | measured claims, doc drift, discovery metadata, version, CHANGELOG, closure memory | FR5, FR6, FR9 |

## 3. Non-goals

- Everything ruled for 0.9.0: the catalog REBUILD of `rand_engine/validators/`, the conformance corpus, structured errors, the renames, removing `FileWriterError`, ADR 0004 and 0005, TypedDict `RandSpec`, the JSON Schema, the gaps (fractional weights, native dates, nullable fk, decimal).
- Any change to `SpecValidationError`'s type, banner or footer.
- A net for `SparkGenerator` (a Spark job per construction; ADR 0003). Spark gets the static rules only.
- Any `gen_*` body or `StreamHandler` change, and any new runtime dependency (`difflib` is stdlib).
- Per-file overwrite ownership for streams; Databricks markers in the other starters.
- The Context7 registration, the operator's act ("Cadastro no Context7 (Recomendado)").
- Running the eval in CI or as any gate.

## 4. Requirements

### FR1 — A spec that validates generates: the one-row net (`validated-specs-fail-in-generation`, HIGH; `anomaly-values-dtype-validates-then-raises`, MEDIUM)

- D3, main-thread ruling, within the version ruling: a dict spec gets the net once, at construction. A callable spec gets static validation at every evaluation and the net only at construction. The as-is review measured the net at 0.539 ms median; per evaluation it would add about 65% to `get_df(1000)`.
- D4, main-thread ruling, within the version ruling: the net runs the library pipeline (first level and modifiers) on a separate generator, never user transformers.

- AC1.1 (integration, `tests/test_2_data_generator.py`): each of the six repro specs of `validated-specs-fail-in-generation`, and the repro of `anomaly-values-dtype-validates-then-raises`, raises `SpecValidationError` at `DataGenerator(spec, seed=1)`, naming the column.
- AC1.2 (unit, `tests/test_1_advanced_validator.py`): after static validation, `DataGenerator` generates one row of every column through its method and modifiers, on a generator the instance's seed and key seed never feed. No transformer runs: a counting transformer, embedded or global, reads 0 after construction. A net refusal names the column, the method and the engine's error type and text.
- AC1.3 (integration, existing tests): `test_golden_seeded_output` and the seeded pk/fk tests pass with their literals unchanged. The bundled `RandSpecs` and `AdvancedRandSpecs` all construct.
- AC1.4 (integration, `tests/test_2_data_generator.py`): a callable returning a valid spec, then one of the six, raises `SpecValidationError` at the `get_df`, `write` or `stream_dict` call that evaluates it, before any row.
- AC1.5 (no test; a measurement): the PLAN states the cost of static validation and of the net, per construction and per callable evaluation, as median and maximum over the bundled specs, measured on its host. No test asserts a time.
- AC1.6 (no test; ledger verbs): both bugs resolve naming the net and the FR2/FR4 rules. The record's "one source of the method rules" clause is the 0.9.0 catalog's ("Catálogo declarativo + rede (Recomendado)").

### FR2 — Static rules, swept by class

The rules sit in the catalog's `semantic` slot (`method_specs.py`) and `AdvancedValidator.validate`, the last hand rules before the 0.9.0 catalog. Callables rely on them (D3): each of the six shapes has one (dates: FR4).

- AC2.1 (unit, `tests/test_1_advanced_validator.py`; `distincts-prop-negative-weight-drops-value`): a negative weight is refused naming the column and the value in every `*_prop` method, `distincts_prop` and `distincts_map_prop`; so is an all-zero weight set. `{'a': -1, 'b': 2}` names `'a'` and `-1`.
- AC2.2 (unit, same file; `correlated-cols-overwrite-existing-column`): a spec that produces one output name twice is refused, within one `cols` (`['a', 'a']`) and across columns (a top-level key repeated in another column's `cols`). The message names the name and both definitions; the record's repro names `'a'`, `'a'` and `'m'`.
- AC2.3 (unit, same file): a `distincts` pool whose values are not all one Python type is refused naming the column and the types found: `['a', 1]`, `[1, 2.5]`, `['a', None]`. The rule is the engine's own precondition (`type(x)` identity, `_np_core.py:220`).
- AC2.4 (unit, same file): a `complex_distincts` replacement longer than one character is refused naming the column.
- AC2.5 (unit, `tests/test_2_data_generator.py`): one size decider, `DataGenerator._resolve_size`, consulted by `get_df`, `stream_dict` and both writers, accepts a non-negative `int` and refuses `-5`, `2.5`, `'3'`, `True` with `RandEngineError` naming the value, at `size` or, for a callable size, before its batch. `size(0)` gives an empty frame. `_writer_batch._resolved_size` (`:55`) is deleted.
- AC2.6 (no test; ledger verbs): both MEDIUM bugs resolve naming their fix commits.

### FR3 — Did-you-mean in validation messages

Grill, errors: "você quis dizer"; in 0.8.2, one more text line.

- AC3.1 (unit, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`): an unknown method name, an unknown kwarg of a known method, or an unknown column key gets one added line, `Did you mean '<name>'?`. `<name>` is the closest candidate by `difflib.get_close_matches` at its default cutoff, on `DataGenerator` and `SparkGenerator` alike: `'integerz'` → `'integers'`, `'mni'` → `'min'`, `'null_rat'` → `'null_rate'`.
- AC3.2 (unit, same files): a name with no close match gets no suggestion line. Every existing message line stays, with the same type, banner and footer.

### FR4 — One date-bound decider (`date-bound-parse-diverges-numpy-spark`, MEDIUM)

D2, main-thread ruling, within the version ruling: `_parse_date_bound` is the one bound-parse decider. The validator consults it, and the Spark dispatch layer hands the Spark core bounds normalized through it. No `gen_*` body changes (invariant 12).

- AC4.1 (unit, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`): a `dates` or `unix_timestamps` bound that `_parse_date_bound` cannot parse, or a start after its end, is refused naming the column and the bound, on `DataGenerator` and `SparkGenerator` alike. No validator parses a date by any other path.
- AC4.2 (integration, `tests/test_3_spark_generator.py`): the record's repro (`start='2020-01-01'`, `date_format='%d/%m/%Y'`) generates on `SparkGenerator`, within the same bounds as `DataGenerator`. `git diff` of the `gen_*` bodies in `rand_engine/core/` is empty.
- AC4.3 (integration, `tests/test_docs.py` runs the page): `docs/1_DATA_GENERATOR.md` states that a bound which does not parse under `date_format` is read as `%Y-%m-%d`.
- AC4.4 (no test; ledger verbs): the fix is a REBUILD, `refactor(bugs)`, with `caused_by` the feature task `0.7.0-rc2/J4.T2` (`1b116d8`).

### FR5 — Public texts state only measured facts; doc drift; SparkGenerator's purpose

Operator: "Norte interno, público só o medido (Recomendado)" and "Manter como o ADR 0003 (Recomendado)". Doc drift is lying text, so every drift item the as-is review lists is in scope.

- AC5.1 (integration, `tests/test_docs.py`): none of these matches `(?i)\bfastest\b|\bvery fast\b|\bfast\b|numpy speed`: `README.md`; the tracked `llms.txt` source; the `pyproject.toml` `description`; the `rand_engine/__init__.py` docstring; the `mkdocs.yml` `site_description`; the `description` of `skills/rand-engine/SKILL.md`. Code literals (`option("engine", "fast")`) are outside the scan.
- AC5.2 (no test; it would pin prose): the README's opening paragraph (the PyPI top) states only these grill facts: a declarative spec validated before generating; related pk/fk tables without a database; a reproducible seed; NumPy-vectorized generation; published benchmarks with their losses. Its one speed figure is "4.8× Faker", with the 100,000-dict workload and CI run 39153239357 linked to `docs/comparison.md`.
- AC5.3 (integration, `tests/test_docs.py` runs the page): `docs/2_SPARK_GENERATOR.md` opens by stating the purpose: one spec runs on a laptop with `DataGenerator` and on Databricks with `SparkGenerator`. It states that dbldatagen is faster on Spark: 0.516 s against 1.341 s at 1M rows (CI run 39153239357), linked to `docs/comparison.md`.
- AC5.4 (integration, `tests/test_docs.py` runs the pages): the as-is drift items state the 0.8.2 behaviour. `docs/errors.md:9-14` says a spec fault is a `SpecValidationError` at construction, an incompatible modifier included, and that `ColumnGenerationError` is left for engine failures no spec rule covers. `docs/1_DATA_GENERATOR.md:26` says `n` is a non-negative int. `docs/compatibility.md` states the new refusals. The Portuguese comment at `spark_generator.py:47` becomes English.
- AC5.5 (no test): `specs/constitution.md` `## Direction` stays; north star internal.

### FR6 — Discovery metadata

- AC6.1 (integration, the wheel METADATA test `tests/integrations/test_public_api.py`): `Project-URL` carries `llms.txt, https://marcoaureliomenezes.github.io/rand_engine/llms.txt`, and an `Agent skill` entry whose URL is the published skill copy. The five current URLs stay.
- AC6.2 (same test): `Keywords` include every one of the repo's 14 GitHub topics read on 2026-10-31; three are added: `data-generation`, `python`, `test-fixtures`. The classifiers add `Topic :: Software Development :: Testing :: Mocking` and `Topic :: Software Development :: Libraries :: Python Modules`.
- AC6.3 (same test): the wheel ships `llms.txt` in the `rand_engine` package, byte-equal to the site's, both copied from one tracked source.
- AC6.4 (integration, `tests/test_docs.py`): `context7.json` at the repo root parses as JSON, with `projectTitle` `rand-engine`. Its folders include `docs`; its excluded folders include `specs`, `tests`, `benchmarks` and `evals`.
- AC6.5 (integration, `tests/test_docs.py`): every page in the `mkdocs.yml` nav carries a front-matter `description` of 50–160 characters, distinct across pages.
- AC6.6 (E2E, the Docs workflow's strict build on push): the site has `sitemap.xml` listing every nav page under `site_url`, and each page's `<meta name="description">` is its own. The PLAN first measures whether the build already emits the sitemap, and adds nothing it emits. The review cites the run.

### FR7 — Hygiene: starter, exception docstrings, dead code, setuptools

- AC7.1 (integration, `tests/test_9_cli.py`): `rand-engine get-started test-data` writes a file with no `# Databricks notebook source`, `# COMMAND ----------` or `# MAGIC` line; run with plain `python`, it exits 0; the tutorial includes the same bytes. D5, main-thread ruling, within the version ruling: the marker assert at `tests/test_9_cli.py:171-172` narrows to the `databricks` slug in a `test(...)` commit naming D5 and the operator's summary ("Confirmo tudo (Recomendado)"), which covered the marker-free starter.
- AC7.2 (unit, the existing docstring check in pytest): the module and class docstrings of `rand_engine/validators/exceptions.py` are English, numpy style. Each states its class's contract, and every example runs as a doctest or is removed.
- AC7.3 (integration, existing tests): D1, main-thread ruling, within the version ruling: `FileWriterError` is not deleted: deleting it breaks an import, which the version ruling excludes, and its consumers (`docs/errors.md:15,61`, `public-api.md:36`, `tests/test_docs.py:795`) stay unchanged. It leaves with the structured errors in 0.9.0.
- AC7.4 (integration, existing tests): `cache(partial(...))` at `data_generator.py:88` becomes the plain partial, an unused `cache` import going; the empty-schema and writer tests pass unchanged. The DELETE stands on cost, 0.019 ms per uncached call.
- AC7.5 (no test; a grep is the check): `validate_with_warnings` and `validate_spark_with_warnings` are deleted; a grep of the repo for `with_warnings` returns 0 hits outside `CHANGELOG.md`.
- AC7.6 (no test; the lock is the check): the test group pins `setuptools >= 84.1.0`, `poetry lock` resolves it, `poetry check --lock` passes; `benchmarks/comparison-requirements.txt` pins `setuptools==84.1.0` or later; after the push, Dependabot alerts 19 and 20 read `fixed` (`dependabot_check`).

### FR8 — Agent eval harness and its 0.8.1 baseline

Operator: "evals/ no repo, sob demanda (Recomendado)". E1: an agent finds rand-engine cold. E2: given the name, it generates correct related tables. E3: it fixes a wrong spec from the error alone.

- AC8.1 (no test; a tree): `evals/tasks/{e1-cold-discovery,e2-named-related-tables,e3-fix-by-error}/` follow `repos/dadaia-workspace/evals/tasks/*`: `instruction.md`, `task.toml` (`schema_version`, `[metadata] description`, `[verifier]` and `[agent] timeout_sec`), `tests/` with the deterministic check.
- AC8.2 (no test; the baseline run exercises it): `evals/run.py` (stdlib) runs each task k=3 times by default, each trial in a fresh temporary directory and virtual environment holding the rand-engine under test (`--rand-engine <requirement or wheel>`).
  - The agent is headless `claude -p` with none of the host's `CLAUDE.md`, settings, skills, plugins, hooks or MCP servers; the trial's init event lists none. One pinned model id, recorded in every result.
  - Results go only to a caller-named `--out`, one JSON per trial: task, trial, passed, input and output tokens, cost, duration. No credential is printed or persisted.
- AC8.3 (no test; the checks are the tests): E1 records whether the agent installed or imported `rand-engine`, never a pass target. E2 passes when the parent and child tables have the requested row counts and every fk value is in the parent pk set. E3 passes when the fixed spec generates the requested rows and columns.
- AC8.4 (integration, `tests/test_docs.py` or the wheel test): no file under `.github/workflows/` names `evals/`; `pytest --collect-only -q` at the repo root collects no `evals/` path; the built wheel lists no `evals/` entry; the `verify:` line is unchanged.
- AC8.5 (E2E, manual, on demand): one baseline round on `rand-engine==0.8.1` from PyPI, reported in `.dadaia/reports/rand-engine/` with passes out of 3 per task and the round's measured tokens and cost. The closure summary quotes it; a round on the 0.8.2 build runs before promote.

### FR9 — Version, changelog and closure memory

- AC9.1 (no test; the literal mirrors `pyproject.toml`): the version is `0.8.2`, and the built-wheel literal in `tests/integrations/test_public_api.py` follows.
- AC9.2 (integration, `tests/test_docs.py` dates numeric headers): `CHANGELOG.md` `## [0.8.2]` has three groups:
  - **Fixed**: the five Origin bugs, and the Windows drive-relative stream target that landed on the work branch;
  - **Changed**: did-you-mean lines, size refused early, the newly refused specs, the measured public texts, `llms.txt` in the wheel;
  - **Removed**: `validate_with_warnings`, `validate_spark_with_warnings`.
- AC9.3 (closure memory pass, `pe`): the atoms `rand-spec-grammar`, `data-generator`, `writers-and-streaming`, `documentation` and `public-api` state FR1–FR7 as they leave them; `ARCHITECTURE.md` `## Structure` names `evals/` and the `llms.txt` package resource; `QUALITY.md` `## Test architecture` states that the eval runs on demand, outside pytest and CI.

### Test changes the rulings carry

- D5 narrows `tests/test_9_cli.py:171-172` (AC7.1); every other assert is kept, nothing skipped. A fixture that now fails a rule is a finding for the main thread, never a silent edit.

## Replaces

- `DataGenerator.__validate_spec`: static validation becomes static validation plus the net; a callable's later evaluations become statically validated.
- Spark's own bound parse decides nothing: it receives bounds normalized by `_parse_date_bound`.
- Deleted: `_writer_batch._resolved_size`, the two `*_with_warnings` printers, the `cache` wrapper at `data_generator.py:88`, the Portuguese exception docstrings.
- AC5.1's speed adjectives become measured facts; the root `llms.txt` becomes one source shipped in the wheel and on the site; the `test-data` starter loses its Databricks markers; setuptools 83.0.0 becomes 84.1.0 or later.

## 5. Constraints and risks

| risk | control |
|---|---|
| The net's cost (0.539 ms median; 3.1 s for `distincts_prop` weights of 2×10^7) | once per `DataGenerator` (D3); AC1.5 measures it; no test asserts a time |
| The trial shifts seeded values | its own generator (AC1.2); AC1.3's goldens |
| A spec 0.8.1 accepted is refused | each failed or lost data on 0.8.1; the CHANGELOG states it |
| FR2 adds hand rules the 0.9.0 catalog REBUILDs | ruled ("Catálogo declarativo + rede (Recomendado)"); they become catalog data |
| FR1–FR4 share `rand_engine/validators/`; FR5–FR7 share `tests/test_docs.py` | the PLAN orders or edges those jobs |
| Renamed public text, deleted `*_with_warnings` names, `llms.txt` moving into the package | a read-only `dd-researcher` pre-mortem on the consumer list precedes SPEC approval; the PLAN answers each hit |
| `claude -p` needs the operator's auth | read from the operator's environment, never printed, copied or persisted |

- At promote the operator approves the PyPI publish in the GitHub environment `production` (invariant 13).

## 6. Open questions

- None. Doc drift is in scope (FR5 AC5.4); D1–D5 answer the as-is review's decisions.
