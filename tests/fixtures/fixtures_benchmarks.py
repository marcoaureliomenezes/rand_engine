import time
import random
import numpy as np
from datetime import datetime as dt, timedelta
from typing import List, Any, Iterator



def time_measure(method):
  def wrapper(*args, **kwargs):
    start = time.time()
    res = method(*args, **kwargs)
    time_elapsed= time.time() - start
    print(f"Time_elapsed  for method {method.__name__}: {time_elapsed}")
    return res
  return wrapper


class DistinctBenchmark:
    
  def __init__(self, core_distinct):
    self.core_distinct = core_distinct


  @time_measure
  def gen_distincts_typed(self, size: int, distinct: List[Any]) -> np.ndarray:
    return self.core_distinct.gen_distincts_typed(size, distinct)
  
  @time_measure
  def gen_distincts_untyped(self, size: int, distinct: List[Any]) -> Iterator:
    return self.core_distinct.gen_distincts_untyped(size, distinct)
  


class NumericBenchmark:

  def __init__(self, core_numeric):
    self.core_numeric = core_numeric

  @time_measure
  def gen_ints(self, size: int, min: int, max: int):
    return self.core_numeric.gen_ints(size, min, max)
  
  @time_measure
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    return self.core_numeric.gen_ints_zfilled(size, length)
  
  @time_measure
  def gen_ints_zfilled_2(self, size: int, length: int) -> np.ndarray:
    return self.core_numeric.gen_ints_zfilled_2(size, length)
  

  @time_measure
  def gen_floats(self, size: int, min: float, max: float):
    return self.core_numeric.gen_floats(size, min, max)
  
  @time_measure
  def gen_floats_normal(self, size: int, mean: float, std: float):
    return self.core_numeric.gen_floats_normal(size, mean, std)


class DatetimeBenchmark:

  def __init__(self, core_datetime):
    self.core_datetime = core_datetime


  @time_measure
  def gen_unix_timestamps(self, size: int, start: str, end: str, format: str):
    return self.core_datetime.gen_unix_timestamps(size, start, end, format)

  @time_measure
  def gen_timestamps(self, size: int, start: str, end: str, format: str):
    return self.core_datetime.gen_timestamps(size, start, end, format)
  
  
class Benchmark:

  def run(self):
    from rand_engine.bulk.core_datetime import CoreDatetime
    from rand_engine.bulk.core_numeric import CoreNumeric
    from rand_engine.bulk.core_distincts import CoreDistincts

    size = 10**7
    parms_numeric_int = {"size": size, "min": 0, "max": 10**6}
    parms_numeric_zfilled = {"size": size, "length": 10}
    parms_numeric_float_normal = {"size": size, "mean": 0.0, "std": 10**6}
    parms_datetime = {"size": size, "start": "01-01-1970", "end": "01-01-2021", "format": "%d-%m-%Y"}
    parms_distinct_typed = {"size": size, "distinct": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
    parms_distinct_untyped = {"size": size, "distinct": [1, 2, "10"]}

    numeric_benchmark = NumericBenchmark(CoreNumeric)
    datetime_benchmark = DatetimeBenchmark(CoreDatetime)
    distinct_benchmark = DistinctBenchmark(CoreDistincts)

    numeric_benchmark.gen_ints(**parms_numeric_int)
    numeric_benchmark.gen_ints_zfilled(**parms_numeric_zfilled)
    numeric_benchmark.gen_floats(**parms_numeric_int)
    numeric_benchmark.gen_floats_normal(**parms_numeric_float_normal)

    datetime_benchmark.gen_unix_timestamps(**parms_datetime)
    datetime_benchmark.gen_timestamps(**parms_datetime)

    distinct_benchmark.gen_distincts_typed(**parms_distinct_typed)
    distinct_benchmark.gen_distincts_untyped(**parms_distinct_untyped)

if __name__ == '__main__':

  #Benchmark().run()
  pass