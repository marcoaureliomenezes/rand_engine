# PLAN — Release: 0.8.0, candidate 10 (stream performance and preview install truth)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-10/SPEC.md`
**Approval:** The operator approved the exact pandas conversion and its bounded
test adjustment, and confirmed the Faker preview-install bug and correction, on
2026-10-18. The records are the mandatory grill handoff
`2026-10-18T142912Z-main-thread-rc10-grill.handoff.json` and
`2026-10-18T142804Z-main-thread-approved-next-actions.html`.

## 1. As-is review

This candidate contains Arm A for the operator-authorized stream conversion and
Arm B for `preview-faker-install-guidance`. The read-only as-is review is
`2026-10-18T142655Z-dd-sw-engineer-sr-rc10-as-is.handoff.json`; the exact
conversion scope and measurement are
`2026-10-18T033518Z-main-thread-stream-conversion-proposal.html`. The measured
CI benchmark is already RED: `stream_dict` ratio `1.345696313` against the
unchanged `1.3` limit. It is the performance evidence; changing public-contract
tests can remain GREEN on their parent because public behavior is unchanged.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/main/data_generator.py` record conversion | normalizes a microbatch, scans Arrow eligibility, conditionally calls Arrow, and falls back to pandas | 0 open; operator replaces rc-4 Arrow requirement | REBUILD | one normalized pandas `to_dict("records")` path replaces the helper, conditional conversion, narrow fallback, and Arrow-only import without changing the public stream contract. |
| `tests/test_6_stream_objects.py` Arrow boundary tests | combines public record assertions with Arrow invocation, eligibility, fallback, and error-propagation mechanics | 0 open | UPDATE, operator-authorized | retain values, exact types, key order, normalized nulls, timestamps, offsets, and cadence; delete only assertions listed in SPEC AC1.3. The authorized test commit records the ruling. |
| `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/compatibility.md`, and `skills/rand-engine/SKILL.md` | describe an Arrow-or-pandas stream path | 0 open | UPDATE | public consumers need one truthful normalized pandas record path; other Arrow features remain described where applicable. |
| `tests/test_docs.py` preview-preparation contract | scans prepared Markdown, llms and skill text, then exposes copied case resources without inspecting their install guidance | 1 (`preview-faker-install-guidance`) | REBUILD | the test home must inspect every copied public case resource and prove no exposed project install bypasses the reviewed SHA. |
| `rand_engine/cases/faker.py.txt` and `docs/tutorials/faker.md` | the included canonical case has two ordinary extra-install comments; the tutorial says the file has its install line | 1 (`preview-faker-install-guidance`, caused by `J6.T8`) | REBUILD | replace only the stale comments and corresponding tutorial claim with the existing Getting started authority, preserving runnable bytes, CLI output and tutorial include identity. |
| `specs/bugs/BUGS.jsonl` record `preview-faker-install-guidance` | confirmed MEDIUM bug is open with no fix SHA | 1 open | UPDATE | resolve through the canonical ledger only after the hardened oracle is RED against the parent and GREEN after the source correction. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| stream record conversion after existing normalization | `DataGenerator.stream_dict` in `rand_engine/main/data_generator.py` | `StreamHandler.convert_dt_to_str`, retained public stream tests | `_stream_records_are_arrow_compatible`, its Arrow-only import, conditional Arrow conversion and fallback path |
| public stream values, types, ordering and cadence | `tests/test_6_stream_objects.py` observable record assertions | `DataGenerator.stream_dict`, `StreamHandler` sleep seam | Arrow boundary invocation, eligibility, representation-fallback and unrelated-Arrow-error assertions only |
| preview installation guidance in the Faker scaffold | `rand_engine/cases/faker.py.txt` | live Getting started route, `docs/tutorials/faker.md`, CLI byte-copy contract | the two ordinary preview-exposed install commands |
| every prepared public preview install instruction | `tests/test_docs.py` preparation oracle | raw copied `rand_engine/cases/*` resources, `scripts/docs_site.py` output | the partial scan that overlooks copied case-resource guidance |
| bug status and fix linkage | `bugs.py resolve` over `specs/bugs/BUGS.jsonl` | RED/GREEN task commits and their reviewer evidence | open record after its correction is merged |

## 2. Decisions and gate cost

- Job 1 deletes the Arrow-specific conversion branch and narrows only the
  explicitly authorized implementation assertions. It retains all observable
  partitions. No public assertion is weakened, no alternate record path or
  feature flag is added, and `StreamHandler` and protected generation units do
  not change.
- The parent already demonstrates the performance failure. A new pandas mock or
  implementation-mirroring RED test would not test a changed public contract,
  so it is not created. The existing candidate-head benchmark remains the sole
  performance gate and its base, workload and `1.3` limit remain unchanged.
- Job 2 repairs the canonical source, not documentation preparation. The
  tutorial continues to include the same case bytes and the CLI continues to
  emit them; only its guidance points to the existing preview-bound Getting
  started authority.
- The repository `verify:` line, CI matrix, strict docs build, documentation
  contracts and benchmark workflow are unchanged. Targeted task checks exercise
  their owners; the official job and candidate merges alone run the full
  `verify:` gate, so no duplicate permanent gate or dependency is introduced.
- Reconciliation, official feature push, public retrieval, source-ZIP journey,
  benchmark observation and frozen rescore occur only after reviewed source
  closure. They award no score before public evidence and retain the stable
  hold in SPEC FR3.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `rand_engine/main/data_generator.py`, `tests/test_6_stream_objects.py`, `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/compatibility.md`, `skills/rand-engine/SKILL.md` |
| Job 2 | — | 1 | `tests/test_docs.py`, `rand_engine/cases/faker.py.txt`, `docs/tutorials/faker.md`, `specs/bugs/BUGS.jsonl` |

The jobs are parallel-safe because their exact write sets are disjoint. Within
each job, tasks run in table order. Job 2's ledger transition waits for the
source correction merged into its job tree and is a governance-only write in
that job's `wt-main`; the one job review follows the ledger transition.

## 3. Requirement trace and post-merge boundary

| acceptance criteria | owner and evidence |
|---|---|
| AC1.1–AC1.3 | Job 1: authorized test adjustment, then source REBUILD; retained observable partitions and parent benchmark failure establish the before state. |
| AC1.4 | Job 1 consumer-guidance task updates every named human and agent consumer of the replaced record-path claim. |
| AC1.5 | existing benchmark workflow after reviewed candidate-head push; no task changes it. |
| AC2.1 | Job 2 RED oracle over prepared documentation and every copied case resource. |
| AC2.2–AC2.3 | Job 2 canonical case/tutorial correction plus existing CLI/include byte-identity contracts. |
| AC2.4 | Job 2 canonical ledger resolution after the RED/GREEN evidence and correction are merged into the job tree. |
| AC3.1 | unchanged official job/candidate merge gates, strict docs build and native CI matrix. |
| AC3.2–AC3.3 | main thread after whole-candidate review, official merge and feature push: retrieve public preview/resources, run the consumer path, observe benchmark, then obtain an independent frozen-rubric rescore. No source task claims those observations. |

## 4. Reconciliation (after both jobs)

**W:** `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`,
`specs/memory/product/generation/data-generator.md`,
`specs/memory/product/onboarding/documentation.md`,
`specs/memory/product/onboarding/get-started-cli.md`,
`specs/memory/product/catalog.json`, `specs/memory/product/index.md`, and
`specs/releases/0.8.0/_RELEASE.json`.

The product engineer derives the final memory worklist from the source diff,
updates only facts established by it, refreshes affected derived markers and
catalog/index, moves the release phase through its canonical writer, and runs
the release, bug, backlog, memory and doctor checks. It records public proof as
pending until the reviewed official feature head is deployed and observed.
