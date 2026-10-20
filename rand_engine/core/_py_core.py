import itertools
import time
from typing import Dict, List, Any
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
from rand_engine.core._np_core import NPCore

def _as_text(a):
  if isinstance(a, (pa.Array, pa.ChunkedArray, pa.Scalar)): return a
  a = np.asarray(a)
  if a.dtype.kind in "iu" and a.size and int(a.max()) - int(a.min()) < 10**6:
    lo = int(a.min())
    return pa.array([str(i) for i in range(lo, int(a.max()) + 1)]).take(pa.array(a - lo))
  return pa.array(a.astype(str), pa.string())


def _level_columns(rows, size, rng):
  idx = rng.integers(0, len(rows), size)
  cols = []
  for pool in zip(*rows):
    if all(isinstance(x, str) for x in pool): cols.append(pa.array(pool, pa.string()).take(pa.array(idx)))
    else: cols.append(np.fromiter(pool, object, len(pool))[idx].tolist())
  return cols


class PyCore:


  @classmethod
  def gen_complex_distincts(cls, size: int, pattern="x.x.x-x", replacement="x", templates=None, *, rng: np.random.Generator) -> pa.Array | pa.ChunkedArray | np.ndarray:
    """Fills each `replacement` of `pattern` with its template's draw, in pattern order; returns Arrow text (a lone part is returned as drawn)."""
    if not templates: return pa.repeat(pattern, size)
    assert pattern.count(replacement) == len(templates)
    parts, lit, counter = [], "", 0
    for ch in pattern:
      if ch != replacement: lit += ch; continue
      if lit: parts.append(pa.scalar(lit)); lit = ""
      method = templates[counter]["method"]
      parts.append((METHODS[method] if isinstance(method, str) else method)(size, rng=rng, **templates[counter]["kwargs"]))
      counter += 1
    if lit: parts.append(pa.scalar(lit))
    if len(parts) == 1: return parts[0]
    return pc.binary_join_element_wise(*[_as_text(p) for p in parts], "")


  @classmethod  
  def gen_distincts_untyped(cls, size: int, distinct: List[Any], *, rng: np.random.Generator) -> List[Any]:
    return list(map(lambda x: distinct[x], rng.integers(0, len(distinct), size)))
  

  @classmethod
  def gen_distincts_map(cls, size: int, distincts: Dict[str, List[Any]], *, rng: np.random.Generator) -> list:
    """Draws rows of (category, value); returns one column per level."""
    assert len(list(set([type(x) for x in distincts]))) == 1
    return _level_columns([(k, v) for k, values in distincts.items() for v in values], size, rng)


  @classmethod
  def gen_distincts_multi_map(cls, size: int, distincts: Dict[str, List[Any]], *, rng: np.random.Generator) -> list:
    """Draws rows of (category, *levels); returns one column per level."""
    return _level_columns([t for k, v in distincts.items() for t in itertools.product([k], *v)], size, rng)

  @classmethod
  def gen_distincts_map_prop(cls, size: int, distincts: Dict[str, List[Any]], *, rng: np.random.Generator) -> list:
    """Draws (category, value) rows, each value repeated by its weight; returns one column per level."""
    return _level_columns([
      (category, value)
      for category, value_weight_pairs in distincts.items()
      for value, weight in value_weight_pairs
      for _ in range(weight)
    ], size, rng)



# the NumPy engine's one method map: DataGenerator columns and complex_distincts templates
METHODS = {
  "integers": NPCore.gen_ints,
  "int_zfilled": NPCore.gen_ints_zfilled,
  "floats": NPCore.gen_floats,
  "floats_normal": NPCore.gen_floats_normal,
  "exponential": NPCore.gen_exponential,
  "lognormal": NPCore.gen_lognormal,
  "poisson": NPCore.gen_poisson,
  "zipf": NPCore.gen_zipf,
  "constant": NPCore.gen_constant,
  "distincts": NPCore.gen_distincts,
  "distincts_prop": NPCore.gen_distincts_prop,
  "unix_timestamps": NPCore.gen_unix_timestamps,
  "uuid4": NPCore.gen_uuid4,
  "booleans": NPCore.gen_booleans,
  "dates": NPCore.gen_dates,
  "distincts_map": PyCore.gen_distincts_map,
  "distincts_multi_map": PyCore.gen_distincts_multi_map,
  "distincts_map_prop": PyCore.gen_distincts_map_prop,
  "complex_distincts": PyCore.gen_complex_distincts,
}


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
