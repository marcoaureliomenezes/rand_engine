# PLAN — Release: 0.8.0, candidate 13 (outreach closure and final maintenance)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-13/SPEC.md`
**Approval:** The Draft SPEC records the completed mandatory grill, the standing
operator approvals for the retained outreach scope and final maintenance, and
the main-thread publication-format ruling. No task starts until the operator
approves this PLAN together with the SPEC and the release enters IMPLEMENTATION.

## 1. As-is review

This is Arm A. The read-only maintenance authority is
`2026-10-18T165336Z-dd-sw-engineer-sr-poststable-maintenance-as-is.html`; it
reviewed the five workflow pin sites and the two skill clauses at
`98dcb45cd5ca3a0ce167e587c5d3582fcaf0e096`. The main thread confirmed those
six files remain byte-identical through rc-12. The Draft SPEC identifies the
single additional guide-format update. The bug ledger has 0 open records. The
active `outreach` item is this candidate's ledger pick and its exit is product
reconciliation work, not a source task.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `.github/workflows/auto_tag_publish_development.yml:99`, `.github/workflows/auto_tag_publish_master.yml:85`, `.github/workflows/pr_to_development.yml:169`, `.github/workflows/pr_to_master.yml:47`, `.github/workflows/test_on_push.yml:60` | each Java 17 setup step pins `actions/setup-java` v4 | 0 open | UPDATE | Replace only the immutable action SHA/comment pair with the approved v5.7.0 pair. The existing workflow inputs, triggers, permissions, matrices, commands and gates remain the behavior authority. |
| `skills/rand-engine/SKILL.md:28,177` | current user guidance contains one obsolete wheel-history clause and one implementation-history lead-in | 0 open | UPDATE | Prune only the stale provenance while retaining starter safety and the direct pandas-record contract. This is repository-native skill source; its existing documentation contracts continue to cover its structure and prepared mirror. |
| `docs/comparison.md:36` | records the observed Java runner version as an IP-shaped dotted token | 0 open | UPDATE | Replace only its representation with the same four opaque components in publication-safe prose. The comparison evidence, workload, pins, samples and claims remain authoritative and unchanged. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| Java setup action identity | the five named `uses: actions/setup-java` lines | maintenance as-is report and the existing v5 comparison workflow | the five v4 SHA/comment pairs only |
| current Agent-starter and stream guidance | `skills/rand-engine/SKILL.md` current surrounding instructions | maintenance as-is report and `tests/test_docs.py` documentation contracts | the rc4 wheel provenance clause and historical normalization lead-in only |
| public comparison Java observation | `docs/comparison.md` observed-environment paragraph | approved rc-13 SPEC and main-thread publication-format ruling | the dotted four-component rendering only |
| outreach delivery disposition | product-engineer reconciliation over the approved evidence | Discussion #51, external PRs #18 and #393, Actions run 39153239357 and `docs/comparison.md` | broad idea-stage `outreach` wording at closure only |

## 2. Decisions and verification

- Job 1 contains three fully stated, disjoint literal/prose tasks. They have no
  new behavior, dependency, runtime, lock, benchmark, gate, assertion-removal
  or workspace change. The `jr` ownership is retained; the documented senior
  fallback can execute it without changing its scope, model configuration or
  exact write set.
- Task 1 replaces exactly the five approved `setup-java` SHA/comment pairs.
  It does not add a brittle pin-text test. Native hosted CI after the reviewed
  candidate reaches its publication branch is the behavior proof; a release
  job that skips because 0.8.0 already exists is recorded as skipped.
- Task 2 applies the AUTHORING pruning rule to the two quoted historical skill
  clauses. Existing `tests/test_docs.py` frontmatter, executable-block, link,
  catalog and prepared-mirror contracts, plus the strict documentation build,
  remain intact. No phrase-mirroring assertion is added or removed.
- Task 3 replaces the Java observation with exactly `Java (version components:
  17, 0, 20, 1)`. It does not edit the comparison harness, requirements,
  workflow, artifact facts or performance conclusions. The official
  unpublished-suffix remedy and exact-head review are main-thread work after
  candidate integration.
- The unchanged official job and candidate merge gates are the automated
  protection. Tasks do not run or duplicate full verification locally. PE
  reconciliation performs AC4.1–AC4.4 after source/documentation gates; native
  CI evidence remains post-merge and does not block that reconciliation.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `skills/rand-engine/SKILL.md`, `docs/comparison.md` |

## 3. Requirement trace and post-merge boundary

| acceptance criteria | owner and evidence |
|---|---|
| AC1.1–AC1.2 | J1.T1 exact five-site diff; source review retains Java 17, Temurin, cache behavior, triggers, permissions, matrices, commands and gates. |
| AC1.3 | main thread observes normal hosted native CI after the reviewed candidate is on its publication branch, recording only actually executed setup-java steps. |
| AC2.1–AC2.2 | J1.T2 semantic comparison with the approved quoted clauses and surrounding current guidance. |
| AC2.3 | unchanged documentation contracts and strict site build at the official merge gate; no task-local duplicate. |
| AC3.1 | J1.T3 single representation replacement; source diff proves every comparison fact remains unchanged. |
| AC3.2 | main thread applies the existing publication-gate remedy only to the unpublished suffix after official candidate merge, preserving public `bff8526...`, then obtains exact-head review. |
| AC3.3 | unchanged documentation validation at the official merge gate; no task-local duplicate. |
| AC4.1–AC4.4 | dd-product-engineer reconciliation verifies the bounded evidence and exits `outreach` as delivered, without claims of external acceptance, indexing, adoption, ranking or excluded channels. |
