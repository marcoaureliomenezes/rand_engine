# SPEC — Release: 0.8.0, candidate 3 (documentation excellence for humans and agents)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-17
**Origin:** backlog:documentation-excellence

- Operator demand, 2026-10-16: document rand-engine so human and agent users can
  discover it, onboard, test its features and use its APIs and use cases well.
- The operator confirmed the refined scope on 2026-10-17: current API reference,
  including returned writers and caller-facing errors; parameter domains and
  pandas/Spark differences; builders, use cases and execution of the five packaged
  examples; useful agent-readable documentation; memory reconciliation and the
  deferred documentation-marker refresh. Handoff:
  `2026-10-17T160713Z-main-thread-rc3-grill.handoff.json`.
- "Current" below means the supported capability snapshot at this candidate's
  birth: the top-level `rand_engine.__all__`, `rand_engine.examples.__all__`, writer
  objects returned by `DataGenerator.write` and `writeStream`, the
  `RandEngineError` family callers catch, `METHOD_CATALOG`, the five `CASES`, and
  their code-defined behavior. Internal cores and validators do not become public
  exports.

## Bug window review

This table judges rc-2's six resolved records (five fix commits). Each persisted
`fix_sha` was read with `git show` against the overfitting patterns. The two
`int_zfilled` records share one fix.

| bug | fix_sha | pattern hit | verdict | why |
|---|---|---|---|---|
| `int-zfilled-nonpositive-length-validates-then-raises`, `int-zfilled-length-above-18-validates-then-raises` | `4a95036` | >= 2 fixes touch the Spark width path (`7c3566b`, `d6569d4`, then this fix) | KEEP | rc-2 already REBUILDs the rule: one catalog semantic owns `length` 1..18 for both validators and the Spark clamp is deleted; the hardened partitions cover 0, -1, 19 and valid 1, 8, 18, with no child bug |
| `package-docstring-contradicts-pitch` | `fe09f54` | none | KEEP | one package-summary line is tied to the `[project]` description by its contract test |
| `stream-trigger-frequency-annotated-int` | `9cfd121` | none | KEEP | the one annotation now matches the accepted fractional-seconds behavior and its type-hint test |
| `reference-test-self-referential` | `adc66be` | the fix changes a test | KEEP | the test itself was the bug; its cases now come from `rand_engine.__all__`, and the recorded mutation proves deleting a public directive turns it red |
| `pipeline-doc-matrix-stale` | `301dd32` | deleted functionality | KEEP | the deleted file was a hand-copied workflow description with no consumers; workflow YAML remains the authority |

No verdict is REBUILD, so the candidate carries no bug-window implementation work.
The four correlated Spark methods' NULL-plus-warning behavior is documented from the
current validator and engine. This review makes no new claim about its older fix
lineage.

## 1. Problem

The 0.8.0 documentation site is runnable and broad, but its discovery paths do not
yet let a user answer several ordinary questions from one accurate source:

- `docs/reference.md` renders the three top-level `__all__` objects, while the
  writer objects returned by `DataGenerator` and the caller-facing error taxonomy
  have no rendered reference of their own.
- The human and agent method tables omit important domains. In particular,
  `int_zfilled` is 1..18 on `DataGenerator` and at most 15 on Spark; Spark also
  refuses `uint64` and integer widths above 2^53. Engine-only, refused and
  NULL-plus-warning outcomes are split across pages.
- Builder documentation demonstrates happy paths but does not give the supported
  Arrow-type/default map, override behavior, optional Faker prerequisite or
  representative failure outcomes. The twenty ready-made Common/Advanced specs
  are not easy to discover as a capability inventory.
- Getting started lists five scaffolds without putting each prerequisite, run
  command and observable local outcome in one place.
- `llms.txt` is a useful index, but the workflow also copies raw Markdown that can
  contain unresolved mkdocstrings and snippet directives. Agent-facing links must
  lead to useful rendered content or direct runnable source, without requiring a
  new export pipeline.
- Three hidden `derived-from` markers in `docs/1_DATA_GENERATOR.md`,
  `docs/2_SPARK_GENERATOR.md` and `docs/5_RECIPES.md` were deliberately deferred
  after the rc-2 memory correction.

## 2. Measurable goals

- A user can navigate from getting started to the supported generators, builders,
  returned writers and error family, with every rendered reference building
  strictly.
- Human and agent method inventories agree with `METHOD_CATALOG`, and executable
  boundary examples show the relevant pandas/Spark differences.
- Each packaged scaffold has one documented command, prerequisite and expected
  result, and all five still execute through the existing case contract at no more
  than 10^4 rows.
- `llms.txt` points agents to the rendered reference/guides and direct case files;
  advertised targets contain useful content rather than an unresolved build
  directive alone.
- Closure memory matches the final docs and code, and the three deferred markers
  are current.

## 3. Non-goals

- Any runtime behavior, public export, exception hierarchy, dependency, Python or
  Spark support range, package metadata or CLI behavior.
- A new docs framework, dependency, workflow, gate, generated-reference layer or
  Markdown expansion/export pipeline. Existing pytest documentation seams and the
  strict Zensical build are sufficient.
- Any change to `benchmarks.yml`, `benchmarks/**`, `docs/BENCHMARKS.md` or
  `docs/benchmarks.json`; rc-2's measured benchmark record remains byte-identical.
- Replacing or weakening the existing `docs/reference.md` assertion sourced from
  `rand_engine.__all__`.
- Fixing the CLI runpy warning, workflow installer pinning, hook/projection drift,
  template refresh warnings or any other unrelated intake item.
- Outreach, Context7 submission, awesome-list work, comparison marketing or stable
  publication; those follow the candidate.

## 4. Requirements

### Terms

- **Main API reference:** `docs/reference.md`, whose `:::` directive set is exactly
  the defining paths of the objects named by `rand_engine.__all__`.
- **Returned-writer surface:** `FileWriter.format`, `mode`, `option`, `options`;
  `FileBatchWriter.save`; and `FileStreamWriter.trigger`, `start`, reached through
  `DataGenerator.write` and `writeStream`. Naming their defining internal modules
  in rendered reference does not make those modules new public imports.
- **Caller-facing error family:** `RandEngineError`, `SpecValidationError`,
  `ColumnGenerationError`, `TransformerError` and `FileWriterError`. Documentation
  states that `FileWriterError` is declared but currently not raised.
- **Method inventory:** the methods, required/optional kwargs and engine outcome
  represented by `METHOD_CATALOG` and Spark validation at candidate birth.
- **Packaged examples:** `test-data`, `lake`, `kafka`, `databricks` and `faker`, the
  five values of `rand_engine.cli.CASES`.
- **Useful agent target:** a rendered site page or direct repository file whose
  content explains the linked subject or is runnable source. An unresolved `:::`
  or `--8<--` directive by itself is not useful content.

### FR1 — Complete the current API reference

- AC1.1 (unit, existing contract): `test_reference_directive_names_the_canonical_documented_object`
  is unchanged and green. The Main API reference continues to contain exactly the
  canonical directives derived from `rand_engine.__all__`; returned writers and
  errors do not enter that set.
- AC1.2 (unit): a separate returned-writer reference has one canonical rendered
  entry for `FileWriter`, `FileBatchWriter` and `FileStreamWriter`. Its documented
  callable surface is exactly the Returned-writer surface, including inherited
  chain methods, return behavior and the accepted format/mode/option boundaries.
  The expected objects and callables come from the classes, not from the page under
  test.
- AC1.3 (unit): an error reference names every class in the Caller-facing error
  family, its common base, when a caller receives it and what context its message
  carries. Examples catch the real classes and run; the page does not claim that
  `FileWriterError` is raised.
- AC1.4 (integration): the reference/discovery surface renders the current
  `rand_engine.examples.__all__`: `RandSpecs`/`CommonRandSpecs` and
  `AdvancedRandSpecs`, including `faker_pool`, `from_schema` and the public
  ready-made spec factories. It states that top-level `RandSpecs` aliases
  `CommonRandSpecs`; no new top-level export is added.
- AC1.5 (integration, existing strict docs build): the navigation exposes the Main
  API, returned-writer, error and builder reference destinations, and the strict
  Zensical build exits 0 with no broken internal link.

### FR2 — State method domains and engine differences from their code authorities

- AC2.1 (unit): the human method inventory and the agent skill each name exactly
  the methods in `METHOD_CATALOG`. For each method they identify its required and
  optional kwargs and its current engine outcome: DataGenerator, SparkGenerator,
  NumPy-only refusal, or correlated Spark NULL plus warning. The expected inventory
  is derived from the catalog and live Spark validation, never copied from either
  document under test.
- AC2.2 (integration, executable documentation): boundary examples demonstrate that
  `int_zfilled.length` 1 and 18 validate on `DataGenerator`, while 0 and 19 are
  refused; on Spark 15 validates and 16 is refused. Spark examples also demonstrate
  refusal of `integers.int_type="uint64"` and of an integer domain whose inclusive
  width exceeds 2^53. Every generated example uses at most 10^4 rows.
- AC2.3 (integration, executable documentation): the method guides state and run
  representative current boundaries for date directives, float decimals/ranges,
  distribution parameters, modifiers and multi-column methods. Spark's four
  correlated methods are shown as NULL plus warning, while `pk`, `fk`,
  distributions, `constant` and modifiers are shown in their current accepted or
  refused engine partition. No example changes the runtime to fit the prose.
- AC2.4 (unit): writer guidance and reference agree with the live writer classes on
  formats, modes and option names, and distinguish total batch rows, file count,
  `maxRowsPerBatch`, append/overwrite staging, stream frequency and timeout. The
  contract checks the accepted option inventory and executable outcomes rather
  than prose wording.

### FR3 — Make builders, use cases and all five examples usable from onboarding

- AC3.1 (integration, executable documentation): `RandSpecs.faker_pool` documents
  the optional `rand-engine[faker]` prerequisite, provider/locale/pool/seed
  behavior, returned `distincts` spec and representative `RandEngineError`
  partitions. Valid and invalid examples execute through the existing docs harness.
- AC3.2 (integration, executable documentation): `RandSpecs.from_schema` documents
  every supported Arrow type family and its default RandSpec recipe, nullable
  handling, override replacement versus merge, and representative unsupported
  type/override failures. Examples build and validate the actual returned specs.
- AC3.3 (unit): the docs expose the current ten `CommonRandSpecs` and ten
  `AdvancedRandSpecs` factories, identify the engines each family targets and link
  each family to an executable use case. The expected factory inventory comes from
  the classes, not from the page.
- AC3.4 (E2E, existing scaffold contracts): getting started gives each Packaged
  example its `rand-engine get-started <slug>` command, written filename,
  prerequisite and observable outcome. The five generated files remain byte-equal
  to their package resources and execute through the current tests: pandas test
  data, related Parquet lake tables, JSON records for Kafka, a Spark DataFrame and
  a Faker-backed DataFrame. Synthetic examples generate no more than 10^4 rows,
  write only under temporary output and replace an external broker only at its
  existing test boundary.
- AC3.5 (integration): a concise use-case map directs a user choosing among pipeline
  test data, a lake, Kafka/another queue, Spark/Databricks, Faker pools, related
  tables and direct file writers to the relevant runnable guide or case. Every link
  passes the existing strict build.

### FR4 — Give agents useful, light discovery outputs

- AC4.1 (unit): `llms.txt` links the main, returned-writer, error, builder/domain and
  use-case destinations plus all five direct packaged case files. Repository links
  target the principal branch and existing files; site links correspond to docs
  navigation destinations.
- AC4.2 (integration, docs artifact): every destination advertised to agents is a
  Useful agent target. Rendered HTML/reference pages and direct raw case files are
  preferred where expanding source Markdown would add another pipeline. Raw
  tutorial/reference Markdown copied by the workflow is either useful on its own
  or is no longer advertised as an agent contract.
- AC4.3 (unit): the agent skill's method outcomes remain derived from live
  validation, and its examples remain executable under the existing docs harness.
  Links from the skill and `llms.txt` resolve; no test asserts editorial prose.
- AC4.4 (no new test; reason: the strict build and documentation tests already run
  in the repo `verify:` and CI gates): this candidate adds no build step, dependency,
  gate or second generated documentation source.

### FR5 — Reconcile product truth and release-facing documentation

- AC5.1 (no test; memory is reviewed against cited code and docs, then validated by
  the existing memory tools): closure reconciles the documentation, public-api,
  templates-and-examples, generation-methods, rand-spec-grammar,
  writers-and-streaming and get-started-cli atoms as changed or reviewed according
  to the final diff. `ARCHITECTURE.md` and `QUALITY.md` change only where the final
  repository truth requires it.
- AC5.2 (no test; hidden provenance metadata): closure refreshes the deferred
  `derived-from` markers in `docs/1_DATA_GENERATOR.md`,
  `docs/2_SPARK_GENERATOR.md` and `docs/5_RECIPES.md` after their source atoms are
  final. The memory catalog check and drift check both exit 0.
- AC5.3 (integration, existing CHANGELOG landing contract): the 0.8.0 section of
  `CHANGELOG.md` records the user-visible rc-3 documentation additions without
  rewriting rc-1 or rc-2 history.

## 5. Replaces

- The incomplete human/skill method rows, including `int_zfilled` without its
  domains and Spark described only as using the same kwargs, are replaced by the
  catalog-backed inventory and explicit engine partitions in FR2.
- Writer behavior available only through docstrings and the writing how-to gains a
  separate rendered Returned-writer reference; the Main API reference and its
  `__all__` contract stay intact.
- The builder happy paths without a supported-type/default/error map are replaced
  by the bounded `faker_pool` and `from_schema` guidance in FR3.
- The five-link scaffold list without per-case prerequisites, commands and outcomes
  is replaced by the executable onboarding inventory in AC3.4.
- Agent discovery that may expose unexpanded copied Markdown is replaced by links
  to useful rendered pages or direct runnable case files; no expansion pipeline is
  introduced.
- The three deferred marker hashes are replaced by hashes derived from the final
  reconciled atoms.

## 6. Constraints, risks and open questions

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — dev-loop contracts | semantic inventories for writers, errors, methods, builders and cases, using the existing docs test home | AC1.1–AC1.4, AC2.1, AC2.4, AC3.3 |
| 2 — shared human reference | returned writers, errors, builders and code-backed method/domain reference | AC1.2–AC2.3 |
| 3 — onboarding and agent discovery | five scaffold outcomes, use-case routing, `llms.txt` and the skill | AC3.1–AC4.4 |
| 4 — promote-facing closure | release notes, product memory and deferred markers | AC5.1–AC5.3 |

### Constraints

- Documentation derives from the code authorities named in Terms. If the docs pass
  discovers a runtime contradiction, it reports a bug proposal; this candidate does
  not change runtime behavior to make a statement true.
- Existing behavior tests stay and are never loosened or skipped. New checks assert
  semantic inventories, executable examples or link/build behavior, not wording.
- Examples use synthetic data, at most 10^4 rows, temporary output and external
  caches. No production data, credential, broker, cloud write or persistent repo
  output is used.
- The benchmark record files and measured paths named by rc-2 are untouched.
- Known hook/projection and template drift belongs to the dadaia-workspace library
  session. This candidate neither reprojects nor installs hooks and never bypasses
  a gate; an actual gate refusal returns to the main thread.

### Risks

| risk | mitigation |
|---|---|
| Human and agent tables drift from `METHOD_CATALOG` | derive test expectations from the catalog and live Spark validation |
| Rendering internal writer/error defining paths is mistaken for a new public export | state the returned/caught contract explicitly and keep `rand_engine.__all__` unchanged |
| Machine-readable docs create a duplicate generated corpus | link rendered HTML/reference and direct case sources; add no expansion/export layer |
| Examples require Spark, Faker or a broker in ordinary onboarding | name prerequisites; keep Faker optional, reuse the existing Spark fixture and mock only the broker boundary |
| Documentation work expands into runtime cleanup | report contradictions and unrelated findings through intake; keep this SPEC's non-goals closed |

### Open questions

None. The confirmed grill answers the documentation depth, engine/domain coverage,
five-example execution, agent-readable outputs and marker reconciliation. The Draft
SPEC and the later PLAN still require the operator's explicit approval before the
candidate may enter implementation.
