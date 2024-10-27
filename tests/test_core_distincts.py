from rand_engine.core.distinct_core import DistinctCore

from tests.fixtures.fixtures_core import (
    get_default_benchmark_distinct_parms_untyped as untyped_distincts_default,
    get_default_benchmark_distinct_parms_typed_str as typed_distincts_default

)

def test_gen_distincts_untyped(untyped_distincts_default):
  result = DistinctCore.gen_distincts_untyped(**untyped_distincts_default)
  print(result)
  

def test_gen_distincts_typed(typed_distincts_default):
  result = DistinctCore.gen_distincts_typed(**typed_distincts_default)
  print(result)

def test_gen_complex_distincts():
  pass


