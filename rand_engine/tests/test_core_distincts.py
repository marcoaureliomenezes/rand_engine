import time


from rand_engine.bulk.core_distincts import CoreDistincts

from rand_engine.tests.fixtures.template_1 import (
    get_default_benchmark_distinct_parms_untyped as untyped_distincts_default,
    get_default_benchmark_distinct_parms_typed_str as typed_distincts_default

)

def test_gen_distincts_untyped(untyped_distincts_default):
  result = CoreDistincts.gen_distincts_untyped(**untyped_distincts_default)
  print(result)
  

def test_gen_distincts_typed(typed_distincts_default):
  result = CoreDistincts.gen_distincts_typed(**typed_distincts_default)
  print(result)

def test_gen_complex_distincts():
  pass


