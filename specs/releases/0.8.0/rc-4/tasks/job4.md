# Job 4 — Arrow record-stream conversion

**Wave:** 2
**Waits on:** —
**W:** `tests/test_6_stream_objects.py`, `rand_engine/main/data_generator.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC4.1–AC4.3 | `tests/test_6_stream_objects.py` | RED integration tests for Arrow-compatible records after current normalization, exact values/types including nullable values, dates, transformed safe scalar values and timestamps; benchmark-like ordinary string records remain eligible. Separate tuple, NumPy-array, object-subclass and mixed-object partitions prove pandas fallback preserves current Python types/values; cover narrow Arrow-error fallback, unrelated-error propagation, and existing stream cadence/order continuity. |
| J4.T2 | sr | AC4.1–AC4.3 | `rand_engine/main/data_generator.py` | Add one cheap object-cell lossless-type eligibility decision, then convert eligible normalized batches through Arrow `from_pandas(..., preserve_index=False).to_pylist()`. Send unproved object representations to pandas and catch only Arrow representation errors there; do not compare two complete conversions. Keep the protected StreamHandler and all throughput behavior untouched. |

`J4.T2` may not edit tests. AC4.4 is validated by the existing candidate-head
benchmark job and adds no task gate or benchmark code.
