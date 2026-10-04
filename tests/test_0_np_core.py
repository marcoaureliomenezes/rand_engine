import time
import uuid
import pytest
import numpy as np
from rand_engine.core._np_core import NPCore

RNG = np.random.default_rng(0)
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
  real_result = NPCore.gen_ints(rng=RNG, **kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert str(type(real_result[0])) == f"<class 'numpy.{int_type}'>"
  item_size = real_result.itemsize
  total_size = real_result.nbytes
  assert item_size == np.dtype(int_type).itemsize
  assert total_size == item_size * kwargs["size"]


@pytest.mark.parametrize("min, max, int_type", [(0, 1000, 'int8'), (-1, 10, 'uint8')])
def test_gen_ints_bounds_not_fitting_int_type_are_rejected(min, max, int_type):
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(rng=RNG, size=10, min=min, max=max, int_type=int_type)


# Test for integer generation with size 0
def test_gen_ints_with_size_0(default_size):
  kwargs = dict(size=0, min=0, max=10)
  data = NPCore.gen_ints(rng=RNG, **kwargs)
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
    _ = NPCore.gen_ints(rng=RNG, **kwargs)


# Test for float generation with various ranges and rounding
@pytest.mark.parametrize("size, min, max, decimals", [
    (10, 0, 10**4, 2),
    (10, 0, 10**4, 10),
    (10, 0, 10**4, 15),
    (10, 0, 10**18, 15),
])
def test_gen_floats(size, min, max, decimals):
  kwargs = dict(size=size, min=min, max=max, decimals=decimals)
  real_result = NPCore.gen_floats(rng=RNG, **kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray
  assert real_result.dtype == np.float64


def test_gen_floats_stay_within_fractional_bounds():
  values = NPCore.gen_floats(rng=RNG, size=10**4, min=9.99, max=10.5, decimals=2)
  assert values.min() >= 9.99 and values.max() <= 10.5
  assert values.max() > 10
  assert np.array_equal(values, values.round(2))


def test_gen_floats_with_equal_bounds_returns_that_value():
  assert NPCore.gen_floats(rng=RNG, size=10, min=5.25, max=5.25, decimals=2).tolist() == [5.25] * 10


# Test for float generation with inconsistent parameters
@pytest.mark.parametrize("size, min, max", [
    (10, 10**5, 10**1),
    (10, -10**1, -10**5),
    (-1, 0, 10**1)
])
def test_gen_floats_with_inconsistent_parameters(size, min, max):
  kwargs = dict(size=size, min=min, max=max)
  with pytest.raises(ValueError):
    _ = NPCore.gen_floats(rng=RNG, **kwargs)


@pytest.mark.parametrize("size, mean, std, decimals", [
    (100, 0, 1, 2),
    (100, 10**3, 10**2, 5),
    (100, 10**6, 10**5, 10),
])
def test_gen_floats_normal(size, mean, std, decimals):
  kwargs = dict(size=size, mean=mean, std=std, decimals=decimals)
  real_result = NPCore.gen_floats_normal(rng=RNG, **kwargs)
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
  result = NPCore.gen_distincts(rng=RNG, size=size, distincts=distincts)
  assert len(result) == size
  assert all(item in distincts for item in result)




def test_gen_ints_fails_1(default_size):
  kwargs = dict(size=default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(rng=RNG, **kwargs)


def test_gen_ints_fails_2(default_size):
  kwargs = dict(size=-default_size, min=10**1, max=0)
  with pytest.raises(ValueError):
    _ = NPCore.gen_ints(rng=RNG, **kwargs)


def test_gen_floats(default_size):
  kwargs = dict(size=default_size, min=0, max=10**4, decimals=2)
  real_result = NPCore.gen_floats(rng=RNG, **kwargs)
  assert len(real_result) == kwargs["size"]
  assert min(real_result) >= kwargs["min"]
  assert max(real_result) <= kwargs["max"]
  assert type(real_result) == np.ndarray


def test_gen_floats_normal(default_size):
  kwargs = dict(size=default_size, mean=10**3, std=10**2, decimals=2)
  real_result = NPCore.gen_floats_normal(rng=RNG, **kwargs)
  assert len(real_result) == kwargs["size"]
  assert type(real_result) == np.ndarray

def test_gen_distincts_low_cardinality(default_size):
  distincts = ["value1", "value2", "value3"]
  result = NPCore.gen_distincts(rng=RNG, size=default_size, distincts=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)

def test_gen_distincts_high_cardinality(default_size):
  distincts = [f"value{i}" for i in range(default_size)]
  result = NPCore.gen_distincts(rng=RNG, size=default_size, distincts=distincts)
  assert len(result) == default_size
  assert all(isinstance(item, str) for item in result)


def test_gen_unix_timestamps(default_size):
  result = NPCore.gen_unix_timestamps(default_size, '2024-07-05', '2024-07-06', date_format="%Y-%m-%d", rng=RNG)
  assert len(result) == default_size


def test_gen_dates(default_size):
  result = NPCore.gen_dates(default_size, '2020-01-01', '2024-12-31', date_format="%Y-%m-%d", rng=RNG)
  assert len(result) == default_size


# ============================================================================
# ADDITIONAL TESTS FOR COMPLETE COVERAGE
# ============================================================================

# Tests for gen_uuid4
def test_gen_uuid4_basic(default_size):
  """Test UUID generation returns correct size and format."""
  result = NPCore.gen_uuid4(rng=RNG, size=default_size)
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
  result = NPCore.gen_uuid4(rng=RNG, size=size)
  unique_uuids = set(result)
  assert len(unique_uuids) == size  # All should be unique


# Tests for gen_booleans
def test_gen_booleans_default_probability(default_size):
  """Test boolean generation with default 50% probability."""
  result = NPCore.gen_booleans(rng=RNG, size=default_size, true_prob=0.5)
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
  result = NPCore.gen_booleans(rng=RNG, size=size, true_prob=true_prob)
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
  result = NPCore.gen_ints_zfilled(rng=RNG, size=default_size, length=length)
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
  result = NPCore.gen_ints_zfilled(rng=RNG, size=size, length=length)
  
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
  result = NPCore.gen_distincts_prop(rng=RNG, size=size, distincts=distincts)
  
  assert len(result) == size
  assert type(result) == np.ndarray
  # All values should be from the keys
  assert all(item in distincts.keys() for item in result)


def test_gen_distincts_prop_distribution():
  """Test that proportional distribution is approximately correct."""
  size = 10000
  distincts = {"Junior": 60, "Pleno": 30, "Senior": 10}
  result = NPCore.gen_distincts_prop(rng=RNG, size=size, distincts=distincts)
  
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
  result = NPCore.gen_distincts_prop(rng=RNG, size=size, distincts=distincts)
  assert len(result) == size
  assert all(item in distincts.keys() for item in result)


# Additional edge case tests
def test_gen_ints_zfilled_edge_case_small():
  """Test zero-filled integers with very small length."""
  size = 10
  length = 2
  result = NPCore.gen_ints_zfilled(rng=RNG, size=size, length=length)
  assert len(result) == size
  for item in result:
    assert len(item) == length
    assert 0 <= int(item) <= 99


def test_gen_booleans_edge_case_all_true():
  """Test boolean generation with 100% true probability."""
  size = 100
  result = NPCore.gen_booleans(rng=RNG, size=size, true_prob=1.0)
  assert all(result)


def test_gen_booleans_edge_case_all_false():
  """Test boolean generation with 0% true probability."""
  size = 100
  result = NPCore.gen_booleans(rng=RNG, size=size, true_prob=0.0)
  assert not any(result)

@pytest.mark.skipif(not hasattr(time, "tzset"), reason="time.tzset is Unix-only")
@pytest.mark.parametrize("tz", ["UTC", "America/Sao_Paulo", "Asia/Tokyo"])
def test_gen_unix_timestamps_and_dates_ignore_process_timezone(tz, monkeypatch):
  monkeypatch.setenv("TZ", tz)
  time.tzset()
  try:
    args = (3, "2024-01-01 00:00:00", "2024-01-01 00:00:01", "%Y-%m-%d %H:%M:%S")
    assert NPCore.gen_unix_timestamps(*args, rng=RNG).tolist() == [1704067200] * 3
    assert NPCore.gen_dates(*args, rng=RNG).tolist() == ["2024-01-01 00:00:00"] * 3
  finally:
    monkeypatch.undo()
    time.tzset()


def test_gen_uuid4_values_are_rfc4122_version_4():
  """AC4.5"""
  values = NPCore.gen_uuid4(1000, rng=np.random.default_rng(0))
  parsed = [uuid.UUID(v) for v in values]
  assert {(u.version, u.variant) for u in parsed} == {(4, uuid.RFC_4122)}
  assert [str(u) for u in parsed] == values.tolist()
  assert len(set(values)) == 1000


def test_gen_ints_and_zfilled_reach_the_inclusive_max():
  assert set(NPCore.gen_ints(1000, 0, 1, rng=RNG).tolist()) == {0, 1}
  assert set(NPCore.gen_ints_zfilled(1000, 1, rng=RNG).tolist()) == set("0123456789")
