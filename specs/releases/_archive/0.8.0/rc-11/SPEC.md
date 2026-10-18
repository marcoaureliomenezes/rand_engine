# SPEC — Release: 0.8.0, candidate 11 (release-note accuracy)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand
**Approval:** The standing operator demand to finish all rand-engine work and the
previous authorization “Aprovar a troca e os ajustes de testes descritos” cover
completion of the already-approved pandas substitution. The validated mandatory
grill records the main-thread ruling that correcting its overlooked release note
is not a new product decision or a new operator response.

- Mandatory grill:
  `2026-10-18T160702Z-main-thread-rc11-grill.handoff.json`; no unanswered
  question.
- As-is authority:
  `2026-10-18T160534Z-dd-sw-engineer-sr-rc11-release-note-as-is.handoff.json`.

## Bug window review

Rc-10 resolved `preview-faker-install-guidance` at `41df169`. Inspection of that
fix shows one canonical correction to the Faker case and tutorial while keeping
the declared extra and the Getting started installation authority. KEEP: this
candidate does not touch those files or their contract.

The false current release note is pure human prose, not a tool breaking its own
contract, so it creates no bug record. The active `outreach` backlog entry
remains open and outside this candidate.

## 1. Problem

`CHANGELOG.md` says 0.8.0 adds Arrow eligibility, Arrow record conversion and a
pandas fallback to `stream_dict`. Rc-10 removed that design under the approved
pandas substitution: the implementation now performs one normalized pandas
`DataFrame.to_dict("records")` conversion. The current Unreleased note therefore
contradicts source, approved rc-10 behavior and every current guide.

The frozen reassessment is 95/100 overall, with Guides at 87.5% and Trust at
75%; the earlier 100 score is superseded. Stable publication remains held on
the unchanged requirement to exceed 90 overall and in every category.

## 2. Measurable goals

- The 0.8.0 Unreleased stream bullet states the one normalized pandas records
  conversion and no longer claims Arrow eligibility, conversion or fallback.
- Every other release note and the Unreleased header remain unchanged.
- Existing gates, the current public evidence check and the unchanged frozen
  rescore establish the correction before stable promotion.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — release truth | correct the single current release-note bullet | AC1.1–AC1.3 |
| 2 — reviewed evidence | unchanged gates, current public proof and frozen rescore | AC2.1–AC2.3 |

## 3. Non-goals

- Runtime, benchmark base or workload, the 1.3 performance limit, dependencies,
  CI, workspace behavior, public APIs or stream behavior.
- Any test addition, removal or adjustment; publication-date bookkeeping;
  stable publication or promotion; broad outreach or disposition of `outreach`.
- Historical closed candidate SPECs, PLANs, release summaries or legitimate
  Arrow schema and CSV/Parquet writer statements.

## 4. Requirements

### FR1 — Make the current release note truthful

- AC1.1 (no test — reversible low-impact prose whose exact wording is not a
  product contract): only `CHANGELOG.md`'s current 0.8.0 stream bullet is
  updated to describe one normalized pandas `to_dict("records")` conversion.
  Semantic review compares it with `DataGenerator.stream_dict`, rc-10 and the
  current data-generator memory atom.
- AC1.2 (semantic review): the corrected bullet makes no Arrow eligibility,
  conversion or fallback claim and makes no new behavior, speed or compatibility
  claim.
- AC1.3 (semantic review): the 0.8.0 header stays `Unreleased`; all other
  changelog content and all historical release artifacts are byte-unchanged.

### FR2 — Retain the release hold until corrected evidence exists

- AC2.1 (existing integration gate): the repository's unchanged official
  verify and merge checks pass; no test, threshold, gate or workflow changes.
- AC2.2 (release/public integration): after reviewed official merge and feature
  push, evidence reads the current public source at that reviewed head and
  confirms the false Arrow/fallback release-note claim is absent.
- AC2.3 (independent product rescore): the unchanged frozen rubric is rescored
  from corrected-head and current public evidence. Stable promotion remains
  blocked unless the result is strictly greater than 90 overall and within
  every category; the prior 100 result remains superseded.

## 5. Replaces

- The current Unreleased claim that compatible batches use lossless Arrow
  conversion with pandas fallback is replaced by the already-approved one-path
  normalized pandas record conversion.

## 6. Constraints and risks

| risk | control |
|---|---|
| correction overstates the existing implementation | use the narrow rc-10 and source wording; add no new claim |
| publication state is changed early | retain `Unreleased`; publication date remains separate |
| a prose check becomes a redundant permanent gate | add no test or gate; use semantic review and existing checks |
| corrected source is mistaken for public proof | collect evidence only after reviewed official push, then rescore unchanged |

## 7. Open questions

None. The validated mandatory grill resolved the lying text by inspection and
recorded that no new product decision or operator question is required.
