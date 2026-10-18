# PLAN — Release: 0.8.0, candidate 6 (stream benchmark restoration)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-6/SPEC.md`

## 1. As-is review

Evidence is the pre-SPEC investigation
`2026-10-18T013348Z-dd-sw-engineer-sr-stream-dict-benchmark-investigation.handoff.json`.
The failed candidate-head benchmark is the existing RED evidence: PR #47 run
39081652038 measured `stream_dict` at 8.478 s against 6.484 s base (ratio 1.31,
limit 1.3). The unchanged 22 stream-object contract tests are the behavioral
GREEN evidence; the existing same-runner benchmark is the performance GREEN
evidence. There is no new behavior to specify and no test write.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `rand_engine/main/data_generator.py` `_stream_records_are_arrow_compatible` | validates labels and each column; object columns allocate a present-value list, build a type set, then rescan integer values for signed-64 range | 0 open; candidate-head benchmark regression evidence | UPDATE | one helper already owns Arrow eligibility. One pass over its NumPy view preserves all decisions while deleting temporary collections and the duplicate scan. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| whether a normalized record batch is Arrow-compatible | `rand_engine/main/data_generator.py` `_stream_records_are_arrow_compatible` | `stream_dict`, existing `tests/test_6_stream_objects.py` contract partitions | the helper's present-value list, type set and separate integer rescan |

## 2. Decisions and measured gate cost

- The helper remains the sole Arrow-eligibility authority. It first retains exact
  string-label checking, then for each object column iterates once over
  `values.to_numpy(copy=False)`, ignoring only `None`, requiring one exact type
  from the current allowed set, and range-checking exact `int` values in that
  same pass.
- Extension dtype, NumPy dtype, Arrow conversion, safe default, narrow fallback,
  returned values/types/order, `StreamHandler` and all protected `gen_*` bodies
  remain unchanged.
- No test, workflow, benchmark, dependency or gate changes. The existing job
  merge runs the unchanged `verify:` once; PR CI supplies the benchmark
  measurement. The task does not rerun either as a planning requirement.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `rand_engine/main/data_generator.py` |

## 3. Reconciliation (after Job 1)

**W:** `specs/releases/0.8.0/_RELEASE.json`.

The product engineer records standard closure evidence after the reviewed job
lands. Product memory is reviewed only if the implementation exposes an actual
truth drift; the intended allocation-only correction has none.
