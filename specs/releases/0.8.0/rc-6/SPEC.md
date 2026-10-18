# SPEC — Release: 0.8.0, candidate 6 (stream benchmark restoration)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand

- Operator authority remains the standing instruction to “work till you finish the
  complete work for rand-engine” so that “all opened work” is completed, followed
  by the latest direction: “aprovado, siga em frente. nos ajude aí”.
- Main-thread ruling: this candidate restores the already approved rc-4 AC4.4
  performance contract after the candidate-head benchmark exposed a narrow
  regression. It adds no product behavior or acceptance threshold and therefore
  needs no new product choice. This SPEC records that ruling; it does not claim the
  operator reviewed this new artifact.
- The failed benchmark belongs to an unmerged candidate integration, so this is
  candidate rework rather than a newly operator-confirmed production bug. No bug
  record is opened.

## Bug window review

Rc-5 resolved no bug record and reports zero open bugs. Its changes select Java 17
in five CI jobs and close two SQLite test-fixture connections; they do not touch
stream conversion or add a `fix_sha`. The prior candidate's bug-window conclusion
therefore remains unchanged: there is no fix to classify KEEP or REBUILD and no
bug-window implementation work in rc-6.

## 1. Problem

Rc-4 made eligible `stream_dict` batches use Arrow while preserving the public
record contract and required the existing same-runner benchmark to stay within its
ratio limit. On PR #47, benchmark run 39081652038 measured the one-million-row
`stream_dict` sink at 8.478 s against a 6.484 s base, ratio 1.31, above the existing
1.3 limit.

Read-only diagnosis found avoidable allocation inside the object-column eligibility
check: it builds a list of present values, then a type set, then scans integers
again. A one-pass inspection of the existing NumPy view removes that duplicate work
without changing which batches use Arrow or any returned record.

## 2. Measurable goals

- Preserve every current `stream_dict` value, Python type, label, order,
  normalization step, Arrow call and fallback decision under the unchanged stream
  contract tests.
- Make the candidate-head same-runner benchmark pass its existing `stream_dict`
  ratio limit of at most 1.3 and publish the row through the existing workflow.

## 3. Non-goals

- New stream behavior, public API, flag, dependency, test case, benchmark, workflow
  or performance threshold.
- Changing `StreamHandler`, any protected `gen_*` body, stream cadence, throughput
  control or timestamp behavior.
- Routing an eligible batch to pandas, widening Arrow eligibility, using
  `safe=False`, changing the Arrow call or swallowing additional exceptions.
- Any outreach, publication, platform or SQLite work from adjacent candidates.

## 4. Requirements

### FR1 — Restore the approved Arrow stream performance contract

- AC1.1 (integration): the unchanged 22 stream-object contract tests pass without
  weakening, deleting or skipping an assertion. Exact output values, Python types,
  string labels, record order, signed-64-bit object-integer eligibility, current
  normalization, the existing
  `Table.from_pandas(..., preserve_index=False).to_pylist()` call, narrow Arrow
  fallback exceptions and pandas fallback partitions remain identical.
- AC1.2 (no new test; the existing PR same-runner A/B benchmark is the contract
  measurement): the candidate-head benchmark completes successfully and reports a
  comparable one-million-row `stream_dict` ratio no greater than its unchanged 1.3
  limit. The benchmark workflow, script, workload and threshold remain untouched.

## 5. Replaces

- The object-column eligibility helper's present-value list, type-set construction
  and separate integer rescan are replaced by one pass over
  `values.to_numpy(copy=False)`. No observable stream behavior is replaced.

## 6. Constraints and risks

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — existing-contract restoration | one internal eligibility-helper allocation correction | AC1.1–AC1.2 |

| risk | control |
|---|---|
| a faster guard changes Arrow eligibility | retain every exact-type, homogeneous-object, allowed-type and signed-64-bit decision; prove parity through the unchanged 22 tests |
| a local timing improvement does not restore CI | acceptance remains the existing same-runner candidate-head benchmark, not a new local threshold |
| optimization spreads into protected or public surfaces | the production write set is only `rand_engine/main/data_generator.py`; no `StreamHandler`, `gen_*`, test, dependency or workflow edit |

## 7. Open questions

none.
