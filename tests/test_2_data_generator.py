from random import randint
import time
import pytest
from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f2_templates import update_transformer
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
def test_create_df_simple_with_args_spec(rand_spec_with_args, size):
  df_data = DataGenerator(rand_spec_with_args).size(size).get_df()
  assert df_data.shape[0] == size
  assert rand_spec_with_args.keys() == set(df_data.columns)



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

