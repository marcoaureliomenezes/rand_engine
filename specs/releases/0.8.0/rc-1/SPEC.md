# SPEC — Release: 0.8.0, candidate 1 (adoption: docs, CLI, agent surface, 0.7.0 leftovers)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-14
**Origin:** backlog:docstrings,readme-landing,docs-site,get-started-cli,agent-skill; bugs:changelog-070-header-says-unreleased,dependabot-pyspark-357-ghsa-9437,dependabot-setuptools-781-ghsa-h35f,faker-extra-undocumented-unpinned-install,spark-integers-width-2pow53-validates-then-raises,workflow-actions-mutable-refs,workflow-missing-top-level-permissions,workflow-summary-text-stale

- Demand: make the published 0.7.0 adoptable — public-surface docstrings, a landing README, a docs site with `llms.txt`, a five-case get-started CLI and an Agent Skill — and close the eight open bugs, including the carried Spark width bug.
- Sources: grill handoff `2026-10-14T132004Z-main-thread-adoption-grill` (8 operator decisions, 6 inspection facts); backlog handoff `2026-10-14T132152Z-dd-product-engineer-adoption-backlog`; the five backlog entries above; the eight open records of `specs/bugs/BUGS.jsonl`.
- Operator decisions carried: one release 0.8.0 with everything ("Uma release 0.8.0 com tudo"); numpydoc on the public surface only; GitHub Pages + Zensical + mkdocstrings, MkDocs-Material fallback; CLI "no maximo 5 casos de uso scaffoldeados", the five adoption cases; the Databricks case teaches native `SparkGenerator` with a note; Agent Skill in the repo plus a Context7 submission by the operator; promote-review findings F2–F7 registered as bugs for this batch.
- As-is review: handoff `2026-10-14T191156Z-dd-sw-engineer-sr-asis-080-rc1` (27 units, measured gate costs); the main thread's 16 rulings on it (2026-10-14), cited below as "ruling n".
- Premise corrections (bug records are append-only, so the ACs carry the scope; ruling 14): `workflow-actions-mutable-refs` covers 6 refs, not 2, and its repro regex misses `@v4` (AC2.3); `workflow-summary-text-stale` covers only the `0.5.6` literals and `.github/workflow_info.md`, since the `__version__` hints become true with FR3 (AC8.1).

## Bug window review

The audit history is empty, so the window is the whole history. The prior candidate (0.7.0 rc-2) judged rc-1's 25 fixes; this table judges rc-2's 15 resolved records (14 fix commits), each read with `git show <fix_sha>` against the overfitting patterns. Test edits in these commits are removals of satisfied strict-xfail RED markers and the one golden AC8.3 replaced; no assert was loosened.

| bug | fix_sha | pattern hit | verdict | why |
|---|---|---|---|---|
| `float-rounded-domain-violates-bounds` | `89553c2` | ≥ 2 fixes on `float_lattice_bounds` (with `be93fd3`, `85a860f`) | KEEP | later fixes are one guard each; the helper is the one decider that validation and both cores consult; no child bug since `85a860f` |
| `distincts-map-empty-pool-validates` | `04034d1` | none (net −212) | KEEP | one intake for both validators |
| `distincts-multi-map-empty-domain-validates` | `04034d1` | none | KEEP | same rebuild |
| `probability-wrong-type-escapes-validation` | `37a612d` | none | KEEP | one typed method catalog replaced duplicated tables |
| `spark-bigint-precision-lost` | `6d35e6a` | helper stack (+378) | KEEP | the stack already left in `a884a0f`; the surviving `SparkCore.gen_ints` refusal is correct |
| `spark-floats-lattice-quadratic-slowdown` | `a884a0f` | none (net −213) | KEEP | operator bodies restored with the minimal fix |
| `unbatched-save-refuses-transformed-null-column` | `ffdb0d1` | none (net −82) | KEEP | one evaluation per final file |
| `fk-parent-args-validates` | `7c3566b` | new decider beside the engine's; net +21 | REBUILD | `_spark_width_errors` restates the Spark integer-width rule of `SparkCore.gen_ints` and diverges by one (`common_validator.py:241` `max - min > 2**53` vs `_spark_core.py:38` `max - min + 1 > 2**53`): child bug `spark-integers-width-2pow53-validates-then-raises` |
| `spark-floats-int64-endpoint-crashes` | `32c729b` | a fallback branch | KEEP | the branch is the operator's 2026-10-11 fine-grid ruling; net −7, it deleted the validator's float-grid copy |
| `floats-span-overflow-validates` | `be93fd3` | none (one line) | KEEP | span taken on exact Decimals |
| `spark-floats-int-bounds-beyond-int64-crash` | `706d036` | third fix on `SparkCore.gen_floats` | KEEP | one-line `float()` cast inside an operator-approved body; no child bug after it |
| `spark-floats-normal-int-kwargs-beyond-int64-crash` | `9a7c5b5` | none (one line) | KEEP | approved by name, same cause as the line above |
| `float-decimals-unbounded-validates` | `85a860f` | none | KEEP | one predicate `float_decimals_supported` for three callers |
| `float-round-overflows-to-inf` | `37a99e7` | a second path in `_round_finite` | KEEP | the fast path is measured in the commit body; no child bug; reworking it needs CI benchmark evidence this candidate does not carry |
| `docs-overstate-modifier-and-decimals-scope` | `06d7de5` | none | KEEP | docs corrected to the code |

- The structural problem behind the REBUILD: a validator re-deriving an engine refusal instead of consulting it. Validation rows of rc-2's own table (`validator-engine-schema-drift`, `method-registry-has-five-owners`) were rebuilt in rc-2; their surface produced `fk-parent-args-validates` and now `spark-integers-width-2pow53-validates-then-raises`. FR1 removes the second copy; Job 1 executes this verdict.

## 1. Problem

- 0.7.0 is on PyPI but hard to adopt: public methods are undocumented (`DataGenerator` 1/8, `SparkGenerator` 1/4, writers 0/5), the package has no `__version__` or `py.typed`, four package directories lack `__init__.py` so no API reference can resolve them, and the README is a reference manual whose Faker install line installs a Faker major the extra excludes.
- Docs live as GitHub-browsed Markdown; there is no site, no generated API reference, and the `llms.txt` links point at GitHub blobs.
- A new user has no scaffold for the five uses the constitution names (pipeline tests, lake, streaming, Spark, realism), and agents have no skill describing the RandSpec grammar.
- Leftovers: the CHANGELOG calls the published 0.7.0 Unreleased; four workflows run with the default token scope and six third-party action refs are mutable, two of them in the jobs holding `id-token: write`; publish summaries state `0.5.6`; two test-group packages carry open advisories; a Spark integers spec of width exactly 2^53 validates and then raises, and an existing assert encodes that bug.

## 2. Measurable goals

- Every public callable of the public surface has a numpydoc docstring whose examples run.
- `rand-engine list` and `rand-engine get-started <case>` scaffold five runnable files, each executed in the suite.
- A strict-built docs site with an API reference, five tutorials and `/llms.txt` deploys to GitHub Pages.
- The README is a landing page; all eight bugs are resolved; no new runtime dependency.

## 3. Non-goals

- The core `gen_*` bodies and `StreamHandler` (constitution invariant 12), except `SparkCore.gen_ints`'s width refusal, approved by name (§6 Open question 1).
- Spark pk/fk parity, a DB key sink, event-time fk, stream-dict via Arrow (other backlog entries).
- Outreach (awesome lists, comparison page, posts, Discussions, conda-forge): backlog after 0.8.0.
- The Context7 submission, enabling GitHub Pages and pointing the GitHub homepage at the site: operator or main-thread acts outside every AC.
- A sixth CLI case, interactive prompts, config files, `init` or other verbs; versioned docs; translations; the skill inside the wheel.
- A lazy package `__init__`: `rand-engine list` and `--help` start in about 1.8 s (the package import) and that is accepted (ruling 8).
- Per-method anchors in validation errors (ruling 5): only the `_raise` footer points at the site.
- Edits to `docs/5_RECIPES.md` (KEEP, ruling 6): its overlap with the cases is left for a later docs release.
- A reusable-workflow REBUILD of the duplicated CI jobs (ruling 10): the PyPI Trusted Publisher is bound to the workflow file names.
- Local benchmark runs and any new benchmark gate.

## 4. Requirements

### Terms and API proposals

- **Public surface (invariant 1):** this candidate adds the console script `rand-engine` and `python -m rand_engine` (stdlib `argparse`), the attribute `rand_engine.__version__` (a `str`) and the `py.typed` marker; `rand_engine.__all__` stays `DataGenerator`, `SparkGenerator`, `RandSpecs`. A new public surface makes this release a minor: `pyproject.toml` reads `0.8.0`.
- **Case:** one of exactly five scaffolds, by slug:

| slug | teaches |
|---|---|
| `test-data` | a DataFrame for pipeline tests with `null_rate` and `anomaly_rate` |
| `lake` | `pk`/`fk` related tables written to a Parquet lake |
| `kafka` | an event stream for Kafka: JSON lines to stdout by default, a producer block ready |
| `databricks` | a Spark/Databricks notebook on native `SparkGenerator`, with a note on `DataGenerator`-only features and the `spark.createDataFrame` path for small volumes |
| `faker` | Faker pools sampled at NumPy speed through `RandSpecs.faker_pool` |

- **Databricks source format:** first line `# Databricks notebook source`, cells separated by `# COMMAND ----------`; both are comments, so the file also runs with `python <file>`.
- **Docs site:** `https://marcoaureliomenezes.github.io/rand_engine/`, built by Zensical from the repo's Markdown with mkdocstrings (numpydoc); MkDocs-Material builds the same `mkdocs.yml` as fallback.

### FR1 — One Spark integer-width rule (Bug window REBUILD)

- AC1.1 (integration, Spark): `SparkGenerator` with `integers` `min=0`, `max=2**53`, `int_type='int64'` raises a collected `SpecValidationError` at construction naming the column and the width; `get_df` never raises a raw `ValueError` for a spec that validated.
- AC1.2 (integration, Spark): `max - min + 1 == 2**53` validates and `get_df` yields values within `[min, max]`.
- AC1.3 (unit): for `max - min + 1` in `2**53 - 1`, `2**53`, `2**53 + 1`, and for `int_zfilled` `length` 15 and 16, Spark validation refuses exactly the specs `SparkCore.gen_ints` refuses. One predicate states the width rule; the validator (integers, and `int_zfilled` by width `10**length`), `float_lattice_bounds` and `SparkCore.gen_ints` call it; no other width literal remains.
- AC1.4 (unit): the existing assert at `tests/test_1_common_validator.py:551-552`, which accepts `max=2**53`, moves to refuse it. This is the main thread's ruling (ruling 2, 2026-10-14) under invariant 3, "a spec that validates generates"; the `test(...)` commit that moves it cites this ruling.

### FR2 — Dev-loop security

- AC2.1 (no test — dependency pins; the CI matrix on the bumped lock is the check): `poetry.lock` pins `pyspark >= 3.5.8` and `setuptools >= 83.0.0`; the test-group constraints admit them; the matrix stays green on Python 3.10–3.12; Dependabot alerts #17 and #18 read `fixed` after the push.
- AC2.2 (no test — the repo has no YAML seam and a parser dependency is refused, ruling 9): every file in `.github/workflows/` declares top-level `permissions: contents: read`; a job widens only the scopes it uses, and `id-token: write` appears only on the publish jobs of `auto_tag_publish_master.yml` and `auto_tag_publish_development.yml` and on the Pages deploy job. The commit body quotes the bug's repro at zero hits.
- AC2.3 (no test — same reason as AC2.2): all 6 mutable third-party refs pin a full 40-hex commit SHA, the release tag in a trailing comment — `codecov/codecov-action@v4` ×3 (`pr_to_master.yml`, `pr_to_development.yml`, `auto_tag_publish_development.yml`), `pypa/gh-action-pypi-publish@release/v1` ×2 (`auto_tag_publish_master.yml`, `auto_tag_publish_development.yml`), `aquasecurity/trivy-action@master` ×1 (`pr_to_development.yml`). The commit body quotes this repro at zero hits: `git grep -nE 'uses: +[^ ]+@' .github/workflows | grep -vE 'uses: +(actions|github)/' | grep -vE '@[0-9a-f]{40}( |$)'`.

### FR3 — Public-surface docstrings and package metadata

- AC3.1 (unit): `rand_engine.__version__` comes from `importlib.metadata.version("rand-engine")`; where the distribution is not installed (`verify:` runs `poetry install --no-root`), `import rand_engine` still succeeds and `__version__` is the fixed placeholder `"0.0.0+unknown"`. `pyproject.toml` stays the one version literal.
- AC3.2 (integration): the built wheel holds `rand_engine/py.typed`, declares the `rand-engine` console script, holds no `skills/` path and no module outside `rand_engine/`, and, imported from the extracted wheel, `rand_engine.__version__` equals the `pyproject.toml` version.
- AC3.3 (unit): every public class and method of `DataGenerator`, `SparkGenerator`, the writer objects `write` and `writeStream` return, and `RandSpecs` carries a numpydoc docstring — summary, `Parameters`, `Returns`, `Raises` where it raises, `Examples`. `ruff` joins the test dependency group and the repo `AGENTS.md` `verify:` lines run `ruff check --select D` with `convention = "numpy"` on those modules (ruling 4); it exits 0.
- AC3.4 (unit): `pytest --doctest-modules` on those modules passes; each example generates at most 10^4 rows and writes only under a temporary directory; Spark examples carry `# doctest: +SKIP` (ruling 11), Spark behaviour staying proven by the suite and the `databricks` case.
- AC3.5 (no test — scope; reason: checked on the diff at review): no docstring task changes a `gen_*` body, `StreamHandler` or an internal module's behaviour.
- AC3.6 (unit): a pytest check over `inspect` of the public callables of `DataGenerator`, `SparkGenerator`, `RandSpecs` and the writer objects `write` and `writeStream` return — `save`, `start` and `trigger` included — asserts each has a numpydoc docstring with a summary, a `Parameters` section when it takes an argument besides `self`, and a `Returns` section when it returns a value. Reason (ruling 12): ruff D skips the `_`-prefixed writer modules, so AC3.3 alone cannot see them.

### FR4 — The get-started CLI

- AC4.1 (unit): `rand-engine list` prints the five slugs in the table's order, each with a one-line description, exits 0, and prints identical bytes on every run.
- AC4.2 (unit): `rand-engine get-started <slug> [--out DIR]` writes exactly `DIR/<slug>.py` (default `DIR` is the current directory, created when missing), prints its path and exits 0; a slug always yields identical file bytes.
- AC4.3 (unit): an unknown slug or a missing argument exits 2 with usage on stderr listing the five slugs; an existing target file is left unchanged and the command exits 1 naming it; the CLI never reads stdin.
- AC4.4 (unit): `rand-engine --help` and `rand-engine get-started --help` describe every argument and list the five slugs.
- AC4.5 (integration): every scaffold is in Databricks source format and each written file executes in-process in the suite in a temporary directory, writing only beneath it, at most 10^4 rows; `databricks` shares the suite's Spark session and skips where the Spark tests skip. One subprocess runs the written `test-data.py` under plain `python` and exits 0 (ruling 7).
- AC4.6 (integration): `kafka` prints JSON lines to stdout with neither a broker nor a Kafka client installed; its producer block runs only when the user enables it. `lake` reads its Parquet tables back and every `fk` value joins a `pk`. `test-data` shows nulls and anomalies in the resulting DataFrame. `faker` runs with the `rand-engine[faker]` extra.
- AC4.7 (unit): `[tool.poetry.dependencies]` is unchanged and the CLI module imports only the standard library and `rand_engine`.
- AC4.8 (no test — repo law; reason: checked on the diff at review): `tests/AGENTS.md`'s layout line names `tests/test_9_cli.py` as the CLI's test file (ruling 4).

### FR5 — The docs site

- AC5.1 (integration): the docs workflow runs the strict build, which aborts on a broken internal link, and it exits 0 on every PR to `development` and `master`; the site is built only there, never in the working tree, and `site/` and `.cache/` are gitignored (ruling 15).
- AC5.2 (integration): the site has Getting started, five Tutorials (one per case), How-to, an API reference generated from the FR3 docstrings, and Explanation.
- AC5.3 (unit): each tutorial shows the exact file `rand-engine get-started <slug>` writes, from one source, so the page and the CLI cannot diverge.
- AC5.4 (unit): every `python` block of every Markdown page under `docs/`, subfolders included, executes in order in a temporary directory; `python no-run` stays reserved to the Kafka producer.
- AC5.5 (integration): the built site serves `/llms.txt` at its root, linking site pages, and each page's Markdown source beside its HTML.
- AC5.6 (unit): the `SpecValidationError` footer built by `_raise` (`common_validator.py:275`) names the docs-site URL, and it equals `pyproject.toml` `documentation` (ruling 5).
- AC5.7 (no test — deployment; reason: verified by the first deploy run on `master`): a workflow deploys the site to GitHub Pages on push to `master`, under FR2's permission and pinning contract.
- AC5.8 (unit): `pyproject.toml` `documentation` points to the site.
- AC5.9 (integration, through AC5.1): `rand_engine/main/`, `file_handlers/`, `core/` and `utils/` each carry an `__init__.py`, so mkdocstrings and griffe resolve `rand_engine.DataGenerator` and its siblings and the API reference builds (ruling 13).
- AC5.10 (no test — comment hygiene; reason: checked on the diff at review): the docstrings at `tests/test_docs.py:22,34,45` carry no AC id (ruling 16).

### FR6 — The Agent Skill

- AC6.1 (unit): `skills/rand-engine/SKILL.md` carries Agent Skills front matter (`name: rand-engine`, `description`) and covers the RandSpec grammar, choosing a method, `pk`/`fk`, sinks and `rand-engine get-started`; its `python` blocks execute under the AC5.4 contract.
- AC6.2 (integration): the wheel holds no `skills/` path (AC3.2); the README and the site link the skill and the AC5.1 build resolves those links.

### FR7 — README landing page and release notes

- AC7.1 (unit): the README holds, in order, the pitch, live shields badges (PyPI version, Python versions, license, CI), install, a 30-second example, when to use it, the five `rand-engine get-started` cases and the docs-site link; every README `python` block executes (the existing README contract); method reference tables live on the site, not in the README.
- AC7.2 (unit): the README and every docs page install Faker as `pip install "rand-engine[faker]"`; every `pip install` names only a declared extra; no page says `pip install faker`.
- AC7.3 (unit): every `## [x.y.z]` header of `CHANGELOG.md` carries an ISO date — `## [0.7.0] - 2026-10-14` among them — and a `## [0.8.0]` section lists this release's Added and Fixed entries.

### FR8 — Truthful CI summaries

- AC8.1 (no test — ruling 9; a prose test would assert text, not behaviour): the `0.5.6` literals at `auto_tag_publish_master.yml:277`, `:335`, `:336` are gone and `.github/workflow_info.md` (a prose mirror of the YAML with 0 readers) is deleted; the commit body quotes `git grep -n '0\.5\.6' .github; git ls-files .github/workflow_info.md` at zero lines. The `rand_engine.__version__` hints are true once AC3.1 lands.

## 5. Replaces

- The Spark integer-width inequality restated in `CommonValidator._spark_width_errors` (`max - min > 2**53`, `length > 15`) and in `float_lattice_bounds` and `SparkCore.gen_ints` (`_spark_core.py:38`, `max - min + 1 > 2**53`) → one predicate (FR1).
- The assert accepting `max=2**53` (`tests/test_1_common_validator.py:551-552`) → an assert refusing it (AC1.4).
- Six mutable action refs (`@v4` ×3, `@release/v1` ×2, `@master` ×1) → commit-SHA pins (AC2.3).
- The default `GITHUB_TOKEN` scope in `auto_tag_publish_master.yml`, `auto_tag_publish_development.yml`, `pr_to_master.yml`, `test_on_push.yml` → top-level `contents: read` (AC2.2).
- `poetry.lock` pyspark 3.5.7 and setuptools 78.1.1 (`setuptools = "^78.1.1"`) → patched versions (AC2.1).
- "The package exposes no `__version__`" → `__version__` from installed metadata (AC3.1); four namespace packages → regular packages (AC5.9).
- The README as reference manual, its `derived-from` markers and its `pip install faker` line → landing page and the `rand-engine[faker]` extra (FR7).
- GitHub-browsed `docs/*.md` and the `documentation` URL to the GitHub tree → the site built from the same Markdown (FR5); the repo-root URL in the `_raise` footer → the site URL (AC5.6).
- The repo-root `llms.txt` linking GitHub blobs → one root file linking site pages, served at `/llms.txt` (AC5.5).
- `## [0.7.0] - Unreleased` → a dated header (AC7.3).
- The `0.5.6` summary literals and `.github/workflow_info.md` → removed (AC8.1).

## 6. Constraints, risks and open questions

### Wave ranking

| wave | kind | FRs |
|---|---|---|
| 1 | law, skills and dev loop | FR2; the dependency groups and ruff (AC2.1, AC3.3) |
| 2 | shared foundation | `__version__`, `py.typed`, the four `__init__.py` (AC3.1, AC3.2, AC5.9) — every later wave imports the skeleton or prints the version |
| 3 | features and bugs | FR3 docstrings, FR1 (the Bug window REBUILD), FR4, FR8 |
| 4 | promote-facing | FR5, FR6, then FR7 and the `0.8.0` version; the Reconciliation job last |

### Constraints

- Zero new runtime dependencies (invariant 10); the CLI is stdlib `argparse`.
- Invariant 11: Zensical is pinned exactly (`==`) in a `docs` dependency group with mkdocstrings-python; ruff enters the `test` group; MkDocs-Material enters only if the fallback is taken, on the same `mkdocs.yml` (ruling 15).
- Repo-law edits in scope (ruling 4): the three `verify:` lines of the repo `AGENTS.md` (AC3.3) and `tests/AGENTS.md` (AC4.8). `ARCHITECTURE.md` `## Tech Stack` and `QUALITY.md` `## Gates` ("No lint or type checker is configured") change in a `pe` task of the Reconciliation job, inside this candidate.
- Invariant 12: the core `gen_*` bodies and `StreamHandler` are out of scope, except `SparkCore.gen_ints`'s width refusal (`_spark_core.py:38`), approved by name (Open question 1).
- Measured gate costs (as-is handoff, this machine): ruff D 0.03 s; docstring and doctest checks under 1 s inside the suite; the five cases in-process 0.85 s; the one subprocess 2.38 s — about 4.3 s on a 72.2 s `verify:` run. The Zensical build (2.2 s strict) runs in the docs workflow only.
- Benchmarks run in CI only; any speed claim in the README, the site or a scaffold cites `docs/BENCHMARKS.md`.
- Invariant 7: scaffolds and examples use synthetic data only. Invariant 9: CLI and docs tests write under pytest `tmp_path`.
- Invariant 6: the Pages deploy uses the workflow token and OIDC; no new secret.
- Out of every AC, operator or main thread: the Context7 submission, enabling GitHub Pages (Actions source), and pointing the GitHub homepage at the site after the first deploy.

### Risks

| risk | mitigation |
|---|---|
| Zensical (pre-1.0) cannot build a needed feature | exact pin; MkDocs-Material builds the same `mkdocs.yml` (measured 0.91 s) |
| tutorials and CLI scaffolds drift | one source per case (AC5.3) |
| the docs footer URL and `documentation` drift | one assert compares them (AC5.6) |
| the `databricks` scaffold cannot run where Spark cannot | it skips exactly where the Spark tests skip (AC4.5) |
| a green ruff D misses the `_`-prefixed writers | the `inspect` check (AC3.6) |

### Open questions

1. Closed 2026-10-14. The operator approved by name, under invariant 12, that `SparkCore.gen_ints` (`_spark_core.py:38`) calls the single width predicate in `_np_core.py` ("Aprovo"); its literal copy is deleted (AC1.3).
