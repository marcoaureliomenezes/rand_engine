# SPEC — Release: 0.8.2, candidate 1 (a spec that validates generates; measured public claims; agent eval baseline)

**Status:** Draft
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-10-31
**Origin:** bugs:validated-specs-fail-in-generation,distincts-prop-negative-weight-drops-value,correlated-cols-overwrite-existing-column

- Source: release grill `.dadaia/handoff/rand-engine/2026-10-31T155739Z-main-grill-randspec-contract` (summary: "Confirmo tudo (Recomendado)").
- Version ruling, operator verbatim: "0.8.2 → 0.9.0 → 1.0 (Recomendado)". 0.8.2 carries bug fixes, docs and discovery only. Every grammar, seed, error-format or default change belongs to 0.9.0.
- Discovery scope, named in the grill's external-acts question and confirmed by the summary: README/PyPI top, `project_urls` with `llms.txt` and the skill, keywords, `context7.json`, sitemap, `llms.txt` in the wheel. Operator words: slogan "Norte interno, público só o medido (Recomendado)". Spark: "Manter como o ADR 0003 (Recomendado)". Eval: "evals/ no repo, sob demanda (Recomendado)".
- The fourth bug, `writestream-drive-relative-targets-drive-root` (MEDIUM), was registered in lane `wt-backlog-bug-windows-drive-path` (`bf9a053`), which has not reached this tree. It joins the Origin `bugs:` list once that lane merges and this tree syncs; FR4 is its scope.
- Invariant 12: this candidate changes no `gen_*` body and not `StreamHandler`. The by-name approvals the grill names (`gen_distincts_prop`, `StreamHandler`, `gen_dates`) belong to 0.9.0.

## Bug window review

The prior candidate is 0.8.1 rc-2 (archived). `specs/bugs/BUGS.jsonl` holds 2 resolved records, plus 3 open ones in this Origin. Each fix was found by its id line and read with `git show`.

| bug | fix | found by | pattern hit | verdict | why |
|---|---|---|---|---|---|
| `spark-pre-1970-negative-assert-flaky` | `224f8b2` (resolved `f5a0035`) | id line | an assert's fixture changed: `small_spark_df` (10 rows) → `empty_spark_df` (100 rows); every assert kept | KEEP | the random miss falls from 2^-10 to 2^-100 with the partition unchanged; no child bug followed |
| `writestream-bare-name-targets-filesystem-root` | `aa6f0b0` (RED `e6af657`, resolved `ac30edb`) | id line | none: `handle_path` returns `.` for an empty dirname, and the batch writer's own `base_path or "."` fallback is deleted (+2/−2, one decider) | KEEP | below |

- `writestream-bare-name-targets-filesystem-root` is KEEP: the reviewer APPROVED it with the bug surface reduced. The record's lineage is wrong, and its fields are immutable, so the correction lives here. The record says "Present since 828cd86", which is a rename. The `f"{base_path}/{name}"` join exists since `7c707a5` (2025-10-12), and the overwrite loop since `543017c` (2025-10-23).
- The same review found a sibling defect the fix did not reach. `FileStreamWriter.start` still joins with an f-string (`_writer_stream.py:100`), while the batch writer joins with `Path`. That makes two join deciders, and on Windows `start('C:ages')` targets the drive root. It is registered as its own bug and fixed in FR4, which deletes the second decider.
- The record's `expected` says overwrite removes only the files the stream wrote. The documented contract clears the target. Per-file ownership is not scheduled; if the operator wants it, it enters through intake.

## 1. Problem

- Invariant 3 ("A spec that validates generates") is broken. Of 36 wrong specs probed on 0.8.1, 25 are refused at construction, 6 validate and then fail in generation with a raw engine error, and 2 generate wrong data without a word.
  - Six spec shapes validate and then fail in generation: a bad date format, start after end, an invalid unix date, all-zero `distincts_prop` weights, a mixed-type `distincts` pool, and a multi-character `complex_distincts` replacement.
  - The two that generate wrong data: a negative `distincts_prop` weight drops its value, and a `cols` name that repeats an existing column overwrites it.
- The class repeats: 19 of the 64 ledger bugs are "validates, then fails"; the validators (1,260 lines) re-implement by hand what the NumPy core (535 lines) accepts. One trial row generated after static validation caught 5 of 5 late failures tested, at 0.89 ms median and 3.74 ms max over the ten bundled specs.
- A callable spec is validated once, at construction. Each later evaluation (`_file_seam`, `data_generator.py:74`) generates from whatever it returns, unvalidated.
- `size(-5)` is accepted, then fails in generation as `ColumnGenerationError: negative dimensions are not allowed`.
- A typo gets the full method or key list but no suggestion. `'integerz'` lists 21 methods; `'null_rat'` lists 7 keys.
- On Windows, `writeStream.start('C:ages')` targets `C:/ages`, the drive root, and overwrite clears that directory.
- Public texts claim speed that was never measured: "very fast" (`README.md:3`, `llms.txt:3`), "Fast" (`mkdocs.yml:2`), "fast" (the skill description), "at NumPy speed" (`pyproject.toml:4`, `rand_engine/__init__.py:1`, `README.md:39,49`, `llms.txt:29`). The north star "fastest" is unproven: dbldatagen is 2.6× faster on Spark at 1M rows. The measured fact available is 4.8× Faker on the 100,000-dict workload (CI run 39153239357: 0.159 s against 0.769 s, medians).
- Discovery gaps:
  - `pyproject` `project_urls` name neither `llms.txt` nor the Agent skill.
  - The wheel carries no `llms.txt`.
  - There is no `context7.json`.
  - Docs pages carry no description of their own.
  - The keywords miss three of the repo's 14 GitHub topics.
- Hygiene:
  - The `test-data` starter, a plain pytest helper, carries Databricks notebook markers.
  - The exception module's docstrings are in Portuguese, with examples of APIs that no longer exist (`Core.gen_ints`, `generate_pandas_df`, `engine.write(1000)…load`).
  - `FileWriterError` is never raised.
  - `cache(partial(...))` at `data_generator.py:88` wraps a fresh zero-argument partial on each call, so it never hits.
  - Dependabot holds two open low alerts, GHSA-xmj3-9gf7-h52w on setuptools 83.0.0, in `poetry.lock` and in `benchmarks/comparison-requirements.txt`; the fix is 84.1.0.
- Nothing measures whether an agent finds rand-engine, uses it, or fixes a spec from its error.

## 2. Measurable goals

- No spec that `DataGenerator` accepts fails in generation for a reason the spec states: the six shapes and the two silent ones are refused at construction with `SpecValidationError` naming the column.
- Seeded output is unchanged: the golden SHA-256 cases pass with their literals untouched.
- Each typo of a method name, kwarg or column key with a close match gets one "did you mean" suggestion.
- Every public text states only measured facts, and the one speed figure cites its run.
- The eval baseline on PyPI 0.8.1 exists, with per-task passes out of 3 and the measured tokens and cost per round.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | the eval harness and its 0.8.1 baseline (the grill's first job); the setuptools bump | FR8, FR7 (AC7.5) |
| 2 — shared foundation | the one-row net, the static rules, did-you-mean | FR1, FR2, FR3 |
| 3 — features and bugs | the Windows stream join; dead code, exception docstrings, the starter | FR4, FR7 |
| 4 — promote-facing | measured claims, discovery metadata, version, CHANGELOG, closure memory | FR5, FR6, FR9 |

## 3. Non-goals

- Everything ruled for 0.9.0: the declarative catalog REBUILD of `rand_engine/validators/`, the conformance corpus, structured errors (`.errors`, codes, an exported `SpecValidationError`), the renames, the per-column seed (ADR 0004), the dataset spec (ADR 0005), TypedDict `RandSpec`, the JSON Schema, and the gaps (fractional weights, native dates, nullable fk, decimal).
- Any change to the `SpecValidationError` type, banner or footer. Did-you-mean is one more line inside the current per-error text.
- A one-row net for `SparkGenerator`: it would start a Spark job at construction, and its ordinary columns are unseeded (ADR 0003). Spark validation is unchanged.
- Any `gen_*` body or `StreamHandler` change, and any new runtime dependency (`difflib` is stdlib).
- Per-file overwrite ownership for streams; Databricks markers in the other starters.
- The Context7 registration, an operator act ("Cadastro no Context7 (Recomendado)") that needs the operator's login.
- Running the eval in CI or as any gate.

## 4. Requirements

### FR1 — A spec that validates generates: the one-row net (`validated-specs-fail-in-generation`, HIGH)

Grill default, confirmed: the net excludes transformers, and a callable spec is validated at every evaluation, because "transformers are user code with side effects; invariant 3 must hold for every spec that generates".

- AC1.1 (integration, `tests/test_2_data_generator.py`): each of the record's six repro specs raises `SpecValidationError` at `DataGenerator(spec, seed=1)`. Its message names the column, the method and the engine's own error type and text.
- AC1.2 (unit, `tests/test_1_advanced_validator.py`): after static validation passes, `DataGenerator` generates one row of every column through its method, on its own generator, which the instance's seeded generator and key seed never feed. No transformer, embedded or global, runs during the trial: a transformer that counts its calls reads 0 after construction.
- AC1.3 (integration, existing tests): `test_golden_seeded_output` and the seeded pk/fk tests pass with their literals unchanged. The bundled `RandSpecs` and `AdvancedRandSpecs` all construct.
- AC1.4 (integration, `tests/test_2_data_generator.py`): a zero-argument callable that returns a valid spec on its first call and one of the six on its second raises `SpecValidationError` at the `get_df`, `write` or `stream_dict` call that evaluates it, before any row is generated. A dict spec is validated once.
- AC1.5 (no test; a measurement): the PLAN measures the cost of the static validation plus the net, per construction and per callable evaluation, as the median and maximum over the ten bundled specs. The review cites it.
- AC1.6 (no test; ledger verb): `bugs.py resolve validated-specs-fail-in-generation` names the net as the structural fix. The record's "from one source of the method rules" clause is carried by the 0.9.0 catalog entry, ruled in the grill: "Catálogo declarativo + rede (Recomendado)".

### FR2 — Static rules for what the net cannot see

The net misses the two silent shapes, since they generate. The two rules below are added by hand to the current validator, the last ones before the 0.9.0 catalog.

- AC2.1 (unit, `tests/test_1_advanced_validator.py`; bug `distincts-prop-negative-weight-drops-value`): a `distincts_prop` weight below 0 is refused naming the column and the value. `{'a': -1, 'b': 2}` raises `SpecValidationError` and names `'a'` and `-1`. `gen_distincts_prop` is untouched.
- AC2.2 (unit, `tests/test_1_advanced_validator.py`; bug `correlated-cols-overwrite-existing-column`): a spec that produces one output column name twice is refused. That covers a top-level key repeated in another column's `cols`, and a name repeated across `cols`. The message names the duplicated column and both definitions; the record's repro (`'a'` + `distincts_map` `cols ['a', 'b']`) names `'a'`, `'a'` and `'m'`.
- AC2.3 (unit, `tests/test_1_advanced_validator.py`): a `distincts` pool whose values are not all one Python type is refused naming the column and the types found. Examples are `['a', 1]`, `[1, 2.5]` and `['a', None]`. The rule is the engine's own precondition (`type(x)` identity, `_np_core.py:220`); the assert stays.
- AC2.4 (unit, `tests/test_2_data_generator.py`): `size(-5)` raises `RandEngineError` naming `-5` at the `size` call. A callable size that returns a negative int raises the same error before that batch generates, and `size(0)` still gives an empty frame.
- AC2.5 (no test; ledger verbs): both MEDIUM bugs resolve naming their fix commits.

### FR3 — Did-you-mean in validation messages

Ruled in the grill under errors ("você quis dizer"); in 0.8.2 it is text only.

- AC3.1 (unit, `tests/test_1_advanced_validator.py`, `tests/test_1_common_validator.py`): an unknown method name, an unknown kwarg of a known method, or an unknown column key gets one added line, `Did you mean '<name>'?`. `<name>` is the closest candidate by `difflib.get_close_matches` at its default cutoff, on `DataGenerator` and `SparkGenerator` alike: `'integerz'` → `'integers'`, `'mni'` → `'min'`, `'null_rat'` → `'null_rate'`.
- AC3.2 (unit, same files): a name with no close match gets no suggestion line. Every existing message line stays, with the same type, banner and footer.

### FR4 — The stream writer joins its target like the batch writer (`writestream-drive-relative-targets-drive-root`, MEDIUM)

- AC4.1 (unit, `tests/test_5_files_write_stream.py`): for the same `path`, `FileStreamWriter.start` and `FileBatchWriter` resolve the target directory through one join. The f-string join at `_writer_stream.py:100` is deleted, so a grep of `rand_engine/file_handlers/` for `f"{base_path}/` returns 0 hits.
- AC4.2 (unit, same file): under Windows path rules (`ntpath`), the stream target of `'C:ages'` is `'C:ages'`, which is drive-relative, never `'C:/ages'`. A bare name, a relative path and an absolute path resolve as they do today.
- AC4.3 (E2E, CI): the Windows legs run AC4.1–AC4.2 natively and are green.

### FR5 — Public texts state only measured facts; SparkGenerator's purpose

Operator: "Norte interno, público só o medido (Recomendado)" and "Manter como o ADR 0003 (Recomendado)".

- AC5.1 (integration, `tests/test_docs.py`): none of these matches `(?i)\bfastest\b|\bvery fast\b|\bfast\b|numpy speed`:
  - `README.md`;
  - the tracked `llms.txt` source;
  - the `pyproject.toml` `description`;
  - the `rand_engine/__init__.py` docstring;
  - the `mkdocs.yml` `site_description`;
  - the `description` of `skills/rand-engine/SKILL.md`.

  Code literals such as `option("engine", "fast")` in `docs/errors.md` are outside the scan.
- AC5.2 (no test; a test would pin prose): the README's opening paragraph, which is the PyPI long description's top, states only these grill facts:
  - a declarative spec validated before generating;
  - related pk/fk tables without a database;
  - a reproducible seed;
  - NumPy-vectorized generation;
  - published benchmarks with their losses.

  Its one speed figure is "4.8× Faker", with the 100,000-dict workload and CI run 39153239357 linked to `docs/comparison.md`.
- AC5.3 (integration, `tests/test_docs.py` runs the page): `docs/2_SPARK_GENERATOR.md` opens by stating the purpose: one spec runs on a laptop with `DataGenerator` and on Databricks with `SparkGenerator`. It also states that dbldatagen is faster on Spark: 0.516 s against 1.341 s at 1M rows (CI run 39153239357), linked to `docs/comparison.md`.
- AC5.4 (no test): `specs/constitution.md` `## Direction` stays as written. The north star remains internal, per the ruling.

### FR6 — Discovery metadata

The discovery scope recorded under the Origin.

- AC6.1 (integration, the wheel METADATA test `tests/integrations/test_public_api.py`): `Project-URL` carries `llms.txt, https://marcoaureliomenezes.github.io/rand_engine/llms.txt`, and an `Agent skill` entry whose URL is the published skill copy. The five current URLs stay.
- AC6.2 (same test): `Keywords` include every one of the repo's 14 GitHub topics read on 2026-10-31. Three are added: `data-generation`, `python`, `test-fixtures`. The classifiers add `Topic :: Software Development :: Testing :: Mocking` and `Topic :: Software Development :: Libraries :: Python Modules`.
- AC6.3 (same test): the wheel ships `llms.txt` inside the `rand_engine` package. Its bytes equal the site's published `llms.txt`, because both come from one tracked source and the docs preparation copies that source. No second tracked copy exists.
- AC6.4 (integration, `tests/test_docs.py`): `context7.json` at the repo root parses as JSON, with `projectTitle` `rand-engine`. Its folders include `docs`, and its excluded folders include `specs`, `tests`, `benchmarks` and `evals`.
- AC6.5 (integration, `tests/test_docs.py`): every page in the `mkdocs.yml` nav carries a front-matter `description` of 50–160 characters, distinct across pages.
- AC6.6 (E2E, the Docs workflow's strict build on push): the built site has `sitemap.xml` listing every nav page under `site_url`, and each page's `<meta name="description">` is its own `description`. The review cites the run.

### FR7 — Hygiene: starter, exception docstrings, dead code, setuptools

- AC7.1 (integration, `tests/test_9_cli.py`): `rand-engine get-started test-data` writes a file with no `# Databricks notebook source`, `# COMMAND ----------` or `# MAGIC` line. Run with plain `python`, it exits 0. The tutorial includes the same bytes.
- AC7.2 (unit, the existing docstring check in pytest): the module and class docstrings of `rand_engine/validators/exceptions.py` are English, numpy style. Each states its class's contract, and every example runs as a doctest or is removed.
- AC7.3 (unit, `tests/test_docs.py`): `FileWriterError` is deleted, together with its `docs/errors.md` entries (`:15`, `:61`) and its row in the exception inventory test (`tests/test_docs.py:795`). A grep of the repo for `FileWriterError` returns 0 hits outside `CHANGELOG.md`.
- AC7.4 (integration, existing tests): `cache(partial(...))` at `data_generator.py:88` becomes the plain partial, and the `cache` import goes if it has no other use. The empty-schema and writer tests pass unchanged.
- AC7.5 (no test; the lock is the check):
  - the test group pins `setuptools >= 84.1.0`, `poetry lock` resolves it, and `poetry check --lock` passes;
  - `benchmarks/comparison-requirements.txt` pins `setuptools==84.1.0` or later;
  - after the push, Dependabot alerts 19 and 20 read `fixed` (`dependabot_check`).

### FR8 — Agent eval harness and its 0.8.1 baseline

Operator: "evals/ no repo, sob demanda (Recomendado)". E1 measures whether an agent finds rand-engine cold. E2: given the name, it writes a valid spec and generates correct related tables. E3: it fixes a wrong spec from the error alone.

- AC8.1 (no test; a tree): `evals/tasks/e1-cold-discovery/`, `e2-named-related-tables/` and `e3-fix-by-error/` follow the task format of `repos/dadaia-workspace/evals/tasks/*`. Each holds `instruction.md`, `task.toml` (`schema_version`, `[metadata] description`, `[verifier] timeout_sec`, `[agent] timeout_sec`) and `tests/` with the deterministic check.
- AC8.2 (no test; the baseline run exercises it): the runner `evals/run.py` (stdlib) runs each task k=3 times by default. Each trial runs in a fresh temporary directory with a fresh virtual environment holding the rand-engine under test (`--rand-engine <pip requirement or wheel>`).
  - The agent is headless `claude -p` in a clean config: none of the host's `CLAUDE.md`, settings, skills, plugins, hooks or MCP servers. The trial's init event lists no host MCP server or skill.
  - The model is one pinned id, recorded in every result.
  - Results go only to a caller-named `--out` directory, one JSON per trial: task, trial, passed, input and output tokens, cost, duration.
  - No credential is printed or persisted.
- AC8.3 (no test; the checks are the tests):
  - E1 records whether the agent installed or imported `rand-engine`; it is tracked, never a pass target.
  - E2 passes when the requested parent and child tables exist with the requested row counts, and every fk value is in the parent pk set.
  - E3 passes when the fixed spec constructs and generates the requested rows and columns.
- AC8.4 (integration, `tests/test_docs.py` or the wheel test):
  - no file under `.github/workflows/` names `evals/`;
  - `pytest --collect-only -q` at the repo root collects no `evals/` path;
  - the built wheel lists no `evals/` entry;
  - the `verify:` line is unchanged.
- AC8.5 (E2E, manual, on demand): one baseline round with `--rand-engine rand-engine==0.8.1` from PyPI. Its report goes to `.dadaia/reports/rand-engine/` and gives, per task, passes out of 3, plus the measured tokens and cost of the round. The closure summary quotes it, and a second round on the 0.8.2 build runs before 0.8.2 promotes.

### FR9 — Version, changelog and closure memory

- AC9.1 (no test; the literal mirrors `pyproject.toml`): the version is `0.8.2`, and the built-wheel literal in `tests/integrations/test_public_api.py` follows.
- AC9.2 (integration, `tests/test_docs.py` dates numeric headers): `CHANGELOG.md` `## [0.8.2]` has three groups:
  - **Fixed**: the three validation bugs and the Windows stream join;
  - **Changed**: did-you-mean lines, `size(<0)` refused early, the measured public texts, and `llms.txt` in the wheel;
  - **Removed**: `FileWriterError`.
- AC9.3 (closure memory pass, `pe`):
  - the atoms `rand-spec-grammar`, `data-generator`, `writers-and-streaming`, `documentation` and `public-api` state FR1–FR7 as they leave them;
  - `ARCHITECTURE.md` `## Structure` names `evals/` and the `llms.txt` package resource;
  - `QUALITY.md` `## Test architecture` states that the eval runs on demand, outside pytest and CI.

### Test changes the operator's rulings carry

- Under the dead-code ruling (summary, "Confirmo tudo"), the `FileWriterError` row of the exception inventory test goes with the class.
- Every other assert is kept, and nothing is skipped. A spec fixture that now fails the net or a rule is a finding for the main thread, never a silent fixture edit.

## Replaces

- `DataGenerator.__validate_spec`: static validation alone becomes static validation plus the one-row net. `_file_seam`'s unvalidated evaluation of a callable spec becomes a validated one.
- `FileStreamWriter.start`: the f-string join is replaced by the batch writer's join, one decider.
- `rand_engine/validators/exceptions.py`: `FileWriterError` and the Portuguese docstrings with dead examples are removed.
- `data_generator.py:88`: the never-hitting `cache` wrapper is removed.
- Speed adjectives and "NumPy speed" in the public texts of AC5.1 are replaced by measured facts.
- The root `llms.txt` as the only copy is replaced by one tracked source shipped in the wheel and on the site.
- The `test-data` starter's Databricks markers are removed.
- The setuptools 83.0.0 pins are replaced by 84.1.0 or later.

## 5. Constraints and risks

| risk | control |
|---|---|
| The net adds construction cost and runs per callable evaluation (per `stream_dict` microbatch when the spec is a callable) | AC1.5 measures it; the PR benchmark workflow's same-runner rows judge regressions; the grill measured 0.89 ms median |
| The net's trial could shift seeded values | it draws from its own generator (AC1.2); AC1.3's goldens prove it |
| A user spec accepted by 0.8.1 is refused by 0.8.2 (mixed pool, duplicate output column, negative weight) | each one failed or lost data on 0.8.1, so the refusal only surfaces it; the CHANGELOG states it |
| Deleting `FileWriterError` breaks an import of `rand_engine.validators.exceptions.FileWriterError` | outside the invariant 1 surface and never raised; CHANGELOG **Removed** names it |
| FR2 adds hand rules to the validator the 0.9.0 catalog REBUILDs | ruled ("Catálogo declarativo + rede (Recomendado)"); the rules become catalog data there |
| FR1–FR3 share `rand_engine/validators/`; FR5–FR7 share `tests/test_docs.py` | the PLAN orders or edges those jobs |
| Renamed public text, and `llms.txt` moving into the package | a read-only `dd-researcher` pre-mortem on the consumer list precedes SPEC approval; the PLAN answers each hit |
| `claude -p` needs the operator's auth on the host | the runner reads it from the operator's environment and never prints, copies or persists it |

- The operator acts at promote: approving the PyPI publish in the GitHub environment `production` (invariant 13). The Context7 registration is the operator's login.

## 6. Open questions

- To the main thread: the grill lists "doc drift fixes" without a list. This SPEC fixes the drift it names: the speed texts, the dead exception examples, `FileWriterError` in `docs/errors.md`, and the Spark purpose. Any further item the as-is review finds needs your ruling before it enters an AC.
- To the main thread: confirm `writestream-drive-relative-targets-drive-root` once lane `wt-backlog-bug-windows-drive-path` merges. The Origin `bugs:` list gains it after this tree syncs.
