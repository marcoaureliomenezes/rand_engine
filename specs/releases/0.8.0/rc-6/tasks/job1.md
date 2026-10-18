# Job 1 — Restore the Arrow stream benchmark

**Wave:** 1
**Waits on:** —
**W:** `rand_engine/main/data_generator.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.2 | `rand_engine/main/data_generator.py` | Update only `_stream_records_are_arrow_compatible`: replace its object-column present-value list, type-set construction and separate integer rescan with one pass over `values.to_numpy(copy=False)`. Preserve exact string labels; `None` handling; exact allowed types; homogeneous-object requirement; signed-64 exact-`int` range; every non-object dtype decision; and the unchanged Arrow call, fallback exceptions, records, types and order. The existing failed benchmark row is RED; the unchanged 22 stream-object tests and existing PR benchmark are GREEN. |

No test file changes: this is an allocation-only UPDATE whose existing contract
partitions already prove every retained semantic decision.
