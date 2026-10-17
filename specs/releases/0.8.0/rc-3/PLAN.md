# PLAN — Release: 0.8.0, candidate 3 (documentation excellence for humans and agents)

**Status:** Draft
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-3/SPEC.md`

## 1. As-is review

Paths are relative to the repo root. The evidence and line references below come from
`2026-10-17T143034Z-dd-sw-engineer-sr-rc3-as-is.handoff.json`; its ledger scan
found zero open bugs. The current candidate changes documentation contracts only.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `tests/test_docs.py` documentation contracts and executable blocks | owns the reference-`__all__`, method-table, tutorial, landing-link and executable-documentation seams | 0 open; `reference-test-self-referential` was resolved here in rc-2 and must remain hardened | UPDATE | it is the one existing home for semantic inventories and runnable docs. New cases derive expected data from code authorities; the canonical reference assertion is unchanged. |
| `docs/reference.md` | renders exactly the three top-level `rand_engine.__all__` objects | 0 | KEEP | the main API reference is already the single canonical `__all__` surface; returned writers and errors need destinations without adding their directives to this page. |
| `docs/3_WRITING_FILES.md` | explains writer use, formats and many options, but does not render the returned writer classes as a reference | 0 | UPDATE | this existing writer page carries the separate returned-writer reference and detailed guidance; a new writer page would duplicate it. |
| `docs/errors.md` | absent | 0 | ADD | caller-facing error taxonomy has no natural existing documentation owner; a dedicated rendered reference avoids treating an internal-module path as a new public import. |
| `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `skills/rand-engine/SKILL.md` | name methods, with incomplete `int_zfilled` and Spark-domain detail | 0 | UPDATE | the existing human and agent inventories are the discovery paths; their semantic inventories come from `METHOD_CATALOG` and live Spark validation. |
| `docs/5_RECIPES.md` | gives happy-path `faker_pool` and `from_schema` examples | 0 | UPDATE | it is the established builder guide; add the bounded supported-type/default, override and error guidance there. |
| `docs/getting-started.md`, `docs/tutorials/*.md`, `llms.txt`, `mkdocs.yml` | list scaffolds and agent links, but do not provide all prerequisite/outcome maps or all required rendered destinations | 0 | UPDATE | the current onboarding, tutorial, agent index and navigation surfaces can carry the material without an export pipeline. |
| `CHANGELOG.md` | has the dated 0.8.0 section and its existing landing contract | 0 | UPDATE | append the rc-3 user-visible additions in place; do not rewrite rc-1/rc-2 history. |
| `specs/memory/{ARCHITECTURE,QUALITY}.md`, relevant product atoms, `catalog.json`, `specs/backlog/*`, release state | rc-2 reconciled code truth; three documentation provenance markers were intentionally deferred | 0 open; deferred marker evidence is recorded in the as-is handoff | UPDATE | closure must reconcile all documentation-derived truth, regenerate the catalog, refresh markers only after atoms settle, exit the picked backlog entry and record the release events. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| which top-level names the Main API reference documents | `rand_engine.__all__` | `docs/reference.md`, `tests/test_docs.py` canonical-directive test | none |
| which writer calls and option boundaries are documented | `rand_engine/file_handlers/{writer,_writer_batch,_writer_stream}.py` classes | `DataGenerator.write`/`writeStream`, `docs/3_WRITING_FILES.md` | none |
| which error classes callers catch | `rand_engine/validators/exceptions.py` | generator, validator and writer call sites; rendered error destination | none |
| methods, kwargs and engine outcomes | `rand_engine/validators/method_specs.py` `METHOD_CATALOG` and live Spark validation | human guide, skill and docs contracts | incomplete copied table values |
| builders, factories and scaffolds | `rand_engine/examples/common_rand_specs.py`, `advanced_rand_specs.py`, `cli.py` `CASES`, and `rand_engine/cases/*.py.txt` | recipes, getting-started, tutorials and `llms.txt` | none |
| published documentation truth and provenance | final code/docs diff and the cited memory atoms | derived-from markers, memory catalog and release summary | the three deferred marker hashes |

### 1.2 Consumers

| changed surface | consumers | answered by |
|---|---|---|
| returned writers and error reference destinations | docs navigation, `llms.txt`, users following `DataGenerator.write` and caught exceptions | Job 1 |
| method/domain inventory | human guide, agent skill and executable docs blocks | Job 2 |
| builders and factory inventory | recipes, reference/discovery and tutorials | Job 2 |
| scaffold commands and outcomes | getting-started, five tutorials, direct case files and agent index | Job 3 |
| documentation memory and deferred markers | catalog readers, docs provenance and release closure | Reconciliation |

## 2. Decisions and measured gate cost

- The existing `tests/test_docs.py` is the sole test home. Every documentation
  job carries a separate RED test task followed by an implementation task whose
  `W:` excludes tests; no test is skipped or marked xfail. No current assert is
  moved, weakened or removed.
- Existing docs execution remains the evidence for runnable examples. Repository
  `verify:` and test CI run documentation tests; the strict Zensical build runs in
  Docs CI. No command, workflow, dependency, export pipeline or gate is added.
- The existing full `verify:` gate measured 47.7 s wall on Python 3.13 in
  `specs/releases/0.8.0/rc-2/PLAN.md` §3. No task adds a repeated gate; targeted
  task evidence is covered by its later job merge `verify:` and Docs CI strict build.
- The known workspace doctor hook/projection drift is reserved for the library
  session. It is reported as a blocker at closure and is neither repaired nor bypassed here.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `tests/test_docs.py`, `docs/3_WRITING_FILES.md`, `docs/errors.md`, `mkdocs.yml` |
| Job 2 | Job 1 | 2 | `tests/test_docs.py`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`, `docs/5_RECIPES.md`, `skills/rand-engine/SKILL.md` |
| Job 3 | Job 2 | 3 | `tests/test_docs.py`, `docs/getting-started.md`, `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `llms.txt` |

Job edges serialize work because all non-closure contracts have one declared
owner (`tests/test_docs.py`); this prevents concurrent writes to its semantic
inventory.

## 3. Reconciliation (after Jobs 1–3)

**W:** `CHANGELOG.md`, `docs/1_DATA_GENERATOR.md`, `docs/2_SPARK_GENERATOR.md`,
`docs/3_WRITING_FILES.md`, `docs/5_RECIPES.md`, `llms.txt`,
`specs/backlog/BACKLOG.json`,
`specs/backlog/_archive/backlog_histo.jsonl`, `specs/memory/ARCHITECTURE.md`,
`specs/memory/QUALITY.md`, `specs/memory/product/catalog.json`,
`specs/memory/product/api/public-api.md`,
`specs/memory/product/content/templates-and-examples.md`,
`specs/memory/product/generation/generation-methods.md`,
`specs/memory/product/index.md`,
`specs/memory/product/onboarding/documentation.md`,
`specs/memory/product/onboarding/get-started-cli.md`,
`specs/memory/product/output/writers-and-streaming.md`,
`specs/memory/product/spec/rand-spec-grammar.md`,
`specs/releases/0.8.0/_RELEASE.json`.

The product engineer performs the RC-FLOW reconciliation: move to CLOSURE, update
the listed atoms and derived docs, generate the catalog, refresh all three deferred
markers after the atoms settle, add the rc-3 CHANGELOG line, exit
`documentation-excellence`, and record the closure summary/state. The existing
memory, backlog, release and doctor verbs validate it. Known library-owned doctor
drift is reported and is neither repaired nor bypassed. No bug ledger archive is
planned: this documentation-only candidate resolves no terminal bug record.

