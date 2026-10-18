# PLAN — Release: 0.8.0, candidate 11 (release-note accuracy)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-11/SPEC.md`
**Approval:** The approved SPEC at `1bbaa7de0b8667a1e29daf594826385c6b756e0f`
records the standing operator authorization and the validated mandatory grill.

## 1. As-is review

The validated read-only review is
`2026-10-18T160534Z-dd-sw-engineer-sr-rc11-release-note-as-is.handoff.json`.
It identifies one false current-Unreleased claim: `CHANGELOG.md:30` says
`stream_dict` uses Arrow conversion with a pandas fallback, while the current
authority performs one normalized pandas `DataFrame.to_dict("records")`
conversion. The main-thread grill ruling is recorded in the approved SPEC and
its validated product-engineer handoff.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `CHANGELOG.md` current 0.8.0 stream bullet | claims compatible Arrow conversion with a pandas fallback | 0 | UPDATE | It contradicts `DataGenerator.stream_dict` and the approved rc-10 replacement. Update only this human-facing current-release claim; preserve the Unreleased header and every other byte. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| current `stream_dict` record conversion | `DataGenerator.stream_dict` in `rand_engine/main/data_generator.py` | rc-10 SPEC and `specs/memory/product/generation/data-generator.md` | the false Arrow-eligibility, Arrow-conversion and fallback claim in `CHANGELOG.md:30` |
| current release-note lifecycle | `CHANGELOG.md` 0.8.0 header | approved rc-11 SPEC | none; `Unreleased` remains until publication |

## 2. Decisions and verification

- One prose task updates `CHANGELOG.md:30` only. It makes no runtime, test,
  dependency, CI, benchmark, gate or publication-state change.
- No test is written: the exact release-note wording is not a product contract,
  and a prose-mirroring test would add no behavior protection for this
  reversible, low-impact correction. Semantic comparison with the source,
  rc-10 and the data-generator memory atom is the task evidence.
- The repository's unchanged official verify and merge gates remain the only
  automated protection. They run at their existing merge point; this task does
  not duplicate them or add a gate. Current public evidence and the frozen
  rescore occur only after the reviewed official push, with no score awarded
  beforehand.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `CHANGELOG.md` |

## 3. Requirement trace and post-merge boundary

| acceptance criteria | owner and evidence |
|---|---|
| AC1.1–AC1.3 | Job 1 semantic comparison with `DataGenerator.stream_dict`, approved rc-10 and the data-generator memory atom; diff confirms only the one current bullet changes and the header remains `Unreleased`. |
| AC2.1 | unchanged official merge verification; no task-local duplicate. |
| AC2.2–AC2.3 | main thread after reviewed official merge and feature push: collect current public evidence and commission the unchanged independent frozen rescore. Promotion remains held until its strict condition is met. |
