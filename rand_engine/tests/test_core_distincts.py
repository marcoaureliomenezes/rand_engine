import time


from rand_engine.bulk.core_numeric import (
    gen_distincts_untyped,
    gen_distincts_typed,
    gen_distincts_untyped_baseline,
    gen_distincts_typed_baseline
)

from rand_engine.tests.fixtures.template_1 import (
    get_default_benchmark_distinct_parms_untyped as untyped_distincts_default,
    get_default_benchmark_distinct_parms_typed_str as typed_distincts_default

)

def test_gen_distincts_untyped(untyped_distincts_default):
  start_time = time.time()
  gen_distincts_untyped_baseline(**untyped_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Baseline: {elapsed_time}")


def test_gen_distincts_untyped_baseline(untyped_distincts_default):
  start_time = time.time()
  gen_distincts_untyped(**untyped_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Benchmark: {elapsed_time}")


def test_gen_distincts_typed(typed_distincts_default):
  start_time = time.time()
  gen_distincts_typed_baseline(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Baseline: {elapsed_time}")


def test_gen_distincts_typed_baseline(typed_distincts_default):
  start_time = time.time()
  gen_distincts_typed(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Benchmark: {elapsed_time}")