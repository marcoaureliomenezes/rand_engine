# Job 3 — DataFrame modifiers and RNG ordering

**Status:** Approved
**done:** true

## Stage J3.S1 — RED

- Contract: exit modifier/stream/benchmark tests fail by assertion under strict xfail markers; envelope `tests/test_2_data_generator.py tests/test_6_stream_objects.py tests/test_benchmarks.py`; ACs AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC9.1, AC9.3.
- J3.S1.T1 — modifier pipeline/dtype RED · AC3.1–AC3.3, AC3.5, AC4.1–AC4.3, AC7.2–AC7.3, AC9.1, AC9.3 · `W:` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · final masks/values, order, null-wins, dtype, row-count refusal and zero-draw literals.
- J3.S1.T2 — stream null normalization RED · AC3.4 · `W:` `tests/test_6_stream_objects.py` · owner `tests/test_6_stream_objects.py` · every pandas missing sentinel becomes Python `None` without changing throughput semantics.
- J3.S1.T3 — modifier benchmark contract RED · AC4.4 · `W:` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · inventory/comparison rows for null and anomaly modifiers at official light/CI sizes.

## Stage J3.S2 — rebuild row-batch pipeline

- Contract: exit owner tests GREEN by marker deletion only and benchmark rows locally enumerable; terminal job close is deferred to J3.S4.T2; envelope `rand_engine/main/** rand_engine/utils/stream_handler.py benchmarks/speed.py tests/test_2_data_generator.py tests/test_6_stream_objects.py tests/test_benchmarks.py specs/releases/0.7.0/rc-2/tasks/job3-modifiers.md`; ACs AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3.
- J3.S2.T1 — one generation/transform/modifier pipeline · AC3.1–AC3.3, AC3.5, AC4.1–AC4.3, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3 · `W:` `rand_engine/main/data_generator.py` `rand_engine/main/_rand_generator.py` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · preserve one RNG, reject row-count changes, anomaly then dtype-specific null, delete dead branches/imports.
- J3.S2.T2 — normalize streamed nulls · AC3.4 · `W:` `rand_engine/utils/stream_handler.py` `tests/test_6_stream_objects.py` · owner `tests/test_6_stream_objects.py`.
- J3.S2.T3 — add modifier benchmark rows · AC4.4 · `W:` `benchmarks/speed.py` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · no local stress execution.

## Stage J3.S3 — modifier target/null representation RED

- Contract: exit `tests/test_2_data_generator.py` fails by final assertions under strict xfail markers for the existing ordinary-column alias and object/string null contracts; envelope `tests/test_2_data_generator.py`; ACs AC3.3, AC4.1–AC4.3, AC9.1, AC9.3.
- J3.S3.T1 — alias modifier and object/string null RED · AC3.3, AC4.1–AC4.3, AC9.1, AC9.3 · `W:` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · require modifiers on a valid single `cols` alias to consume the actual generated column, and require nulls on object or transformed pandas string Series to be literal Python `None` with object dtype; preserve the legacy embedded-transformer mapping and every prior assertion.

## Stage J3.S4 — modifier target/null correction and close

- Contract: exit `tests/test_2_data_generator.py` GREEN by deletion of only the J3.S3 marker lines, with one existing-column resolver used by compatibility, anomaly and null handling and no duplicate pipeline; after the task gate and required review checkpoint are green, write this job file's terminal `done` exactly once; envelope `rand_engine/main/_rand_generator.py tests/test_2_data_generator.py specs/releases/0.7.0/rc-2/tasks/job3-modifiers.md`; ACs AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3.
- J3.S4.T1 — resolve modifier output names and Python-None object nulls · AC3.3, AC4.1–AC4.3, AC9.1, AC9.3 · `W:` `rand_engine/main/_rand_generator.py` `tests/test_2_data_generator.py` · owner `tests/test_2_data_generator.py` · resolve the existing spec key or sole `cols` alias once and reuse it for compatibility, anomaly and null operations; normalize object and transformed pandas string null assignment to object dtype with literal `None`, without a test-specific branch, second resolver, duplicate pipeline, new declaration or hidden limit.
- J3.S4.T2 — close modifier job · AC3.1–AC3.5, AC4.1–AC4.4, AC7.2–AC7.3, AC8.7, AC9.1, AC9.3 · `W:` `specs/releases/0.7.0/rc-2/tasks/job3-modifiers.md` · owner `tests/test_2_data_generator.py` · after J3.S3, J3.S4.T1 and the complete job contract are green, write terminal `done` exactly once and commit `chore(tasks): done job3-modifiers`.
