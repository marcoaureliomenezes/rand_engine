import time


from rand_engine.bulk.core_distincts import CoreDistincts

from rand_engine.tests.fixtures.template_1 import (
    get_default_benchmark_distinct_parms_untyped as untyped_distincts_default,
    get_default_benchmark_distinct_parms_typed_str as typed_distincts_default

)

def test_gen_distincts_untyped(untyped_distincts_default):
  start_time = time.time()
  list(CoreDistincts.gen_distincts_untyped(**untyped_distincts_default))
  elapsed_time = time.time() - start_time
  print(f"\nElapsed time gen_distincts_untyped: {elapsed_time}")


def test_gen_distincts_untyped_baseline_1(untyped_distincts_default):
  start_time = time.time()
  list(CoreDistincts.gen_distincts_untyped_baseline_1(**untyped_distincts_default))
  elapsed_time = time.time() - start_time
  print(f"Elapsed time gen_distincts_untyped_baseline_1: {elapsed_time}")


def test_gen_distincts_untyped_baseline_2(untyped_distincts_default):
  start_time = time.time()
  list(CoreDistincts.gen_distincts_untyped_baseline_2(**untyped_distincts_default))
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_untyped_baseline_2: {elapsed_time}")




def test_gen_distincts_typed(typed_distincts_default):
  start_time = time.time()
  list(CoreDistincts.gen_distincts_typed(**typed_distincts_default))
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_typed: {elapsed_time}")


def test_gen_distincts_typed(typed_distincts_default):
  start_time = time.time()
  CoreDistincts.gen_distincts_typed(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_typed: {elapsed_time}")


def test_gen_distincts_typed_baseline_1(typed_distincts_default):
  start_time = time.time()
  CoreDistincts.gen_distincts_typed_baseline_1(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_typed_baseline_1: {elapsed_time}")

def test_gen_distincts_typed_baseline_2(typed_distincts_default):
  start_time = time.time()
  CoreDistincts.gen_distincts_typed_baseline_2(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_typed_baseline_2: {elapsed_time}")

def test_gen_distincts_typed_baseline_3(typed_distincts_default):
  start_time = time.time()
  CoreDistincts.gen_distincts_typed_baseline_3(**typed_distincts_default)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time test_gen_distincts_typed_baseline_3: {elapsed_time}")