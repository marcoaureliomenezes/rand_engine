import pytest
import numpy as np

from rand_engine.core.numeric_core import NumericCore
from datetime import datetime as dt


def test_gen_ints():
  kwargs = dict(size=10**1, min=0, max=10**4)
  real_result = NumericCore.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_sparse():
  kwargs = dict(size=10**4, min=0, max=10**1)
  real_result = NumericCore.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) == kwargs["min"]
  assert max(real_result) == kwargs["max"]
  assert type(real_result) == np.ndarray

def test_gen_ints_fails_1():
  kwargs = dict(size=10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NumericCore.gen_ints(**kwargs)


def test_gen_ints_fails_2():
  kwargs = dict(size=-10**1, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NumericCore.gen_ints(**kwargs)



def test_gen_floats():
  kwargs = dict(size=10**1, min=0, max=10**4, round=2)
  real_result = NumericCore.gen_floats(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray


