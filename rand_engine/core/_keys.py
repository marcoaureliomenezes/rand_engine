import json
import zlib

import numpy as np

from rand_engine.validators.exceptions import RandEngineError


class Keys:

  # xxh64 primes; uint64 arithmetic wraps like Spark's XXH64.hashLong
  P1, P2, P3 = np.uint64(0x9E3779B185EBCA87), np.uint64(0xC2B2AE3D27D4EB4F), np.uint64(0x165667B19E3779F9)
  P4, P5 = np.uint64(0x85EBCA77C2B2AE63), np.uint64(0x27D4EB2F165667C5)


  @classmethod
  def _rotl(cls, x, r):
    return (x << np.uint64(r)) | (x >> np.uint64(64 - r))


  @classmethod
  def xxh64_long(cls, v, seed) -> np.ndarray:
    v = np.asarray(v).astype(np.int64).view(np.uint64)
    seed = np.asarray(seed).astype(np.int64).view(np.uint64)
    with np.errstate(over="ignore"):
      h = seed + cls.P5 + np.uint64(8)
      h ^= cls._rotl(v * cls.P2, 31) * cls.P1
      h = cls._rotl(h, 27) * cls.P1 + cls.P4
      h ^= h >> np.uint64(33); h *= cls.P2
      h ^= h >> np.uint64(29); h *= cls.P3
      h ^= h >> np.uint64(32)
    return h.view(np.int64)


  @classmethod
  def cell_hash(cls, col_seed: int, idx) -> np.ndarray:
    return cls.xxh64_long(idx, cls.xxh64_long(np.int64(col_seed), np.int64(42)))


  @classmethod
  def _feistel(cls, idx: np.ndarray, domain: int, key: int, rounds: int = 4) -> np.ndarray:
    """Bijection on [0, domain): balanced Feistel on 2*half bits, cycle-walked back into the domain."""
    bits = max(2, int(domain - 1).bit_length()); bits += bits & 1; half = bits // 2
    mask = np.int64((1 << half) - 1)
    seeds = [cls.xxh64_long(np.int64(key + k), np.int64(42)) for k in range(rounds)]
    x = idx.copy()
    pos, v = np.arange(x.size), x
    while pos.size:
      l, r = v >> half, v & mask
      for s in seeds:
        l, r = r, l ^ (cls.xxh64_long(r, s) & mask)
      v = (l << half) | r
      x[pos] = v
      walk = v >= domain
      pos, v = pos[walk], v[walk]
    return x


  @classmethod
  def _pk_at(cls, idx: np.ndarray, style: str = "sequence", start: int = 0, step: int = 1,
             domain: int = 0, key: int = 0, format: str = None) -> np.ndarray | list:
    if style == "permuted":
      if idx.size and idx.max() >= domain:
        raise RandEngineError(f"pk row index {idx.max()} is outside the permuted domain {domain}")
      values = start + cls._feistel(idx, domain, key)
    else:
      if idx.size and not all(-2**63 <= start + int(i) * step < 2**63 for i in (idx.min(), idx.max())):
        raise RandEngineError(f"pk sequence start={start} step={step} leaves int64 at row index {idx.max()}")
      values = start + idx * step
    return values if format is None else list(map(format.format, values.tolist()))


  @classmethod
  def gen_pk(cls, size: int, offset: int = 0, **kwargs) -> np.ndarray | list:
    return cls._pk_at(np.arange(offset, offset + size, dtype=np.int64), **kwargs)


  @classmethod
  def _zipf_rank(cls, h: np.ndarray, n: int, s: float) -> np.ndarray:
    """Bounded power-law rank in [0, n): inverse CDF of the continuous x^-s on [1, n+1]."""
    u = (h % np.int64(1 << 53)) / float(1 << 53)
    if s == 1.0:
      x = np.exp(u * np.log(n + 1.0)) - 1.0
    else:
      x = ((n + 1.0) ** (1 - s) * u + (1 - u)) ** (1 / (1 - s)) - 1.0
    return np.minimum(x.astype(np.int64), n - 1)


  @classmethod
  def gen_fk(cls, size: int, parent: dict, parent_size: int, skew: float = 0.0, offset: int = 0,
             key_seed: int = 0, column: str = "") -> np.ndarray | list:
    kwargs = json.dumps({"parent": parent, "parent_size": parent_size, "skew": float(skew)}, sort_keys=True)
    fk_seed = zlib.crc32(f"{key_seed}/{column}/{kwargs}".encode())
    h = cls.cell_hash(fk_seed, np.arange(offset, offset + size, dtype=np.int64))
    if skew:  # Zipf over ranks, ranks permuted so the hot parents are not the first row indices
      idx = cls._feistel(cls._zipf_rank(h, parent_size, skew), parent_size, fk_seed)
    else:
      idx = h % np.int64(parent_size)
    return cls._pk_at(idx, **parent.get("kwargs", {}))
