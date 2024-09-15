import pytest
import numpy as np

from rand_engine.bulk.core_numeric import CoreNumeric
from datetime import datetime as dt


def test_gen_ints():
  kwargs = dict(size=10**1, min=0, max=10**4)
  real_result = CoreNumeric.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_sparse():
  kwargs = dict(size=10**4, min=0, max=10**1)
  real_result = CoreNumeric.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) == kwargs["min"]
  assert max(real_result) == kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_fails_1():
  kwargs = dict(size=10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = CoreNumeric.gen_ints(**kwargs)


def test_gen_ints_fails_2():
  kwargs = dict(size=-10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = CoreNumeric.gen_ints(**kwargs)


def test_gen_ints10():
  kwargs = dict(size=10**1, min=0, max=3)
  real_result = CoreNumeric.gen_ints10(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= 10**kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints10_sparse():
  kwargs = dict(size=10**3, min=0, max=2)
  real_result = CoreNumeric.gen_ints10(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= 10**kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints10_fails_1():
  kwargs = dict(size=10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = CoreNumeric.gen_ints10(**kwargs)



def test_gen_datetime():
  kwargs = dict(size=10**1, start="01-01-2020", end="01-01-2021", format="%d-%m-%Y")
  real_result = CoreNumeric.gen_datetime(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= dt.strptime(kwargs["start"], kwargs["format"])
  assert max(real_result) <= dt.strptime(kwargs["end"], kwargs["format"])
  assert type(real_result) == np.ndarray


