from random import randint
import pickle
import numpy as np
import time
import pytest
from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_right_specs import (
    rand_spec_with_kwargs,
    rand_spec_with_args,
    rand_spec_with_related_columns,
    rand_spec_with_transformers,
    rand_spec_lambda_with_kwargs,
    rand_spec_all_methods
)

from tests.fixtures.f3_integrations import (
    df_size,
    microbatch_size,
    batch_size,
)




@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_with_kwargs_spec(rand_spec_with_kwargs, size):
  df_data = DataGenerator(rand_spec_with_kwargs).size(size).get_df()
  assert df_data.shape[0] == size
  assert rand_spec_with_kwargs.keys() == set(df_data.columns)


def test_create_df_simple_with_kwargs_spec_lambda_size(rand_spec_with_kwargs):
  min_size = 10**2
  max_size = 10**3
  df_data = DataGenerator(rand_spec_with_kwargs).size(lambda: randint(min_size, max_size)).get_df()
  assert min_size <= df_data.shape[0] <= max_size
  assert rand_spec_with_kwargs.keys() == set(df_data.columns)



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_with_lazy_spec(rand_spec_lambda_with_kwargs, size):
  df_data = DataGenerator(rand_spec_lambda_with_kwargs()).size(size).get_df()
  assert df_data.shape[0] == size
  assert rand_spec_lambda_with_kwargs().keys() == set(df_data.columns)


@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_with_related_columns(rand_spec_with_related_columns, size):
  df_data = DataGenerator(rand_spec_with_related_columns).size(size).get_df()
  assert df_data.shape[0] == size
  columns = []
  for k, v in rand_spec_with_related_columns.items():
    columns.append(k) if "cols" not in v else columns.extend(v["cols"])
  assert set(columns) == set(df_data.columns)



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_with_inline_transformer(rand_spec_with_transformers, size):
  df_data = DataGenerator(rand_spec_with_transformers).size(size).get_df()
  assert df_data.shape[0] == size
  # Check transformed columns exist
  assert "timestamp" in df_data.columns
  assert "email" in df_data.columns
  assert "price" in df_data.columns
  # Verify transformers were applied
  assert all("@example.com" in email for email in df_data["email"])
  assert all("/" in ts for ts in df_data["timestamp"])  # Date format check



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_pandas_df_transformer(size, rand_spec_with_args):
  df_data_1 = DataGenerator(rand_spec_with_args).size(size).get_df()
  # Transform temperature column
  transformers = [
    lambda df: df.assign(temp_fahrenheit=(df["temperature"] * 9/5) + 32),
  ]
  df_data_2 = DataGenerator(rand_spec_with_args).transformers(transformers).size(size).get_df()
  assert df_data_1.shape[0] == size
  assert df_data_2.shape[0] == size
  assert "temp_fahrenheit" in df_data_2.columns
  # Verify transformation is correct
  assert all(df_data_2["temp_fahrenheit"] > df_data_2["temperature"])



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_with_seed(rand_spec_with_args, size):
  df_data_1 = DataGenerator(rand_spec_with_args, seed=True).size(size).get_df()
  df_data_2 = DataGenerator(rand_spec_with_args, seed=True).size(size).get_df()
  assert df_data_1.equals(df_data_2)
  assert df_data_1.shape == df_data_2.shape



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_create_df_simple_without_seed(rand_spec_with_args, size):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using a variable seed.
  """
  df_data_1 = DataGenerator(rand_spec_with_args).size(size).get_df()
  df_data_2 = DataGenerator(rand_spec_with_args).size(size).get_df()
  assert df_data_1.shape == df_data_2.shape
  assert  not df_data_1.equals(df_data_2)


@pytest.mark.parametrize("size", [10**2, 10**3])
def test_create_df_with_all_methods(rand_spec_all_methods, size):
  """
  Test spec that uses ALL available DataGenerator methods.
  Validates complete method coverage.
  """
  df_data = DataGenerator(rand_spec_all_methods).size(size).get_df()
  assert df_data.shape[0] == size
  
  # Check NPCore methods
  assert "id" in df_data.columns  # integers
  assert "code" in df_data.columns  # int_zfilled
  assert "price" in df_data.columns  # floats
  assert "rating" in df_data.columns  # floats_normal
  assert "category" in df_data.columns  # distincts
  assert "tier" in df_data.columns  # distincts_prop
  assert "created_at" in df_data.columns  # unix_timestamps
  assert "uuid" in df_data.columns  # uuid4
  assert "is_verified" in df_data.columns  # booleans
  
  # Check PyCore correlated columns
  assert "device" in df_data.columns  # distincts_map
  assert "os" in df_data.columns  # distincts_map
  assert "trade_type" in df_data.columns  # distincts_map_prop
  assert "trade_side" in df_data.columns  # distincts_map_prop
  assert "industry" in df_data.columns  # distincts_multi_map
  assert "sub_industry" in df_data.columns  # distincts_multi_map
  assert "company_size" in df_data.columns  # distincts_multi_map
  assert "ip_address" in df_data.columns  # complex_distincts
  
  # Validate data types and ranges
  assert df_data["id"].between(1, 1000000).all()
  assert df_data["is_verified"].isin([True, False]).all()
  assert df_data["category"].isin(["A", "B", "C"]).all()
  assert df_data["tier"].isin(["gold", "silver", "bronze"]).all()


@pytest.mark.parametrize("size", [10**2])
def test_create_df_with_multiple_transformers(rand_spec_with_transformers, size):
  """
  Test that multiple transformers on same column are applied in sequence.
  """
  df_data = DataGenerator(rand_spec_with_transformers).size(size).get_df()
  
  # Price has 2 transformers: multiply by 1.1, then round
  assert all(isinstance(price, float) for price in df_data["price"])
  # All prices should be > 11.0 (min 10.0 * 1.1) and < 110.0 (max 100.0 * 1.1)
  assert df_data["price"].min() >= 11.0
  assert df_data["price"].max() <= 110.0


@pytest.mark.parametrize("size", [10**2])
def test_correlated_columns_distinct_map(rand_spec_with_related_columns, size):
  """
  Test distincts_map creates valid parent-child relationships.
  """
  df_data = DataGenerator(rand_spec_with_related_columns).size(size).get_df()
  
  # Check device_type and os_type correlation
  for _, row in df_data.iterrows():
    device = row["device_type"]
    os = row["os_type"]
    if device == "smartphone":
      assert os in ["android", "iOS"]
    elif device == "desktop":
      assert os in ["linux", "windows", "macos"]


@pytest.mark.parametrize("size", [10**2])
def test_complex_distincts_ip_address(rand_spec_all_methods, size):
  """
  Test complex_distincts generates valid IP addresses.
  """
  df_data = DataGenerator(rand_spec_all_methods).size(size).get_df()
  
  # Validate IP format: x.x.x.x
  for ip in df_data["ip_address"]:
    parts = ip.split(".")
    assert len(parts) == 4
    # First octet should be from ["192", "172", "10"]
    assert parts[0] in ["192", "172", "10"]
    # Other octets should be numbers
    for part in parts[1:]:
      assert 0 <= int(part) <= 255



def test_checkpoint_surface_is_gone():
  """AC5.3: no db_checkpoint, no option."""
  g = DataGenerator({"id": {"method": "pk"}})
  assert not hasattr(g, "db_checkpoint")
  assert not hasattr(g, "option")


@pytest.fixture
def every_np_method(rand_spec_all_methods):
  dates = dict(method="dates", kwargs=dict(start="2024-01-01", end="2024-12-31", date_format="%Y-%m-%d"))
  return {**rand_spec_all_methods, "day": dates}


def test_generator_leaves_global_numpy_state_untouched(every_np_method, tmp_path):
  """AC4.1: construct, get_df, one stream_dict microbatch, one batch write."""
  before = pickle.dumps(np.random.get_state())
  gen = DataGenerator(every_np_method, seed=1).size(10)
  gen.get_df()
  next(gen.stream_dict())
  gen.write.format("csv").save(str(tmp_path / "out"))
  assert pickle.dumps(np.random.get_state()) == before


def test_same_seed_generators_return_identical_frames(every_np_method):
  """AC4.2: uuid4 included; one generator's rng advances across batches."""
  gen = DataGenerator(every_np_method, seed=5).size(200)
  one = gen.get_df()
  assert one.equals(DataGenerator(every_np_method, seed=5).size(200).get_df())
  assert not gen.get_df().equals(one)
  assert not one.equals(DataGenerator(every_np_method, seed=6).size(200).get_df())


def test_another_generator_running_in_between_does_not_change_a(every_np_method):
  """AC4.3"""
  expected = DataGenerator(every_np_method, seed=5).size(200).get_df()
  a = DataGenerator(every_np_method, seed=5).size(200)
  DataGenerator(every_np_method, seed=6).size(200).get_df()
  assert a.get_df().equals(expected)


def test_callable_spec_is_evaluated_once_per_get_df_and_per_microbatch():
  """Lazy-spec guard (PLAN §3): validation evaluates it once, then once per batch."""
  calls = []
  def spec():
    calls.append(1)
    return {"n": dict(method="integers", kwargs=dict(min=0, max=9))}
  gen = DataGenerator(spec, seed=1).size(2)
  gen.get_df()
  assert len(calls) == 2
  stream = gen.stream_dict(min_throughput=10**4, max_throughput=10**4)
  for _ in range(4): next(stream)
  assert len(calls) == 4


@pytest.mark.parametrize("method, expected", [
  ("dates", {"2024-01-01"}),
  ("unix_timestamps", set(range(1704067200, 1704153600))),
])
def test_documented_date_spec_without_date_format_generates(method, expected):
  spec = {"d": {"method": method, "kwargs": {"start": "2024-01-01", "end": "2024-01-02"}}}
  df = DataGenerator(spec, seed=1).size(1000).get_df()
  assert len(df) == 1000
  assert set(df["d"].tolist()) <= expected


# FR13 goldens: seed 42, 10**3 rows, UTC run. A deliberate output change rewrites its line here, the commit body saying why.
GOLDEN_SHA256 = {
  "integers": "953f31ff97cb998eb78ce3b16215f99bfda4fbf2628b856cd5755e97d80b195a",
  "int_zfilled": "56c7e77935c45862e81c70fc019572f234e2c2faca802353b7bfc31aebdd4128",
  "floats": "1e59355e2f889ba13ca3e3e8adc355e9cb5070c9bdf6494a363c641743f0e5f0",
  "floats_normal": "a780eb25f39ca93c4fe9c86aedf074c2901058f2638aa88442567adc3f2c4780",
  "distincts": "9ed5a4bc7ab4166a007da955731e00f82080182feb6507edec09d7406c3376e2",
  "distincts_prop": "a551262b37e7743f62bf46d60fe60b13dc9fa5ca000ca3d62f589d0bf250d0dc",
  "unix_timestamps": "4dbe45709175a998c32b04c4617677ee5cf6933e60b61ee3f56a467cea23f9f6",
  "uuid4": "375ea08389dbdd1ff08caf390bff4c158bfeea06a7f66e13a22254e2bfa57b4b",
  "booleans": "da7a8360dd086fc14e1fe7b7e6b42d927807a434eb4dea876848fc03cec8e794",
  "dates": "0f3e14d4485a3418bcb304c7f9618b63547194d4f3e0d970a528b821e0cbb42e",
  "distincts_map": "6dd39ea7e62ff23b7c36d4f5748f6edb65f2ec248aac062c47c4048113a85dad",
  "distincts_multi_map": "84522aea46e2b39bfa4b591f479ad82bf38108910c6e9cd4e2ed44301daf7e5b",
  "distincts_map_prop": "563b3d7fc27913cb65d710b98474754cb79eca1611cbae54fe5669a80d0b06ce",
  "complex_distincts": "880ef59af262594f18ddd705076dd0fe8ed06f2b961d750b917b498e01d30a33",
}


def test_golden_covers_every_numpy_method():
  from benchmarks.speed import SAMPLE_KWARGS
  from rand_engine.main._rand_generator import RandGenerator
  assert set(GOLDEN_SHA256) == set(SAMPLE_KWARGS) - {"pk", "fk"} == set(RandGenerator({}).map_methods()) - {"pk", "fk"}


@pytest.mark.parametrize("method", sorted(GOLDEN_SHA256))
def test_golden_seeded_output(method):
  import hashlib
  import json
  from benchmarks.speed import column
  df = DataGenerator({"c": column(method)}, seed=42).size(10**3).get_df()
  assert hashlib.sha256(json.dumps(df.to_dict("list")).encode()).hexdigest() == GOLDEN_SHA256[method]


def test_golden_multi_column_draw_order():
  import hashlib
  import json
  from benchmarks.speed import SINK_SPEC
  df = DataGenerator(SINK_SPEC, seed=42).size(10**3).get_df()
  assert hashlib.sha256(json.dumps(df.to_dict("list")).encode()).hexdigest() == "3b0464af85f501117a2be790d55ac1bd856a004f6745f781d317dabcc9dcb10f"
