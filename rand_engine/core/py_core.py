from typing import List, Any
import numpy as np
from datetime import datetime as dt
from functools import reduce


class PyCore:

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


  @classmethod
  def gen_distincts_untyped(self, size: int, distinct: List[Any]) -> List[Any]:
    return list(map(lambda x: distinct[x], np.random.randint(0, len(distinct), size)))
  

  @classmethod
  def gen_complex_distincts(self, size: int, pattern="x.x.x-x", replacement="x", templates=[]):
    from rand_engine.core.np_core import NPCore
    
    # Mapeamento de strings para métodos
    method_map = {
      "integers": NPCore.gen_ints,
      "int_zfilled": NPCore.gen_ints_zfilled,
      "floats": NPCore.gen_floats,
      "floats_normal": NPCore.gen_floats_normal,
      "distincts": NPCore.gen_distincts,
      "unix_timestamps": NPCore.gen_unix_timestamps,
      "unique_ids": NPCore.gen_unique_identifiers,
      "booleans": NPCore.gen_bools,
    }
    
    assert pattern.count(replacement) == len(templates)
    list_of_lists, counter = [], 0
    for replacer_cursor in range(len(pattern)):
      if pattern[replacer_cursor] == replacement:
        method = templates[counter]["method"]
        # Se for string, mapeia para o callable
        if isinstance(method, str):
          method = method_map[method]
        list_of_lists.append(method(size, **templates[counter]["parms"]))
        counter += 1
      else:
        list_of_lists.append(np.array([pattern[replacer_cursor] for i in range(size)]))
    return reduce(lambda a, b: a.astype('str') + b.astype('str'), list_of_lists)