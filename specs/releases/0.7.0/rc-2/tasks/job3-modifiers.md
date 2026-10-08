# Job 3 — DataFrame modifiers and RNG ordering

**Status:** Approved

## Stage J3.S1 — RED

- Contract: exit modifier/stream/benchmark tests fail by assertion under strict xfail markers; envelope `tests/test_2_data_generator.py tests/test_6_stream_objects.py tests/test_benchmarks.py`; ACs AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC9.1, AC9.3.
- J3.S1.T1 — modifier pipeline/dtype RED · AC3.1–AC3.3, AC3.5, AC4.1–AC4.3, AC7.2–AC7.3, AC9.1, AC9.3 · `W:` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · final masks/values, order, null-wins, dtype, row-count refusal and zero-draw literals.
- J3.S1.T2 — stream null normalization RED · AC3.4 · `W:` `tests/test_6_stream_objects.py` · owner `tests/test_6_stream_objects.py` · every pandas missing sentinel becomes Python `None` without changing throughput semantics.
- J3.S1.T3 — modifier benchmark contract RED · AC4.4 · `W:` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · inventory/comparison rows for null and anomaly modifiers at official light/CI sizes.

## Stage J3.S2 — rebuild row-batch pipeline

- Contract: exit owner tests GREEN by marker deletion only and benchmark rows locally enumerable; envelope `rand_engine/main/** rand_engine/utils/stream_handler.py benchmarks/speed.py tests/test_2_data_generator.py tests/test_6_stream_objects.py tests/test_benchmarks.py`; ACs AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3.
- J3.S2.T1 — one generation/transform/modifier pipeline · AC3.1–AC3.3, AC3.5, AC4.1–AC4.3, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3 · `W:` `rand_engine/main/data_generator.py` `rand_engine/main/_rand_generator.py` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · preserve one RNG, reject row-count changes, anomaly then dtype-specific null, delete dead branches/imports.
- J3.S2.T2 — normalize streamed nulls · AC3.4 · `W:` `rand_engine/utils/stream_handler.py` `tests/test_6_stream_objects.py` · owner `tests/test_6_stream_objects.py`.
- J3.S2.T3 — add modifier benchmark rows · AC4.4 · `W:` `benchmarks/speed.py` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · no local stress execution.
