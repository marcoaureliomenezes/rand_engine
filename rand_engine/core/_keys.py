import zlib

import numpy as np


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
  def _pk_at(cls, idx: np.ndarray, style: str = "sequence", start: int = 0, step: int = 1) -> np.ndarray:
    return start + idx * step


  @classmethod
  def gen_pk(cls, size: int, offset: int = 0, **kwargs) -> np.ndarray:
    return cls._pk_at(np.arange(offset, offset + size, dtype=np.int64), **kwargs)


  @classmethod
  def gen_fk(cls, size: int, parent: dict, parent_size: int, offset: int = 0, key_seed: int = 0, column: str = "") -> np.ndarray:
    fk_seed = zlib.crc32(f"{key_seed}/{column}".encode())
    h = cls.cell_hash(fk_seed, np.arange(offset, offset + size, dtype=np.int64))
    return cls._pk_at(h % np.int64(parent_size), **parent.get("kwargs", {}))
