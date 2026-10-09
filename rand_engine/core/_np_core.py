
import uuid
import re
import numpy as np

from typing import List, Any, Dict
from datetime import datetime as dt, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR


DATE_DIRECTIVES = ("%Y", "%m", "%d", "%H", "%M", "%S", "%f")
DATE_SPLIT = re.compile(f"({'|'.join(DATE_DIRECTIVES)})")


def _parse_date_bound(value: str, date_format: str) -> dt:
  try:
    return dt.strptime(value, date_format)
  except ValueError:
    return dt.strptime(value, "%Y-%m-%d")


def _shift_decimal(value: Decimal, places: int) -> Decimal:
  sign, digits, exponent = value.as_tuple()
  return Decimal((sign, digits, exponent + places))


def float_lattice_bounds(minimum: int | float, maximum: int | float, decimals: int) -> tuple[int, int, Decimal]:
  """Return inclusive integer endpoints and exact scale for a decimal lattice."""
  if isinstance(decimals, bool) or not isinstance(decimals, int):
    raise ValueError("decimals must be an integer")
  try:
    low, high = Decimal(str(minimum)), Decimal(str(maximum))
  except (InvalidOperation, ValueError) as error:
    raise ValueError("float bounds must be finite numbers") from error
  if not low.is_finite() or not high.is_finite():
    raise ValueError("float bounds must be finite numbers")
  lower = int(_shift_decimal(low, decimals).to_integral_value(rounding=ROUND_CEILING))
  upper = int(_shift_decimal(high, decimals).to_integral_value(rounding=ROUND_FLOOR))
  if lower > upper:
    raise ValueError("float bounds contain no representable value at the requested decimals")
  return lower, upper, Decimal((0, (1,), decimals))


def poisson_lam_supported(lam: int | float) -> bool:
  """Whether NumPy can produce its int64 Poisson result for this lambda."""
  try:
    np.random.default_rng(0).poisson(lam=lam, size=0)
  except (OverflowError, ValueError):
    return False
  return True


def _unbiased_python_ints(rng: np.random.Generator, size: int, lower: int, upper: int) -> list[int]:
  width = upper - lower + 1
  limbs = (width.bit_length() + 63) // 64
  source_width = 1 << (64 * limbs)
  limit = source_width - source_width % width
  values: list[int] = []
  while len(values) < size:
    word = 0
    for limb in rng.bit_generator.random_raw(limbs):
      word = word << 64 | int(limb)
    if word < limit:
      values.append(lower + word % width)
  return values


def _lattice_to_float64(values: np.ndarray | list[int], scale: Decimal, decimals: int) -> np.ndarray:
  float_scale = float(scale)
  if isinstance(values, np.ndarray) and np.isfinite(float_scale) and float_scale != 0:
    return np.asarray(values, dtype=np.float64) / float_scale
  return np.fromiter(
    (float(_shift_decimal(Decimal(int(value)), -decimals)) for value in values),
    dtype=np.float64,
    count=len(values),
  )


class NPCore:


  @classmethod
  def gen_uuid4(cls, size: int, *, rng: np.random.Generator) -> np.ndarray:
    b = np.frombuffer(rng.bytes(16 * size), np.uint8).reshape(size, 16).copy()
    b[:, 6] = b[:, 6] & 0x0F | 0x40
    b[:, 8] = b[:, 8] & 0x3F | 0x80
    return np.array([str(uuid.UUID(bytes=row.tobytes())) for row in b])
    
  @classmethod
  def gen_booleans(cls, size: int, true_prob=0.5, *, rng: np.random.Generator) -> np.ndarray:
    return rng.choice([True, False], size, p=[true_prob, 1 - true_prob])
  

  @classmethod
  def gen_ints(cls, size: int, min: int, max: int, int_type: str = 'int32', *, rng: np.random.Generator) -> np.ndarray:
    allowed_integers = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
    assert int_type in allowed_integers, f"int_type must be one of {allowed_integers}"
    return rng.integers(min, max + 1, size, dtype=int_type)
  

  @classmethod
  def gen_ints_zfilled(cls, size: int, length: int, *, rng: np.random.Generator) -> np.ndarray:
    # Use int64 explicitly to handle large numbers on Windows
    max_val = 10**length - 1
    str_arr = rng.integers(0, max_val + 1, size, dtype=np.int64).astype('str')
    return np.char.zfill(str_arr, length)
  
  
  @classmethod
  def gen_floats(cls, size: int, min: int | float, max: int | float, decimals: int = 2, *, rng: np.random.Generator) -> np.ndarray:
    lower, upper, scale = float_lattice_bounds(min, max, decimals)
    int64 = np.iinfo(np.int64)
    if int64.min <= lower <= upper <= int64.max:
      values = rng.integers(lower, upper, size, dtype=np.int64, endpoint=True)
    else:
      values = _unbiased_python_ints(rng, size, lower, upper)
    return _lattice_to_float64(values, scale, decimals)


  @classmethod
  def gen_floats_normal(cls, size: int, mean: int, std: int, decimals: int = 2, *, rng: np.random.Generator) -> np.ndarray:
    return np.round(rng.normal(mean, std, size), decimals)


  @classmethod
  def gen_exponential(cls, size: int, scale: int | float = 1.0, decimals: int = 2, *, rng: np.random.Generator) -> np.ndarray:
    return np.round(rng.exponential(scale, size), decimals)


  @classmethod
  def gen_lognormal(cls, size: int, mean: int | float = 0.0, std: int | float = 1.0, decimals: int = 2, *, rng: np.random.Generator) -> np.ndarray:
    return np.round(rng.lognormal(mean, std, size), decimals)


  @classmethod
  def gen_poisson(cls, size: int, lam: int | float = 1.0, *, rng: np.random.Generator) -> np.ndarray:
    return rng.poisson(lam, size)


  @classmethod
  def gen_zipf(cls, size: int, a: int | float = 2.0, *, rng: np.random.Generator) -> np.ndarray:
    return rng.zipf(a, size)


  @classmethod
  def gen_constant(cls, size: int, value: Any, *, rng: np.random.Generator) -> np.ndarray:
    return np.full(size, value)



  @classmethod
  def gen_distincts(cls, size: int, distincts: List[Any], *, rng: np.random.Generator) -> np.ndarray:
    assert len(list(set([type(x) for x in distincts]))) == 1
    return rng.choice(distincts, size)


  @classmethod
  def gen_distincts_prop(cls, size: int, distincts: Dict[str, int], *, rng: np.random.Generator) -> np.ndarray:
    distincts_prop = [ key for key, value in distincts.items() for i in range(value) ]
    #assert len(list(set([type(x) for x in distincts]))) == 1
    return rng.choice(distincts_prop, size)
  

  @classmethod
  def gen_unix_timestamps(cls, size: int, start: str, end: str, date_format: str = "%Y-%m-%d", *, rng: np.random.Generator) -> np.ndarray:
    dt_start, dt_end = (_parse_date_bound(value, date_format) for value in (start, end))
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = (int(d.replace(tzinfo=timezone.utc).timestamp()) for d in (dt_start, dt_end))
    # Use int64 to handle large Unix timestamps on Windows
    int_array = rng.integers(timestamp_start, timestamp_end, size, dtype=np.int64)
    return int_array
  

  @classmethod
  def gen_dates(cls, size: int, start: str, end: str, date_format: str = "%Y-%m-%d", *, rng: np.random.Generator) -> np.ndarray:
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
    timestamp_array = cls.gen_unix_timestamps(size, start, end, date_format, rng=rng)
    s = timestamp_array.astype("datetime64[s]")
    y, m, d = (s.astype(f"datetime64[{u}]") for u in "YMD")
    sec = (s - d).astype(np.int64)
    fields = {"%Y": y.astype(np.int64) + 1970, "%m": (m - y).astype(np.int64) + 1, "%d": (d - m).astype(np.int64) + 1,
              "%H": sec // 3600, "%M": sec // 60 % 60, "%S": sec % 60}
    tokens = [{"%f": "000000"}.get(t, t) for t in DATE_SPLIT.split(date_format) if t]
    widths = [(4 if t == "%Y" else 2) if t in fields else len(t) for t in tokens]
    codes, c = np.empty((size, sum(widths)), np.uint32), 0
    for t, w in zip(tokens, widths):
      if t in fields:
        for k in range(w): codes[:, c + k] = fields[t] // 10 ** (w - 1 - k) % 10 + 48
      else:
        codes[:, c:c + w] = [ord(ch) for ch in t]
      c += w
    return codes.view(f"<U{sum(widths)}").ravel()

if __name__ == "__main__":
  
  # test gen_dates
  import time
  start_time = time.time()
  dates = NPCore.gen_dates(10**7, "2020-01-01", "2024-12-31", "%Y-%m-%d", rng=np.random.default_rng())
  #print(f"Generated dates: {dates}")
  print(f"Execution time: {time.time() - start_time} seconds")
