import pytest
import numpy as np
from rand_engine.core._np_core import NPCore
from tests.fixtures.f1_general import default_size



@pytest.mark.parametrize("min, max,int_type", [
    (-1*2**7, (2**7 - 1), 'int8'),
    (-1*2**15, (2**15 - 1), 'int16'),
    (-1*2**31, (2**31 - 1), 'int32'),
    (-1*2**63, (2**63 - 1), 'int64'),
    (0, (2**8 - 1), 'uint8'),
    (0, (2**16 - 1), 'uint16'),
    (0, (2**32 - 1), 'uint32'),
    (0, (2**63 - 1), 'uint64'),
])
def test_gen_ints(min, max, int_type):
  kwargs = dict(size=10, min=min, max=max, int_type=int_type)
  real_result = NPCore.gen_ints(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert str(type(real_result[0])) == f"<class 'numpy.{int_type}'>"
  item_size = real_result.itemsize
  total_size = real_result.nbytes
  assert item_size == np.dtype(int_type).itemsize
  assert total_size == item_size * kwargs["size"]


def test_gen_ints_with_size_0(default_size):
  kwargs = dict(size=0, min=0, max=10)
  data = NPCore.gen_ints(**kwargs)
  assert len(data) == 0


@pytest.mark.parametrize("size, min, max", [
    (10, 10**5, 10**1),
    (10, 0, -10**1),
    (-1, 0, 10**1)
])
def test_gen_ints_with_inconsistent_parameters(size, min, max):
  kwargs = dict(size=size, min=min, max=max)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(**kwargs)


@pytest.mark.parametrize("size, min, max, round", [
    (10, 0, 10**4, 2),
    (10, 0, 10**4, 10),
    (10, 0, 10**4, 15),
    (10, 0, 10**18, 15),
])
def test_gen_floats(size, min, max, round):
  kwargs = dict(size=size, min=min, max=max, round=round)
  real_result = NPCore.gen_floats(**kwargs)
  print(real_result)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert real_result.dtype == np.float64


# def test_gen_floats_normal(default_size):
#   kwargs = dict(size=default_size, mean=10**3, std=10**2, round=2)
#   real_result = NPCore.gen_floats_normal(**kwargs)
#   assert len(real_result) == kwargs["size"]
#   assert type(real_result) == np.ndarray

# def test_gen_distincts_low_cardinality(default_size):
#   distincts = ["value1", "value2", "value3"]
#   result = NPCore.gen_distincts(size=default_size, distincts=distincts)
#   assert len(result) == default_size
#   assert all(isinstance(item, str) for item in result)

# def test_gen_distincts_high_cardinality(default_size):
#   distincts = [f"value{i}" for i in range(default_size)]
#   result = NPCore.gen_distincts(size=default_size, distincts=distincts)
#   assert len(result) == default_size
#   assert all(isinstance(item, str) for item in result)


# def test_gen_unix_timestamps(default_size):
#   result = NPCore.gen_unix_timestamps(default_size, '2024-07-05', '2024-07-06', format="%Y-%m-%d")
#   assert len(result) == default_size

# # def test_gen_datetimes_fails_1(default_size):
# #   with pytest.raises(ValueError):
# #     _ = NPCore.gen_datetimes(default_size, '2024-07-05', '2024-07-06', format_in="%Y/%m/%d", format_out="%d/%b/%Y:%H:%M:%S")
# # def test_gen_datetimes_fails_2(default_size):
# #   with pytest.raises(ValueError):
# #     _ = NPCore.gen_datetimes(default_size, '2024-07-05', '2024-07-06', format_in="%Y-%m-%d", format_out="%d-%b-%Y:%H:%M:%S")


# def test_gen_unique_ids_zfilled(default_size):
#   result = NPCore.gen_unique_identifiers(default_size, strategy="uuid4")
#   assert len(result) == default_size
#   assert len(set(result)) == default_size