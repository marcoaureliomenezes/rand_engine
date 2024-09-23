import time
import random
import numpy as np
from datetime import datetime as dt, timedelta
from typing import List, Any, Generator



def time_measure(method):
  def wrapper(*args, **kwargs):
    start = time.time()
    res = method(*args, **kwargs)
    time_elapsed= time.time() - start
    print(f"Time_elapsed  for method {method.__name__}: {time_elapsed}")
    return res
  return wrapper


class DistinctsGenerator:
    
  @classmethod
  def gen_distincts_untyped_baseline_1(size: int, distinct: List[Any]) -> Generator:
    return (random.choice(distinct) for i in range(size))
  
  @classmethod
  def gen_distincts_untyped_baseline_2(size: int, distinct: List[Any]) -> List[Any]:
    return map(lambda x: distinct[x], [random.randint(0, len(distinct)-1) for _ in range(size)])
  
  
  @classmethod
  def gen_distincts_typed_baseline_1(size: int, distinct: List[Any]) -> List[Any]:
    return [distinct[i] for i in np.random.randint(0, len(distinct), size)]
  

  @classmethod
  def gen_distincts_typed_baseline_2(size: int, distinct: List[Any]) -> np.ndarray:
    return np.vectorize(lambda x: random.choice(distinct))(np.arange(size))
  
  
  @classmethod
  def gen_distincts_typed_baseline_3(size: int, distinct: List[Any]) -> np.ndarray:
    return np.vectorize(lambda x: distinct[x])(np.random.randint(0, len(distinct), size))
  


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
  
  
if __name__ == '__main__':

  from rand_engine.bulk.core_datetime import CoreDatetime
  from rand_engine.bulk.core_numeric import CoreNumeric


  parms_numeric_int = {"size": 10**7, "min": 0, "max": 10**6}
  parms_numeric_zfilled = {"size": 10**7, "length": 10}
  parms_numeric_float = {"size": 10**7, "min": 0.0, "max": 10**6}
  parms_numeric_float_normal = {"size": 10**7, "mean": 0.0, "std": 10**6}
  parms_datetime = {"size": 10**7, "start": "01-01-1970", "end": "01-01-2021", "format": "%d-%m-%Y"}

  numeric_benchmark = NumericBenchmark(CoreNumeric)
  numeric_benchmark.gen_ints(**parms_numeric_int)
  numeric_benchmark.gen_ints_zfilled(**parms_numeric_zfilled)
  numeric_benchmark.gen_floats(**parms_numeric_int)
  numeric_benchmark.gen_floats_normal(**parms_numeric_float_normal)

  datetime_benchmark = DatetimeBenchmark(CoreDatetime)
  datetime_benchmark.gen_unix_timestamps(**parms_datetime)
  datetime_benchmark.gen_timestamps(**parms_datetime)