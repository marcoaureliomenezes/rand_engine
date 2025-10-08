
from typing import List, Any
import numpy as np
from datetime import datetime as dt
from functools import reduce



class Core:
    
  @classmethod
  def gen_distincts_typed(self, size: int, distinct: List[Any]) -> np.ndarray:
    assert len(list(set([type(x) for x in distinct]))) == 1
    return np.random.choice(distinct, size)
  

  @classmethod
  def gen_distincts_untyped(self, size: int, distinct: List[Any]) -> List[Any]:
    return list(map(lambda x: distinct[x], np.random.randint(0, len(distinct), size)))
  

  @classmethod
  def gen_complex_distincts(self, size: int, pattern="x.x.x-x", replacement="x", templates=[]):
    assert pattern.count(replacement) == len(templates)
    list_of_lists, counter = [], 0
    for replacer_cursor in range(len(pattern)):
      if pattern[replacer_cursor] == replacement:
        list_of_lists.append(templates[counter]["method"](size, **templates[counter]["parms"]))
        counter += 1
      else:
        list_of_lists.append(np.array([pattern[replacer_cursor] for i in range(size)]))
    return reduce(lambda a, b: a.astype('str') + b.astype('str'), list_of_lists)
  
  
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
  def gen_unique_identifiers(self, size: int, method="uuid4") -> np.ndarray:
    import uuid
    if method == "uuid4":
      return np.array([str(uuid.uuid4()) for _ in range(size)])
    elif method == "uuid1":
      return np.array([str(uuid.uuid1()) for _ in range(size)])
    else:
      raise ValueError("Method not recognized. Use 'uuid4', 'uuid1', 'shortuuid' or 'random'.")
  # @classmethod
  # def gen_timestamps(self, size: int, start: str, end: str, format: str) -> np.ndarray:
  #   """
  #   This method generates an array of random timestamps.
  #   :param size: int: Number of elements to be generated.
  #   :param start: str: Start date of the generated timestamps.
  #   :param end: str: End date of the generated timestamps.
  #   :param format: str: Format of the input dates.
  #   :return: np.ndarray: Array of random timestamps."""
  #   date_array = self.gen_unix_timestamps(size, start, end, format).astype('datetime64[s]')
  #   return date_array
  
  
  # @classmethod
  # def gen_datetimes(self, size: int, start: str, end: str, format_in: str, format_out: str):
  #   timestamp_array = self.gen_unix_timestamps(size, start, end, format_in)
  #   vectorized_func = np.vectorize(lambda x: dt.fromtimestamp(x).strftime(format_out))
  #   return vectorized_func(timestamp_array)