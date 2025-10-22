
from typing import List, Any, Dict
import numpy as np
from datetime import datetime as dt


class NPCore:
    

  @classmethod
  def gen_bools(cls, size: int, true_prob=0.5) -> np.ndarray:
    return np.random.choice([True, False], size, p=[true_prob, 1 - true_prob])
  
  @classmethod
  def gen_ints(cls, size: int, min: int, max: int, int_type: str = 'int32') -> np.ndarray:
    # Use int64 explicitly to avoid Windows int32 overflow issues
    return np.random.randint(min, max + 1, size, dtype=np.int64).astype(int_type)


  @classmethod
  def gen_ints_zfilled(cls, size: int, length: int) -> np.ndarray:
    # Use int64 explicitly to handle large numbers on Windows
    max_val = 10**length - 1
    str_arr = np.random.randint(0, max_val + 1, size, dtype=np.int64).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(cls, size: int, min: int, max: int, round: int = 2) -> np.ndarray:
    # Use int64 for integer parts to avoid Windows overflow
    sig_part = np.random.randint(min, max, size, dtype=np.int64)
    decimal = np.random.randint(0, 10 ** round, size, dtype=np.int64)
    return sig_part + (decimal / 10 ** round) if round > 0 else sig_part


  @classmethod
  def gen_floats_normal(cls, size: int, mean: int, std: int, round: int = 2) -> np.ndarray:
    return np.round(np.random.normal(mean, std, size), round)
  

  @classmethod
  def gen_unix_timestamps(cls, size: int, start: str, end: str, format: str) -> np.ndarray:
    dt_start, dt_end = dt.strptime(start, format), dt.strptime(end, format)
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = int(dt_start.timestamp()), int(dt_end.timestamp())
    # Use int64 to handle large Unix timestamps on Windows
    int_array = np.random.randint(timestamp_start, timestamp_end, size, dtype=np.int64)
    return int_array
  

  @classmethod
  def gen_unique_identifiers(cls, size: int, strategy="zint", length=12) -> np.ndarray:
    import uuid
    if strategy == "uuid4":
      return np.array([str(uuid.uuid4()) for _ in range(size)])
    elif strategy == "uuid1":
      return np.array([str(uuid.uuid1()) for _ in range(size)])
    elif strategy == "zint":
      return cls.gen_ints_zfilled(size, length)
    else:
      raise ValueError("Method not recognized. Use 'uuid4', 'uuid1', 'shortuuid' or 'random'.")


  @classmethod
  def gen_distincts(cls, size: int, distincts: List[Any]) -> np.ndarray:

    assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts, size)


  @classmethod
  def gen_distincts_prop(cls, size: int, distincts: Dict[str, int]) -> np.ndarray:
    distincts_prop = [ key for key, value in distincts.items() for i in range(value) ]
    #assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts_prop, size)
  


    
if __name__ == "__main__":
  
  # distinct_prop = {"A": 1, "B": 2, "C": 7}
  # result = NPCore.gen_distincts_prop(10, distinct_prop)
  # print(result)

  distincts_map = {"smartphone": [2,1], "desktop": [2, 1]}
  result = NPCore.gen_distincts_map(10, distincts_map)
  print(result)