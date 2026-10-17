# Job 4 — Arrow record-stream conversion

**Wave:** 2
**Waits on:** —
**W:** `tests/test_6_stream_objects.py`, `rand_engine/main/data_generator.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC4.1–AC4.3 | `tests/test_6_stream_objects.py` | RED integration tests for Arrow-compatible records after current normalization, exact values/types including nullable values, dates, transformed values and timestamps; a real mixed-object representation fallback; no fallback for unrelated errors; and existing stream cadence/order continuity. |
| J4.T2 | sr | AC4.1–AC4.3 | `rand_engine/main/data_generator.py` | Convert compatible normalized batches via Arrow `from_pandas(..., preserve_index=False).to_pylist()` and catch only Arrow representation failures to retain pandas records. Keep the protected StreamHandler and all throughput behavior untouched. |

`J4.T2` may not edit tests. AC4.4 is validated by the existing candidate-head
benchmark job and adds no task gate or benchmark code.
