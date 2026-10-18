# SPEC — Release: 0.8.0, candidate 10 (stream performance and preview install truth)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** bugs:preview-faker-install-guidance
**Approval:** Operator “Aprovar a troca e os ajustes de testes descritos” and
“Confirmar e corrigir o bug” on 2026-10-18.

- The mandatory grill handoff
  `2026-10-18T142912Z-main-thread-rc10-grill.handoff.json` has no unanswered
  question. It binds this candidate to the exact stream-conversion proposal and
  the confirmed Faker preview defect.
- The operator's stream ruling explicitly replaces rc-4's Arrow-path
  requirement and authorizes removal of only the Arrow-specific implementation
  assertions identified below. That operator demand is recorded by the Approval
  line and release note because the canonical Origin grammar cannot combine
  `operator-demand` with a bug pick. Public record behavior remains unchanged.
- The as-is authority table is
  `2026-10-18T142655Z-dd-sw-engineer-sr-rc10-as-is.handoff.json`; the exact
  approved scope is preserved in
  `2026-10-18T142804Z-main-thread-approved-next-actions.html` and the measured
  conversion proposal in
  `2026-10-18T033518Z-main-thread-stream-conversion-proposal.html`.

## Bug window review

Rc-9 resolved no bug-ledger record and added no persisted `fix_sha`, so there is
no new prior fix to judge KEEP or REBUILD. Its public verification instead found
`preview-faker-install-guidance`, now an open MEDIUM record. The record's public
reproduction finds two ordinary `pip install "rand-engine[faker]"` comments in
the rendered Faker tutorial where rc-9 requires every preview installation
route to identify the same immutable reviewed SHA.

The older correlated fix `faker-extra-undocumented-unpinned-install` is retained:
the extra remains declared and ordinary stable guidance remains quoted and
discoverable. This candidate fixes the distinct preview leak by routing the
canonical case comments to the existing Getting started authority and by
strengthening the current preview-artifact oracle. It does not add a second
installer or rewrite included case bytes during documentation preparation.

The active `outreach` backlog entry remains open. Two authorized pre-stable
submissions have been opened as separate external evidence, but acceptance,
indexing, comparison CI, posts, Discussions and on-demand conda-forge work are
not complete and are not dispositioned by this candidate.

## 1. Problem

Rc-4 introduced a conditional Arrow record path after stream normalization. In
the required one-million-record benchmark, the current candidate took
8.516387594 seconds against 6.328610335 seconds at its fixed base: ratio
1.345696313, above the unchanged 1.3 regression limit. The eligibility scan and
two conversion paths add work while the already-normalized pandas frame can
produce the same public records directly.

That implementation detail is protected by tests that mix public behavior with
Arrow invocation, call counts, eligibility and fallback mechanics. The operator
has approved deleting only those Arrow-specific assertions and restoring one
normalized pandas `to_dict("records")` path. Values, exact types, key order,
missing-value normalization, timestamps and cadence remain product contracts.

Separately, the deployed unreleased preview is reachable and correctly binds its
main installation guidance to one reviewed SHA, but its verbatim Faker case
include carries two ordinary installation comments. This contradicts rc-9's
preview-install contract and lowers evidenced onboarding and public acceptance.

The latest frozen score is 92.5/100 overall, with discoverability at 15/20
(75%) and onboarding at 17.5/20 (87.5%). Stable 0.8.0 remains held until the
required CI and benchmark pass and the frozen rubric is strictly greater than
90 overall and in every category. This candidate earns no score for a plan or
an unobserved fix.

## 2. Measurable goals

- `stream_dict` uses one pandas record conversion after its existing
  normalization and passes the unchanged one-million-record benchmark at ratio
  less than or equal to 1.3 against the same base and workload.
- All existing public record partitions retain their values, exact Python types,
  key order, `None` handling, datetime strings, `timestamp_created`, continuous
  offsets and sleep cadence; protected generation and stream scheduling units
  remain unchanged.
- The prepared public preview contains zero ordinary rand-engine installation
  commands in copied case resources. The Faker scaffold points to the live
  Getting started installation authority while the CLI output and tutorial
  include remain the same bytes.
- The confirmed bug closes with a behavior regression test, the full repository
  checks stay green and public verification/rescoring records only observed
  post-merge evidence.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — runtime and preview truth | one normalized pandas record path; one preview-install oracle and canonical Faker guidance | AC1.1–AC2.4 |
| 2 — reviewed evidence | truthful consumers, fixed benchmark, bug closure and post-merge public proof | AC1.4–AC3.3 |

## 3. Non-goals

- Changing the benchmark base, one-million-row workload, 1.3 limit, workflow,
  dependency set or rerunning a failed measurement merely to seek a favorable
  sample.
- Changing `StreamHandler`, any protected `gen_*` primitive, RandSpec semantics,
  public method signatures, throughput bounds, offset logic or timestamp/sleep
  behavior.
- Retaining an alternate Arrow path, adding a feature flag or replacing public
  behavior tests with assertions that mirror pandas implementation details.
- Rewriting included resources in `scripts/docs_site.py`, adding a second
  installation authority, changing CLI case selection or changing the runnable
  Faker example.
- Stable publication, promotion, search indexing or rank, acceptance of the two
  external submissions, broad outreach closure, comparison CI, posts,
  Discussions, Context7 or conda-forge.
- Changing dadaia-workspace, hooks, worktree behavior, agents, skills, rules or
  configuration.

## 4. Requirements

### Terms

- **Normalized frame:** the pandas frame after the existing
  `StreamHandler.convert_dt_to_str` operation and missing-value normalization.
- **Public record contract:** record values and exact types, key order, `None`
  handling, datetime strings, offset continuity, `timestamp_created` insertion
  and rate-limiting cadence.
- **Preview installation instruction:** any public instruction that installs the
  rand-engine project or optional extra while the unreleased preview is active.
- **Getting started authority:** the live preview page whose generated commands
  already bind installation to the reviewed event SHA.

### FR1 — Restore one fast record-conversion path without a contract break

- AC1.1 (integration and existing performance gate): after unchanged
  normalization, every `stream_dict` microbatch converts with
  `DataFrame.to_dict("records")`. The Arrow eligibility helper, conditional
  conversion and narrow Arrow fallback leave this path; an import used only by
  the deleted helper leaves with it. No second conversion path or feature flag
  remains.
- AC1.2 (unit/integration): existing tests continue to cover size and callable
  size, missing-value normalization, safe scalars, nested and mixed object
  values, NumPy/pandas nullable scalar partitions, non-string-label behavior,
  exact types, key order, datetime strings, continuous keys,
  `timestamp_created` and sleep cadence. Those product assertions are retained
  or rewritten around their observable values, never weakened or skipped.
- AC1.3 (operator-reserved test ruling): remove only the prior implementation
  assertions for `_record_arrow_boundary`, Arrow invocation/call counts,
  Arrow-path exclusion, Arrow representation fallback and propagation of an
  unrelated Arrow conversion error. Boundary mocks in otherwise useful public
  value tests may be removed; their value and exact-type assertions remain.
  This is the exact scope authorized by “Aprovar a troca e os ajustes de testes
  descritos.”
- AC1.4 (integration): the DataGenerator docstring, data-generator guide,
  recipes, explanation, compatibility guide and Agent skill state one normalized
  pandas record path and retain the public stream behavior. The executable guide
  uses neutral record names and keeps its value assertions. No other use of
  Arrow, including schema-based RandSpec construction, changes.
- AC1.5 (existing performance gate): the candidate-head benchmark publishes the
  one-million-row `stream_dict` row and passes the existing ratio limit of 1.3
  against the unchanged base, code, workload and environment record.

### FR2 — Remove the Faker preview installation leak at its source

- AC2.1 (integration, RED first): the existing preview-preparation contract also
  inspects copied public case resources. In preview mode, each own-project
  installation instruction it can expose identifies the same reviewed SHA; the
  two current ordinary Faker-extra commands make the hardened test fail before
  the fix and the expected match count after the fix is zero.
- AC2.2 (unit/integration): `rand_engine/cases/faker.py.txt` replaces its two
  installation commands with concise pointers to the live Getting started
  authority. The runnable example, prerequisite meaning and package resource
  identity remain intact.
- AC2.3 (integration): the Faker tutorial routes installation to its generated
  preview command and Getting started authority rather than claiming the
  included file contains an install line. The included case remains byte-equal
  to the packaged resource and to `rand-engine get-started faker` output.
- AC2.4 (bug ledger): `preview-faker-install-guidance` resolves only after the
  hardened oracle is RED against the parent and GREEN with the source
  correction. Post-merge public observation remains separately required by
  AC3.2 and is never claimed by source closure.

### FR3 — Close with truthful evidence while retaining the stable hold

- AC3.1 (existing gates): the repository verify command, documentation
  contracts, strict site build and existing native CI matrix pass. No existing
  gate is loosened and no new permanent gate is introduced.
- AC3.2 (release/public integration): after reviewed official merge and feature
  push, the actual preview HTML and raw resources are retrieved again. The proof
  records the reviewed SHA, zero ordinary Faker preview installations, working
  Getting started route and successful source-ZIP consumer path before any score
  credit is awarded.
- AC3.3 (independent product rescore): the unchanged frozen 20-check rubric is
  rescored from the post-merge source, CI, benchmark and public observations.
  Stable promotion remains blocked unless the result is strictly greater than
  90 overall and within every category; external submissions, acceptance,
  indexing and rank receive only their separately observed credit.

## 5. Replaces

- Rc-4 AC4.1–AC4.3 and their current Arrow-compatible eligibility, conversion
  and fallback implementation are replaced by one normalized pandas record
  conversion under AC1.1–AC1.5.
- Arrow-only assertions and tests listed in AC1.3 are replaced by the retained
  public record contracts in AC1.2. No public assertion is replaced.
- The two ordinary installation comments in the canonical Faker case and the
  tutorial claim that the case carries its install line are replaced by the
  existing Getting started installation authority and its preview-bound command.

## 6. Constraints and risks

| risk | control |
|---|---|
| pandas conversion changes a public scalar or order partition | preserve exact-value/type/order assertions across every existing partition |
| test narrowing deletes product coverage with Arrow mechanics | AC1.3 enumerates the only authorized removals; reviewer compares the parent and reverted implementation |
| local timing passes but fixed CI still fails | unchanged candidate-head benchmark is authoritative; no threshold, base or workload adjustment |
| Faker guidance diverges between CLI and docs | edit the canonical packaged case and retain the existing byte-identity include/CLI contracts |
| source proof is mistaken for public proof or score credit | public retrieval and independent rescore happen only after reviewed feature push |
| successful correction is mistaken for stable authorization | AC3.3 retains the explicit overall, per-category, CI and benchmark hold |

## 7. Open questions

None. The operator approved the exact stream replacement and prior-test ruling,
confirmed the Faker defect and correction, and separately authorized the two
pre-stable external submissions. Submission acceptance and indexing remain
observations, not assumptions or candidate requirements.
