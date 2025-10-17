
from typing import List, Any
import numpy as np
from datetime import datetime as dt
from functools import reduce



class NPCore:
    
  @classmethod
  def gen_distincts(self, size: int, distincts: List[Any]) -> np.ndarray:
    assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts, size)

  @classmethod
  def gen_bools(self, size: int, true_prob=0.5) -> np.ndarray:
    return np.random.choice([True, False], size, p=[true_prob, 1 - true_prob])
  
  @classmethod
  def gen_ints(self, size: int, min: int, max: int) -> np.ndarray:
    return np.random.randint(min, max + 1, size)


  @classmethod
  def gen_ints_zfilled(self, size: int, length: int) -> np.ndarray:
    str_arr = np.random.randint(0, 10**length, size).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(self, size: int, min: int, max: int, round: int = 2) -> np.ndarray:
    sig_part = np.random.randint(min, max, size)
    decimal = np.random.randint(0, 10 ** round, size)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


  @classmethod
  def gen_floats_normal(self, size: int, mean: int, std: int, round: int = 2) -> np.ndarray:
    return np.round(np.random.normal(mean, std, size), round)
  

  @classmethod
  def gen_unix_timestamps(self, size: int, start: str, end: str, format: str) -> np.ndarray:
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = dt_start.timestamp(), dt_end.timestamp()
    int_array = np.random.randint(timestamp_start, timestamp_end, size)
    return int_array
  

  @classmethod
  def gen_unique_identifiers(self, size: int, strategy="zint", length=12) -> np.ndarray:
    import uuid
    if strategy == "uuid4":
      return np.array([str(uuid.uuid4()) for _ in range(size)])
    elif strategy == "uuid1":
      return np.array([str(uuid.uuid1()) for _ in range(size)])
    elif strategy == "zint":
      return self.gen_ints_zfilled(size, length)
    else:
      raise ValueError("Method not recognized. Use 'uuid4', 'uuid1', 'shortuuid' or 'random'.")


