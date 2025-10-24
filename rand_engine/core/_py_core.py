import itertools
import time
from typing import Dict, List, Any
import numpy as np
from functools import reduce
from rand_engine.integrations._duckdb_handler import DuckDBHandler

class PyCore:


  @classmethod
  def gen_complex_distincts(cls, size: int, pattern="x.x.x-x", replacement="x", templates=None):
    if templates is None:
      templates = []
    from rand_engine.core._np_core import NPCore
    
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


  @classmethod  
  def gen_distincts_untyped(cls, size: int, distinct: List[Any]) -> List[Any]:
    return list(map(lambda x: distinct[x], np.random.randint(0, len(distinct), size)))
  

  @classmethod
  def gen_distincts_map(cls, size: int, distincts: Dict[str, List[Any]]) -> np.ndarray:
    distincts_map = [(i, j) for j in distincts for i in distincts[j]]
    assert len(list(set([type(x) for x in distincts]))) == 1
    return cls.gen_distincts_untyped(size, distincts_map)


  @classmethod
  def gen_distincts_multi_map(cls, size: int, distincts: Dict[str, List[Any]]) -> np.ndarray:
    combinations = [list(itertools.product([k], *v)) for k, v in distincts.items()]
    combinations = [[[i for i in tupla] for tupla in sublist] for sublist in combinations]
    distincts = [i for sublist in combinations for i in sublist]
    return cls.gen_distincts_untyped(size, distincts)

  @classmethod
  def gen_distincts_map_prop(cls, size: int, distincts: Dict[str, List[Any]]) -> np.ndarray:
    distincts_map_prop = [
      (category, value)
      for category, value_weight_pairs in distincts.items()
      for value, weight in value_weight_pairs
      for _ in range(weight)
    ]
    return cls.gen_distincts_untyped(size, distincts_map_prop)




# def test_handle_distincts_lvl_5():
#     distincts = {
#         "PF": [{"premium": ["platinum", "black, gold"]}, {"standard": ["simples"]}],
#         "PJ": [{"premium": ["platinum", "black, gold"]}, {"standard": ["simples"]}]
#     }
#     result = DistinctsUtils.handle_distincts_lvl_5(distincts, sep=";")
#     assert result == ['PF;premium;platinum', 'PF;premium;black, gold', 'PF;standard;simples', 'PJ;premium;platinum', 'PJ;premium;black, gold', 'PJ;standard;simples']


if __name__ == "__main__":
  pass

  # @classmethod
  # def gen_timestamps(cls, size: int, start: str, end: str, format: str) -> np.ndarray:
  #   """
  #   This method generates an array of random timestamps.
  #   :param size: int: Number of elements to be generated.
  #   :param start: str: Start date of the generated timestamps.
  #   :param end: str: End date of the generated timestamps.
  #   :param format: str: Format of the input dates.
  #   :return: np.ndarray: Array of random timestamps."""
  #   date_array = cls.gen_unix_timestamps(size, start, end, format).astype('datetime64[s]')
  #   return date_array
  
  
  # @classmethod
  # def gen_datetimes(cls, size: int, start: str, end: str, format_in: str, format_out: str):
  #   timestamp_array = cls.gen_unix_timestamps(size, start, end, format_in)
  #   vectorized_func = np.vectorize(lambda x: dt.fromtimestamp(x).strftime(format_out))
  #   return vectorized_func(timestamp_array)
