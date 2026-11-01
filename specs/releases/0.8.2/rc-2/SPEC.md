# SPEC — Release: 0.8.2, candidate 2 (measured public texts; doc drift; discovery metadata)

**Status:** Approved
**Release ID:** 0.8.2
**Owner:** dd-product-engineer
**Opened:** 2026-11-01
**Origin:** operator-demand

- Split from rc-1 (rc-1 SPEC, Split line): "FR5 (public texts, doc drift) and FR6 (discovery metadata), with R3, R4, R6, R8 and their Replaces rows, move to rc-2". FR numbers stay. The demand is the operator's 2026-10-31 grill: "Norte interno, público só o medido (Recomendado)".
- Sources: the rc-2 grill `.dadaia/handoff/rand-engine/2026-11-01T214516Z-main-grill-0.8.2-rc2.handoff.json`, where the operator confirmed scope: "Confirm scope (Recommended)". The as-is review `2026-11-01T205713Z-dd-sw-engineer-sr-asis-0.8.2-rc2`, anchored at `9c1351e`. The `dd-researcher` consumer pre-mortem of `d0e6fc5` produced the main thread's rulings R17–R25. Every `path:line` below is a `9c1351e` anchor; the PLAN re-greps each one before its task.
- Version ruling, operator verbatim: "0.8.2 → 0.9.0 → 1.0 (Recomendado)". 0.8.2 carries bug fixes, docs and discovery; every grammar, seed, error-format or default change belongs to 0.9.0. Spark: "Manter como o ADR 0003 (Recomendado)".
- Dropped because rc-1 already satisfies them (as-is review): the `docs/1_DATA_GENERATOR.md` items (`:25` net, `:32` size, `:270` did-you-mean); R8 (`docs/4_CONSTRAINTS.md:85`); the `rand-spec-grammar.md:27` atom item; and the sitemap half of AC6.6. The live `sitemap.xml` lists the 18 nav pages (Docs run 41316724862).
- Bug `spark-pool-types-fail-or-corrupt` (HIGH; registration `c35b421` on `feature/0.8.2`) is not rc-2 scope. It is fixed in its own lane, `wt/0.8.2/wt-hotfix-spark-pool-types-fail-or-corrupt` (rework in flight), which merges into `feature/0.8.2` before rc-2's jobs start (`specs/bugs/AGENTS.md` §2). rc-2 documents the contract that fix leaves (AC5.3) and lists it in the CHANGELOG (AC10.1).

## Bug window review

Prior candidate: 0.8.2 rc-1, with 9 resolved records. rc-1's own review already judged the two `writestream-*` records. Each named fix was read with `git show --stat --patch` (`LINEAGE.md` §Read persisted facts). This review only judges; it schedules nothing.

| bug | fix chain | pattern hit | verdict | why |
|---|---|---|---|---|
| `validated-specs-fail-in-generation` (HIGH) | `30b74ab`, REBUILDs `9cdcc9d`, `4cbdd5f`; static rules `4a6c3f8`, `6d582f4`, `d3e8aa4`, REBUILD `957adbf`, `7244f63` | a new branch: the net skips modifiers on a column with embedded transformers (`data_generator.py:111`), copying the engine's own predicate (`_rand_generator.py:66`) | KEEP | operator ruling R14 ("Keep R14 (Recommended)"); no child bug after `4cbdd5f`. The residual is a documented partition that AC5.4 states. One home for the predicate belongs to the 0.9.0 catalog. |
| `anomaly-values-dtype-validates-then-raises` | the same chain (`30b74ab` → `4cbdd5f`) | the same branch | KEEP | the same chain; a column with embedded transformers keeps its dtype check at generation (`_rand_generator.py:156`) |
| `distincts-prop-negative-weight-drops-value` | `4a6c3f8`, REBUILD `449bbc8` | none; the rules sit in the catalog's semantic slot, net 0 lines | KEEP | no child bug on the weight rule |
| `correlated-cols-overwrite-existing-column` | `6d582f4`, REBUILD `cd20733` | the shape rule demanded `str` names, deleting names that 0.8.1 generated | REBUILD, done | child bug `cols-rule-refuses-non-string-names` (`caused_by` J5.T4) rebuilt the unit |
| `cols-rule-refuses-non-string-names` | REBUILDs `3f52e7f`, `e837492`, `8d4b5fa`, `8963a54` | repetition: four REBUILDs of `_duplicate_output_errors` / `_valid_cols` in one candidate; the final identity is the generator's dict key | KEEP | each REBUILD replaced the previous one; nothing stacked. As a REBUILD chain, it leaves the window after rc-2 if no child bug appears. |
| `date-bound-parse-diverges-numpy-spark` | REBUILDs `7244f63`, `b4f19c7`, `cc59dc8` (R13) | none; one decider, and the lossy re-render was deleted (net −9) | KEEP | the chain ends in a deletion |
| `validator-non-string-kwarg-raises-typeerror` | REBUILD `f6672ff` | none; two names are stringified where they are collected | KEEP | the same "non-string name" class as `cols-rule-…`, but in a separate unit; no child bug |
| `spark-mixed-type-pool-refused` (HIGH) | REBUILD `0479659` | a method-name branch (`method != "distincts"`) in `AdvancedValidator.validate`: a second home for a pool rule beside the semantic slot; net +6 | REBUILD, by its child bug's lane | an incomplete fix in the same surface. The main thread ruled that child bug `spark-pool-types-fail-or-corrupt`'s `caused_by` (this bug) stands, and the reviewer accepted it (verdict 2026-11-01T220131Z, INFO 8): the defect reproduces on 0.8.1, and `0479659` re-exposed it by lifting the whole rule off Spark instead of narrowing it. The child's hotfix lane rebuilds the Spark pool rule, and rc-3's window judges that fix. |
| `eval-token-reaches-agent-shell` | REBUILD `f29b3e8` | none; one env flag and the pinned CLI | KEEP | operator ruling "Scrub child env (Recommended)" |

## 1. Problem

- Public texts claim speed nobody measured. Fourteen lines in eleven files carry it (the R4 list less `docs/comparison.md`): "very fast", "fast", "at NumPy speed", and "Faker is slow per value". `docs/comparison.md` disclaims the comparison those figures cite (`:20-22`, `:87`; R18). The measured facts are in `docs/comparison.md:72-75`, CI run 39153239357, one run of three samples, medians:
  - rand-engine is 4.8× faster than Faker on the 100,000-dict workload (0.159 s against 0.769 s);
  - dbldatagen is faster on Spark at 1M rows (0.516 s against 1.341 s).
- Doc drift:
  - `docs/2_SPARK_GENERATOR.md:76-77` says Spark "coerces" any mixed pool. The rc-1 memory pass wrote that sentence (`59c25f1`); it states more than any test pins.
  - The page never states SparkGenerator's purpose.
  - `docs/errors.md:9-16`, `docs/compatibility.md:53-54` and the `rand_engine/validators/exceptions.py` docstrings (`:16-17`, `:37`, `:88-93`) state absolute or time-bound claims that the raise sites contradict.
  - `docs/compatibility.md:44-52` stops at 0.7 → 0.8.
  - One comment is in Portuguese (`rand_engine/main/spark_generator.py:48`).
- Discovery gaps:
  - `project_urls` lacks `llms.txt` and the Agent skill;
  - the wheel does not ship `llms.txt`;
  - there is no `context7.json`;
  - no docs page has its own description;
  - the keywords miss 3 of the repo's 14 GitHub topics.

## 2. Measurable goals

- Every public text states only measured facts. Each speed figure cites its run and its sample size.
- Each sentence about Spark pools and error classes names only cases that a contract test or a raise site decides.
- An agent or index reaches `llms.txt`, the skill and each page's description from package metadata and page front matter.

### Wave ranking

| wave | scope | FRs |
|---|---|---|
| 1 — law, skills and dev loop | none: no skill, rule, hook or gate changes; the `verify:` line and the Docs workflow stay unchanged | — |
| 2 — shared foundation | none: no validator or core file changes | — |
| 3 — features and bugs | none: `spark-pool-types-fail-or-corrupt` takes its own hotfix lane | — |
| 4 — promote-facing | measured texts, doc drift, discovery metadata, CHANGELOG, closure memory | FR5, FR6, FR10 |

## 3. Non-goals

- Every grammar, seed, error-format or default change; all of them belong to 0.9.0 (the version ruling). No exception class is renamed or removed, and `FileWriterError` stays (D1).
- Anything new for `SparkGenerator`: no net, no rule, no behaviour (ADR 0003). The Spark pool rule belongs to the bug lane.
- The fix of `spark-pool-types-fail-or-corrupt`.
- The Context7 registration. It is the operator's act ("Cadastro no Context7 (Recomendado)").
- A theme override, a template, sitemap code, a new gate, or any change to the `verify:` line or the Docs workflow.
- `evals/tasks/e1-cold-discovery/instruction.md:1`: it is the simulated user's prompt, and editing it shifts the eval baseline.
- `specs/constitution.md` `## Direction`: the north star stays internal (AC5.5).
- R19, main-thread ruling (pre-mortem): `specs/constitution.md:11,14` and `specs/memory/product/index.md:14` are out of FR5. `specs/` is internal law, not a public text, and the constitution is the operator's.
- R20, main-thread ruling (pre-mortem): `skills/rand-engine/SKILL.md:232` ("Quote no speed numbers") stays. It tells agents what to quote, and the README's one figure links its measurement.

## 4. Requirements

### FR5 — Public texts state only measured facts; doc drift; SparkGenerator's purpose

Operator: "Norte interno, público só o medido (Recomendado)". Doc drift is lying text, so every drift item is in scope. Each docs unit holds net lines ≤ 0. The exceptions are the Spark purpose paragraph (AC5.3), `context7.json` (AC6.4) and the front matter (AC6.5).

- R4, main-thread ruling (pre-mortem), re-anchored at `9c1351e`. The public texts are:
  - `README.md:3`, `:39`, `:49`;
  - `llms.txt:3`, `:29` (`rand_engine/llms.txt` after AC6.3);
  - `rand_engine/cli.py:22`;
  - `rand_engine/cases/faker.py.txt:2`, which `docs/tutorials/faker.md:20` includes by `--8<--`;
  - `docs/explanation.md:17`;
  - `mkdocs.yml:2`;
  - `skills/rand-engine/SKILL.md:3`;
  - `pyproject.toml:4` with `rand_engine/__init__.py:1`;
  - R17, main-thread ruling (pre-mortem): `docs/5_RECIPES.md:10` ("Faker is slow per value") and `AGENTS.md:9` ("fast synthetic data generation");
  - R18, main-thread ruling (pre-mortem): `docs/comparison.md`.

  Facts stay ("vectorized NumPy", a benchmark link); unmeasured speed adjectives go. The README keeps its landing constraints: pitch first after the H1, heading order and the exact badge set (`tests/test_docs.py:832-850`), and absolute https links on master (`:217-226`).
- R18, main-thread ruling (pre-mortem): the operator's figures stand. "4.8× Faker" comes from the rc-1 grill, and the rc-2 scope was confirmed with "one CI run, three samples, medians". `docs/comparison.md` disclaims the comparison those figures cite (`:20-22`, `:87`), so it becomes an R4 site:
  - its CI-run section ("Bounded CI observations", `:24`) states what was measured: the 100,000-dict workload, run 39153239357, three samples, medians, and the limit of one run on one runner;
  - it no longer says "No winner is inferred" (`:87`);
  - the regression-table disclaimer (`:20-22`) stays, scoped to the regression table.
- AC5.1 (integration, `tests/test_docs.py`): the scan covers exactly the R4 list, with code spans and fences excluded (R21, main-thread ruling, pre-mortem). No line in it matches `(?i)\bfastest\b|\bvery fast\b|\bfast\b|numpy speed|\bslow\b`. `SKILL.md`'s description keeps "synthetic data" and "RandSpec" (`tests/test_docs.py:269-273`). The package docstring's first line stays equal to the wheel `Summary` (`tests/integrations/test_public_api.py:459-462`).
- AC5.2 (no test; a test would pin prose): the README's opening paragraph, which is the PyPI top, states only the grill facts:
  - a declarative spec, validated before generation;
  - related pk/fk tables without a database;
  - a reproducible seed;
  - NumPy-vectorized generation;
  - published benchmarks, losses included.

  Its one speed figure is "4.8× Faker", with the 100,000-dict workload, "one CI run, three samples, medians" (Q2), and run 39153239357 linked to `docs/comparison.md`. `docs/explanation.md:17` gives the measured Faker figure (0.769 s per 100,000 dicts, `docs/comparison.md:73`) instead of "slow per value" (Q7), and keeps its BENCHMARKS link. `docs/5_RECIPES.md:10` is rewritten the same way (R17). `docs/comparison.md` follows R18.
- R24, main-thread ruling (pre-mortem): the Spark pool contract is defined by reference: the Spark pool rule as the hotfix lane merges it, for `distincts` and for `distincts_prop`. For `distincts_prop`, the rule applies to its positive-weight keys, in order.
  - A floor of faithful 0.8.1 pools stays accepted:
    - `[1, 2.5]` as doubles;
    - `['x', None]` as text and nulls;
    - `[1, 'x']` and `[True, 'x']` as text.
- AC5.3 (integration, `tests/test_3_spark_generator.py` pins the pools; `tests/test_docs.py` runs the page): `docs/2_SPARK_GENERATOR.md` opens with its purpose: one spec runs on a laptop with `DataGenerator` and on Databricks with `SparkGenerator`. It states that dbldatagen is faster on Spark: 0.516 s against 1.341 s at 1M rows, "one CI run, three samples, medians", run 39153239357, linked to `docs/comparison.md`. The pool paragraph (`:76-77`) is replaced by R24's contract.
  - The page names each refused class and each accepted example as the lane merged them, the R24 floor included. Each one is pinned in `tests/test_3_spark_generator.py` by Spark `dataType` and literal values. A set compare cannot tell `1` from `1.0`, which is why the `dataType` is pinned (the set-only case at `:728-736` gains it).
  - "NaN, not null" for a `None` in a numeric pool is measured with Arrow on and off (`arrow_conf`, `:686`) and pinned under both. The page states it as measured, and states each setting's result if they differ.
- AC5.4 (unit, `tests/test_docs.py`: the pages run and the `exceptions.py` doctests stay): the drift items state 0.8.2 exactly (Q4). R25, main-thread ruling (pre-mortem), sets the partition:
  - a fault that static validation or the one-row net finds is a `SpecValidationError` at construction;
  - `RandEngineError` is raised at generation for:
    - size faults (`rand_engine/main/data_generator.py:39`, `:42`);
    - the fk no-eligible-parent cases still judged at generation (`rand_engine/core/_keys.py:131`, `rand_engine/main/spark_generator.py:207`);
    - the pk domain and int64 guards (`rand_engine/core/_keys.py:66`, `:70`);
    - columns with embedded transformers (`rand_engine/main/_rand_generator.py:154`, `:156`);
    - the writers;
  - `ColumnGenerationError` wraps a column's generation step: the method call, the conversion and the multi-column unpack (`_rand_generator.py:52-60`).

  The drift items:
  - `docs/errors.md:9-14` states R25's partition. `:15-16` loses its time-bound "no current library path raises it".
  - The `exceptions.py` docstrings become contracts checked against the raise sites (`grep 'raise .*Error' rand_engine`):
    - `RandEngineError` (`:10-17`) names raise families, not lines: size, fk eligibility, the pk domain and int64 guards, modifiers after embedded transformers, the global-transformer row count, the empty-schema derivation, `RandSpecs.faker_pool`, and the writers. Its "a column's failure surfaces as `ColumnGenerationError`" claim narrows to R25's generation step.
    - `SpecValidationError`'s "lists every problem found" (`:37`) narrows to the validators and the construction net; `RandSpecs.from_schema` reports one problem per raise.
    - `FileWriterError` (`:88-93`) loses its repeated "raised nowhere" sentence and the phrase "in this release".
    - The five exception docstrings keep their summary and their Examples section (`tests/test_docs.py:680-684`, `:700`, `:720-724`), and their doctests still run (`:727-735`), the "No size set" doctest (`exceptions.py:26`) included.
  - `docs/compatibility.md` adds one short 0.8.2 paragraph pointing to the CHANGELOG `### Changed` refusals; it does not duplicate that list. `:53-54` ("a complete validation report") is narrowed to what the validators report.
  - The comment at `rand_engine/main/spark_generator.py:48` becomes English. No other line of that file changes (invariant 12).
- AC5.5 (no test): `specs/constitution.md` `## Direction` stays; the north star stays internal.

### FR6 — Discovery metadata

- AC6.1 (integration, the wheel METADATA test in `tests/integrations/test_public_api.py`): `Project-URL` carries two new entries (Q6, the published copies at `scripts/docs_site.py:47-51`):
  - `llms.txt, https://marcoaureliomenezes.github.io/rand_engine/llms.txt`;
  - `Agent skill, https://marcoaureliomenezes.github.io/rand_engine/skills/rand-engine/SKILL.md`.

  The five current URLs stay.
- AC6.2 (same test): `Keywords` hold 17 terms: the repo's 14 GitHub topics read on 2026-10-31 plus `random-data`, `spark` and `parquet`. That adds three terms to today's list: `data-generation`, `python`, `test-fixtures`. R3, main-thread ruling (pre-mortem): `test_public_api.py:465-473` keeps an exact list, updated to these 17. R21: the test `test_wheel_keywords_are_the_fourteen_search_terms` (`:465`) is renamed to match. The classifiers add `Topic :: Software Development :: Testing :: Mocking` and `Topic :: Software Development :: Libraries :: Python Modules`.
- AC6.3 (integration, the wheel test plus `tests/test_docs.py`): R6, main-thread ruling (pre-mortem). The one tracked source is `rand_engine/llms.txt`, and the wheel ships it. R22, main-thread ruling (pre-mortem):
  - the move is a `git mv`, because `copy_input` (`scripts/docs_site.py:21`) copies only `git ls-files` (`:17`);
  - the source at `scripts/docs_site.py:47` changes to `rand_engine/llms.txt`, so the site still serves `/llms.txt`, byte-equal;
  - a wheel test asserts that `rand_engine/llms.txt` ships byte-equal to the tracked file.

  `.github/workflows/docs.yml:47` stays unchanged.
- AC6.4 (integration, `tests/test_docs.py`): `context7.json` at the repo root:
  - parses as JSON;
  - has `projectTitle` `rand-engine`;
  - lists `docs` among its folders;
  - lists `specs`, `tests`, `benchmarks` and `evals` among its excluded folders.
- AC6.5 (integration, `tests/test_docs.py`): each of the 17 nav pages other than Home carries a front-matter `description` of 50–160 characters. Every description differs from the others and from `mkdocs.yml`'s `site_description`. Home is generated from the README and so cannot carry front matter; `site_description` covers it (Q3). R23, main-thread ruling (pre-mortem): `docs/BENCHMARKS.md` is generated, so its description comes from its one writer, `render()` in `benchmarks/speed.py` (`:248`, written at `:319`), never from a hand edit.
- AC6.6 (E2E, J5.T1's scratch Zensical build of one page; the review cites it): a page's `<meta name="description">` is its front-matter `description`. If Zensical 0.0.70 does not render that tag, AC6.6 is reported as a Zensical limit, AC6.5 still holds for the raw Markdown agents read, and no theme override is added (Q5).

### FR10 — Changelog and closure memory

- AC10.1 (integration, `tests/test_docs.py:862-870` requires an ISO-dated header): rc-2 adds its entries under the existing `## [0.8.2]` header (`CHANGELOG.md:10`) and re-dates the header at rc-2's closure (R7). The date is corrected at ship if the publish date differs. Groups:
  - **Fixed**: `spark-pool-types-fail-or-corrupt`, from its hotfix lane; the lane writes no CHANGELOG line;
  - **Changed**: the measured public texts; `llms.txt` shipped in the wheel from `rand_engine/llms.txt`; the keywords and classifiers;
  - **Added**: the `llms.txt` and `Agent skill` Project-URLs; `context7.json`; the page descriptions.
- AC10.2 (closure memory pass, `pe`): the atoms state FR5 and FR6 as rc-2 leaves them:
  - `spark-generator` (`:26`, the pool contract);
  - `get-started-cli` (`:29`, the `list` line);
  - `documentation` (`:25`, `:36`, the `llms.txt` location, the page descriptions, `context7.json`);
  - `public-api` (Project-URLs, keywords).

  `ARCHITECTURE.md` `## Structure` names the `rand_engine/llms.txt` package resource. The same pass re-stamps the derived-from sha256 markers in `docs/1..5` whose atoms changed.

### Test changes the rulings carry

R3, R4 and R24 each change asserts in a `test(...)` commit that names the ruling:
- R3: the keyword list at `tests/integrations/test_public_api.py:465-473`, with the test renamed (R21);
- R4: the `cli.py:22` literal at `tests/test_9_cli.py:79`;
- R24: the set-only Spark pool case at `tests/test_3_spark_generator.py:728-736` gains its `dataType` pin. This tightens the test and loosens nothing.

R6 and R22 change paths and add the wheel byte-equality test. Every other assert is kept and nothing is skipped.

## Replaces

- The speed adjectives at every R4 site, and "Faker is slow per value" (`docs/explanation.md:17`, `docs/5_RECIPES.md:10`), become measured facts (R4, R17).
  - Consumers: `tests/test_9_cli.py:79`, `tests/integrations/test_public_api.py:459-462` (the equality stays), and the atom `get-started-cli.md:29` (closure).
  - `docs/tutorials/faker.md:20` includes `faker.py.txt` by `--8<--`, so it follows without an edit.
- `AGENTS.md:9` ("fast synthetic data generation") drops the adjective (R17).
- `docs/comparison.md`'s "No winner is inferred" (`:87`) becomes the measured statement of its CI-run section (R18).
- The root `llms.txt` moves to `rand_engine/llms.txt` by `git mv` (R6, R22). Its consumers:
  - `scripts/docs_site.py:47`;
  - `tests/AGENTS.md:8`;
  - `tests/test_docs.py:196`, `201`, `217`, `230`, `420`, `641`, `877`, `892`, `911`, `936`, `946`;
  - the atom `documentation.md:25,36` (closure).

  Unchanged: `CHANGELOG.md:70,77` (history); `rand_engine/cases/agent.md.txt:25`, which names the published URL; and `skills/rand-engine/SKILL.md:8`, which names `llms.txt` without a URL or path (R21).
- The exact keyword list and the test name at `tests/integrations/test_public_api.py:465-473` (R3, R21).
- "Spark coerces a mixed pool" (`docs/2_SPARK_GENERATOR.md:76-77`, atom `spark-generator.md:26`) becomes R24's contract.
- The absolute error-class claims (`docs/errors.md:9-16`, `exceptions.py:16-17`, `:37`, `docs/compatibility.md:53-54`) become R25's partition. The repeated `FileWriterError` sentence and "in this release" are deleted.
- The Portuguese comment at `spark_generator.py:48`.

## 5. Constraints and risks

| risk | control |
|---|---|
| Four jobs share `tests/test_docs.py`, and two share `docs/*.md` | the PLAN orders them in one chain or edges them |
| AC5.3 depends on the bug lane's contract (rework in flight) | the lane merges into `feature/0.8.2` before rc-2's jobs start; the wt-rc syncs before Job 4; the page follows the rule as merged (R24) |
| Docs that state more than the code: a repeating class (`docs-overstate-modifier-and-decimals-scope`, the rc-1 pool sentence) | each new sentence names only cases that a test or raise site decides; net lines ≤ 0 per docs unit |
| `llms.txt` moving, renamed public text | Replaces lists the consumers; the PLAN answers each one |
| Zensical may not render front-matter `description` | J5.T1 probes it first (Q5); no theme layer |
| README is also the PyPI page and the generated Home | the landing tests (`tests/test_docs.py:832-850`, `:217-226`) stay green unchanged |

- At promote, the operator approves the PyPI publish in the GitHub environment `production` (invariant 13).

## 6. Open questions

- None for the operator before approval. R17–R25 answer the pre-mortem's hits. Q3 (Home covered by `site_description`), Q5 (the Zensical probe) and Q6 (the two Project-URLs) are the grill's agent defaults, unruled. Approving this SPEC approves them.
