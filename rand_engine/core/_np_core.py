
import math
import uuid
import re
import numpy as np

from typing import List, Any, Dict
from datetime import datetime as dt, timezone
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR


DATE_DIRECTIVES = ("%Y", "%m", "%d", "%H", "%M", "%S", "%f")
DATE_SPLIT = re.compile(f"({'|'.join(DATE_DIRECTIVES)})")


def _parse_date_bound(value: str, date_format: str) -> dt:
  try:
    return dt.strptime(value, date_format)
  except ValueError:
    return dt.strptime(value, "%Y-%m-%d")


def float_lattice_bounds(min: int | float, max: int | float, decimals: int) -> tuple[int, int, bool]:
  if type(decimals) is not int or abs(decimals) > 308: raise ValueError(f"decimals ({decimals}) must be an int with abs <= 308")
  low, high = Decimal(str(min)), Decimal(str(max))
  if not (low.is_finite() and high.is_finite()): raise ValueError("float bounds must be finite")
  if not math.isfinite(float(high - low)): raise ValueError(f"span between min ({min}) and max ({max}) overflows float64")
  low, high = (int(x.scaleb(decimals, Context(prec=400)).to_integral_value(r)) for x, r in ((low, ROUND_CEILING), (high, ROUND_FLOOR)))
  if low > high: raise ValueError(f"no representable value between min ({min}) and max ({max}) at decimals={decimals}")
  return low, high, high - low + 1 > 2 ** 53 or low < -2 ** 63 or high >= 2 ** 63


POISSON_LAM_MAX = 10**6
ZIPF_TABLE = 1000  # the table covers k <= 1000 and the exact tail sampler covers the rest, so this only trades build cost against tail draws
_INT64_TOP = 9223372036854774784.0  # largest float64 below 2**63


def poisson_lam_supported(lam: int | float) -> bool:
  """Whether the alias table stays small: lam is at most POISSON_LAM_MAX."""
  return lam <= POISSON_LAM_MAX


def _alias_draw(weights: np.ndarray, size: int, rng: np.random.Generator) -> np.ndarray:
  """Walker/Vose alias draw of bucket indexes proportional to weights."""
  n = len(weights)
  scaled = weights * (n / weights.sum())
  prob, alias = np.ones(n), np.arange(n)
  small = [i for i in range(n) if scaled[i] < 1]
  large = [i for i in range(n) if scaled[i] >= 1]
  while small and large:
    s, l = small.pop(), large.pop()
    prob[s], alias[s] = scaled[s], l
    scaled[l] -= 1 - scaled[s]
    (small if scaled[l] < 1 else large).append(l)
  i = rng.integers(0, n, size)
  return np.where(rng.random(size) < prob[i], i, alias[i])


def _zipf_tail(count: int, a: float, first: int, rng: np.random.Generator) -> np.ndarray:
  """Exact draws of k >= first with P(k) proportional to k**-a, by rejection from floor(Pareto).

  The proposal q(k) is the integral of x**-a over [k, k+1); p/q is r(k) below, decreasing in k,
  so r(first) bounds it. Draws are limited to int64 by truncating the Pareto uniform, not by redrawing.
  """
  def ratio(k):
    return (a - 1) / (k * -np.expm1((1 - a) * np.log1p(1 / k)))
  bound, floor_u = ratio(float(first)), (first / 2.0 ** 63) ** (a - 1)
  out, pending = np.empty(count, np.int64), np.arange(count)
  while pending.size:
    u = floor_u + (1 - floor_u) * (1 - rng.random(pending.size))
    k = np.floor(np.minimum(first * u ** (-1 / (a - 1)), _INT64_TOP))
    accepted = rng.random(pending.size) * bound < ratio(k)
    out[pending[accepted]] = k[accepted]
    pending = pending[~accepted]
  return out


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
    low, high, fine = float_lattice_bounds(min, max, decimals)
    if fine: return rng.uniform(min, max, size)
    scale = float(10 ** abs(decimals))
    values = rng.integers(low, high, size, dtype=np.int64, endpoint=True)
    return values / scale if decimals >= 0 else values * scale


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
    if lam == 0: return np.zeros(size, np.int64)
    width = 12 * lam ** 0.5 + 20  # P(|X - lam| > width) is below 1e-16, folded into the normalisation
    low = max(0, int(lam - width))
    k = np.arange(low, int(lam + width) + 1)
    log_pmf = -lam + k * np.log(lam) - np.array([math.lgamma(x + 1) for x in k])
    return low + _alias_draw(np.exp(log_pmf - log_pmf.max()), size, rng).astype(np.int64)


  @classmethod
  def gen_zipf(cls, size: int, a: int | float = 2.0, *, rng: np.random.Generator) -> np.ndarray:
    n = ZIPF_TABLE + 1  # exact tail weight sum_{k>n-1}: Euler-Maclaurin to the n**-(a+3) term, error below 1e-20 relative
    tail = n ** (1 - a) / (a - 1) + n ** -a / 2 + a * n ** (-a - 1) / 12 - a * (a + 1) * (a + 2) * n ** (-a - 3) / 720
    weights = np.append(np.arange(1, n, dtype=float) ** -a, tail)
    out = _alias_draw(weights, size, rng).astype(np.int64) + 1
    in_tail = out == n
    out[in_tail] = _zipf_tail(int(in_tail.sum()), a, n, rng)
    return out


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
