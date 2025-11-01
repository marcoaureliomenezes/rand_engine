
import uuid
import numpy as np

from typing import List, Any, Dict
from datetime import datetime as dt


class NPCore:


  @classmethod
  def gen_uuid4(cls, size: int, length=None) -> np.ndarray:
    
    lambda_uuid = lambda: str(uuid.uuid4()) if not length else str(uuid.uuid4())
    return np.array([lambda_uuid() for _ in range(size)])
    
  @classmethod
  def gen_booleans(cls, size: int, true_prob=0.5) -> np.ndarray:
    return np.random.choice([True, False], size, p=[true_prob, 1 - true_prob])
  

  @classmethod
  def gen_ints(cls, size: int, min: int, max: int, int_type: str = 'int32') -> np.ndarray:
    allowed_integers = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
    assert int_type in allowed_integers, f"int_type must be one of {allowed_integers}"
    return np.random.randint(min, max + 1, size, dtype=np.int64).astype(int_type)
  

  @classmethod
  def gen_ints_zfilled(cls, size: int, length: int) -> np.ndarray:
    # Use int64 explicitly to handle large numbers on Windows
    max_val = 10**length - 1
    str_arr = np.random.randint(0, max_val + 1, size, dtype=np.int64).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(cls, size: int, min: int, max: int, decimals: int = 2) -> np.ndarray:
    # Use int64 for integer parts to avoid Windows overflow
    sig_part = np.random.randint(min, max, size, dtype=np.int64)
    decimal = np.random.randint(0, 10 ** decimals, size, dtype=np.int64)
    return sig_part + (decimal / 10 ** decimals) if decimals > 0 else sig_part


  @classmethod
  def gen_floats_normal(cls, size: int, mean: int, std: int, decimals: int = 2) -> np.ndarray:
    return np.round(np.random.normal(mean, std, size), decimals)



  @classmethod
  def gen_distincts(cls, size: int, distincts: List[Any]) -> np.ndarray:
    assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts, size)


  @classmethod
  def gen_distincts_prop(cls, size: int, distincts: Dict[str, int]) -> np.ndarray:
    distincts_prop = [ key for key, value in distincts.items() for i in range(value) ]
    #assert len(list(set([type(x) for x in distincts]))) == 1
    return np.random.choice(distincts_prop, size)
  

  @classmethod
  def gen_unix_timestamps(cls, size: int, start: str, end: str, date_format: str) -> np.ndarray:
    dt_start, dt_end = dt.strptime(start, date_format), dt.strptime(end, date_format)
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = int(dt_start.timestamp()), int(dt_end.timestamp())
    # Use int64 to handle large Unix timestamps on Windows
    int_array = np.random.randint(timestamp_start, timestamp_end, size, dtype=np.int64)
    return int_array
  

  @classmethod
  def gen_dates(cls, size: int, start: str, end: str, date_format: str) -> np.ndarray:
    """
    Generate random dates as formatted strings.
    
    Args:
        size: Number of dates to generate
        start: Start date string
        end: End date string
        format: Date format (e.g., "%Y-%m-%d", "%Y-%m-%d %H:%M:%S")
    
    Returns:
        numpy array of formatted date strings
    """
    timestamp_array = cls.gen_unix_timestamps(size, start, end, date_format)
    # Convert to datetime64 then format as strings
    date_array = np.array([dt.fromtimestamp(ts).strftime(date_format) for ts in timestamp_array])
    return date_array

if __name__ == "__main__":
  
  # test gen_dates
  import time
  start_time = time.time()
  dates = NPCore.gen_dates(10**7, "2020-01-01", "2024-12-31", "%Y-%m-%d")
  #print(f"Generated dates: {dates}")
  print(f"Execution time: {time.time() - start_time} seconds")