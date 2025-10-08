import pytest
import numpy as np
from rand_engine.core import Core
from tests.fixtures.fixtures import default_size



def test_gen_ints(default_size):
  kwargs = dict(size=default_size, min=0, max=10**4)
  real_result = Core.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints_sparse(default_size):
  kwargs = dict(size=default_size, min=0, max=10**1)
  real_result = Core.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) == kwargs["min"]
  assert max(real_result) == kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_ints_fails_1(default_size):
  kwargs = dict(size=default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = Core.gen_ints(**kwargs)


def test_gen_ints_fails_2(default_size):
  kwargs = dict(size=-default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = Core.gen_ints(**kwargs)


def test_gen_floats(default_size):
  kwargs = dict(size=default_size, min=0, max=10**4, round=2)
  real_result = Core.gen_floats(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_floats_normal(default_size):
  kwargs = dict(size=default_size, mean=10**3, std=10**2, round=2)
  real_result = Core.gen_floats_normal(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray

def test_gen_distincts_typed_low_cardinality(default_size):
  distincts = ["value1", "value2", "value3"]
  result = Core.gen_distincts_typed(size=default_size, distinct=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)

def test_gen_distincts_typed_high_cardinality(default_size):
  distincts = [f"value{i}" for i in range(default_size)]
  result = Core.gen_distincts_typed(size=default_size, distinct=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)


def test_gen_unix_timestamps(default_size):
  result = Core.gen_unix_timestamps(default_size, '2024-07-05', '2024-07-06', format="%Y-%m-%d")
  assert len(result) == default_size

# def test_gen_datetimes_fails_1(default_size):
#   with pytest.raises(ValueError):
#     _ = Core.gen_datetimes(default_size, '2024-07-05', '2024-07-06', format_in="%Y/%m/%d", format_out="%d/%b/%Y:%H:%M:%S")
# def test_gen_datetimes_fails_2(default_size):
#   with pytest.raises(ValueError):
#     _ = Core.gen_datetimes(default_size, '2024-07-05', '2024-07-06', format_in="%Y-%m-%d", format_out="%d-%b-%Y:%H:%M:%S")


def test_gen_unique_ids_zfilled(default_size):
  result = Core.gen_unique_identifiers(default_size, method="uuid4")
  assert len(result) == default_size
  assert len(set(result)) == default_size