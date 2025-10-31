import pytest
import numpy as np
from rand_engine.core._np_core import NPCore
from tests.fixtures.f1_data_generator_specs_right import default_size



# Test for integer generation with various types and ranges
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


# Test for integer generation with size 0
def test_gen_ints_with_size_0(default_size):
  kwargs = dict(size=0, min=0, max=10)
  data = NPCore.gen_ints(**kwargs)
  assert len(data) == 0


# Test for integer generation with inconsistent parameters
@pytest.mark.parametrize("size, min, max", [
    (10, 10**5, 10**1),
    (10, 0, -10**1),
    (-1, 0, 10**1)
])
def test_gen_ints_with_inconsistent_parameters(size, min, max):
  kwargs = dict(size=size, min=min, max=max)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(**kwargs)


# Test for float generation with various ranges and rounding
@pytest.mark.parametrize("size, min, max, round", [
    (10, 0, 10**4, 2),
    (10, 0, 10**4, 10),
    (10, 0, 10**4, 15),
    (10, 0, 10**18, 15),
])
def test_gen_floats(size, min, max, round):
  kwargs = dict(size=size, min=min, max=max, round=round)
  real_result = NPCore.gen_floats(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert real_result.dtype == np.float64


# Test for float generation with inconsistent parameters
@pytest.mark.parametrize("size, min, max", [
    (10, 10**5, 10**1),
    (10, -10**1, -10**5),
    (-1, 0, 10**1)
])
def test_gen_floats_with_inconsistent_parameters(size, min, max):
  kwargs = dict(size=size, min=min, max=max)
  with pytest.raises(ValueError):
    _ = NPCore.gen_floats(**kwargs)


@pytest.mark.parametrize("size, mean, std, round", [
    (100, 0, 1, 2),
    (100, 10**3, 10**2, 5),
    (100, 10**6, 10**5, 10),
])
def test_gen_floats_normal(size, mean, std, round):
  kwargs = dict(size=size, mean=mean, std=std, round=round)
  real_result = NPCore.gen_floats_normal(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert real_result.dtype == np.float64
  assert abs(np.mean(real_result) - mean) < std * 3  # within 3 std devs
  assert abs(np.std(real_result) - std) < std * 0.5


@pytest.mark.parametrize("size, distincts", [
    (10, ["A", "B", "C"]),
    (10, [1, 2, 3, 4, 5]),
    (10, [True, False]),
])
def test_gen_distincts_low_cardinality(size, distincts):
  result = NPCore.gen_distincts(size=size, distincts=distincts)
  assert len(result) == size
  assert all(item in distincts for item in result)




def test_gen_ints_fails_1(default_size):
  kwargs = dict(size=default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(**kwargs)


def test_gen_ints_fails_2(default_size):
  kwargs = dict(size=-default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(**kwargs)


def test_gen_floats(default_size):
  kwargs = dict(size=default_size, min=0, max=10**4, decimals=2)
  real_result = NPCore.gen_floats(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_floats_normal(default_size):
  kwargs = dict(size=default_size, mean=10**3, std=10**2, decimals=2)
  real_result = NPCore.gen_floats_normal(**kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray

def test_gen_distincts_low_cardinality(default_size):
  distincts = ["value1", "value2", "value3"]
  result = NPCore.gen_distincts(size=default_size, distincts=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)

def test_gen_distincts_high_cardinality(default_size):
  distincts = [f"value{i}" for i in range(default_size)]
  result = NPCore.gen_distincts(size=default_size, distincts=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)


def test_gen_unix_timestamps(default_size):
  result = NPCore.gen_unix_timestamps(default_size, '2024-07-05', '2024-07-06', format="%Y-%m-%d")
  assert len(result) == default_size


def test_gen_dates(default_size):
  result = NPCore.gen_dates(default_size, '2020-01-01', '2024-12-31', format="%Y-%m-%d")
  assert len(result) == default_size


# ============================================================================
# ADDITIONAL TESTS FOR COMPLETE COVERAGE
# ============================================================================

# Tests for gen_uuid4
def test_gen_uuid4_basic(default_size):
  """Test UUID generation returns correct size and format."""
  result = NPCore.gen_uuid4(size=default_size)
  assert len(result) == default_size
  assert type(result) == np.ndarray
  # Check UUID format (36 characters with dashes)
  for uuid_str in result:
    assert isinstance(uuid_str, str)
    assert len(uuid_str) == 36
    assert uuid_str.count('-') == 4


def test_gen_uuid4_uniqueness():
  """Test that generated UUIDs are unique."""
  size = 1000
  result = NPCore.gen_uuid4(size=size)
  unique_uuids = set(result)
  assert len(unique_uuids) == size  # All should be unique


# Tests for gen_booleans
def test_gen_booleans_default_probability(default_size):
  """Test boolean generation with default 50% probability."""
  result = NPCore.gen_booleans(size=default_size, true_prob=0.5)
  assert len(result) == default_size
  assert type(result) == np.ndarray
  assert result.dtype == bool
  # Should have mix of True and False
  assert True in result
  assert False in result


@pytest.mark.parametrize("true_prob", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_gen_booleans_various_probabilities(true_prob):
  """Test boolean generation with various probabilities."""
  size = 10000
  result = NPCore.gen_booleans(size=size, true_prob=true_prob)
  true_ratio = np.sum(result) / size
  
  # Allow 5% tolerance
  if true_prob == 0.0:
    assert true_ratio == 0.0
  elif true_prob == 1.0:
    assert true_ratio == 1.0
  else:
    assert abs(true_ratio - true_prob) < 0.05


# Tests for gen_ints_zfilled
@pytest.mark.parametrize("length", [4, 6, 8, 10, 12])
def test_gen_ints_zfilled_various_lengths(length, default_size):
  """Test zero-filled integer generation with various lengths."""
  result = NPCore.gen_ints_zfilled(size=default_size, length=length)
  assert len(result) == default_size
  assert type(result) == np.ndarray
  
  # Check all are strings of correct length
  for item in result:
    assert isinstance(item, (str, np.str_))
    assert len(item) == length
    assert item.isdigit()


def test_gen_ints_zfilled_padding():
  """Test that zero-filling correctly pads numbers."""
  size = 100
  length = 8
  result = NPCore.gen_ints_zfilled(size=size, length=length)
  
  # All should be 8 characters
  for item in result:
    assert len(item) == length
    # Should be valid integers when converted
    int_val = int(item)
    assert 0 <= int_val <= 10**length - 1


# Tests for gen_distincts_prop
def test_gen_distincts_prop_basic():
  """Test proportional distinct generation."""
  size = 1000
  distincts = {"A": 70, "B": 20, "C": 10}
  result = NPCore.gen_distincts_prop(size=size, distincts=distincts)
  
  assert len(result) == size
  assert type(result) == np.ndarray
  # All values should be from the keys
  assert all(item in distincts.keys() for item in result)


def test_gen_distincts_prop_distribution():
  """Test that proportional distribution is approximately correct."""
  size = 10000
  distincts = {"Junior": 60, "Pleno": 30, "Senior": 10}
  result = NPCore.gen_distincts_prop(size=size, distincts=distincts)
  
  # Count occurrences
  from collections import Counter
  counts = Counter(result)
  
  total_weight = sum(distincts.values())
  
  # Check proportions (allow 5% tolerance)
  for key, weight in distincts.items():
    expected_ratio = weight / total_weight
    actual_ratio = counts[key] / size
    assert abs(actual_ratio - expected_ratio) < 0.05


@pytest.mark.parametrize("distincts", [
    {"X": 1},
    {"A": 50, "B": 50},
    {"low": 10, "medium": 30, "high": 60}
])
def test_gen_distincts_prop_various_distributions(distincts):
  """Test proportional generation with various weight distributions."""
  size = 1000
  result = NPCore.gen_distincts_prop(size=size, distincts=distincts)
  assert len(result) == size
  assert all(item in distincts.keys() for item in result)


# Additional edge case tests
def test_gen_ints_zfilled_edge_case_small():
  """Test zero-filled integers with very small length."""
  size = 10
  length = 2
  result = NPCore.gen_ints_zfilled(size=size, length=length)
  assert len(result) == size
  for item in result:
    assert len(item) == length
    assert 0 <= int(item) <= 99


def test_gen_booleans_edge_case_all_true():
  """Test boolean generation with 100% true probability."""
  size = 100
  result = NPCore.gen_booleans(size=size, true_prob=1.0)
  assert all(result)


def test_gen_booleans_edge_case_all_false():
  """Test boolean generation with 0% true probability."""
  size = 100
  result = NPCore.gen_booleans(size=size, true_prob=0.0)
  assert not any(result)