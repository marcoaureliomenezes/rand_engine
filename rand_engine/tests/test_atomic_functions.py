import numpy as np
import pytest
import time
from rand_engine.bulk.atomic_functions import gen_ints, gen_ints10, gen_distincts_typed, gen_distinct_untyped_baseline, gen_distincts_untyped, fake_dates
from datetime import datetime as dt


def test_gen_ints():
  kwargs = dict(size=10**1, min=0, max=10**4)
  real_result = gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_sparse():
  kwargs = dict(size=10**4, min=0, max=10**1)
  real_result = gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) == kwargs["min"]
  assert max(real_result) == kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_fails_1():
  kwargs = dict(size=10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = gen_ints(**kwargs)


def test_gen_ints_fails_2():
  kwargs = dict(size=-10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = gen_ints(**kwargs)


def test_gen_ints10():
  kwargs = dict(size=10**1, min=0, max=3)
  real_result = gen_ints10(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= 10**kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints10_sparse():
  kwargs = dict(size=10**3, min=0, max=2)
  real_result = gen_ints10(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= 10**kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints10_fails_1():
  kwargs = dict(size=10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = gen_ints10(**kwargs)


def test_gen_dates():
  kwargs = dict(size=10**1, start="01-01-2020", end="01-01-2021", format="%d-%m-%Y")
  real_result = fake_dates(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= dt.strptime(kwargs["start"], kwargs["format"])
  assert max(real_result) <= dt.strptime(kwargs["end"], kwargs["format"])
  assert type(real_result) == np.ndarray


def test_gen_distincts():
  kwargs = dict(size=10**7, distinct=["value1", "value2", True, 1, 1.0])
  
  start_time = time.time()
  real_result = gen_distinct_untyped_baseline(**kwargs)
  elapsed_time = time.time() - start_time
  del real_result
  print(f"Elapsed time Baseline: {elapsed_time}")
  start_time = time.time()
  real_result = gen_distincts_untyped(**kwargs)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Benchmark: {elapsed_time}")


def test_gen_distincts_same_type():
  kwargs = dict(size=10**7, distinct=["value1", "value2"])
  start_time = time.time()
  real_result = gen_distinct_untyped_baseline(**kwargs)
  elapsed_time = time.time() - start_time
  del real_result
  print(f"Elapsed time Baseline: {elapsed_time}")
  start_time = time.time()
  real_result = gen_distincts_untyped(**kwargs)
  elapsed_time = time.time() - start_time
  print(f"Elapsed time Benchmark: {elapsed_time}")
