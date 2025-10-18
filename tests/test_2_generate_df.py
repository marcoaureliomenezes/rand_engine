import time
import pytest
from rand_engine.main.data_generator import DataGenerator
from datetime import datetime as dt
from rand_engine.utils.distincts_utils import DistinctsUtils
from tests.fixtures.f2_templates import update_transformer
from tests.fixtures.f1_right_specs import (
    rand_spec_with_kwargs,
    rand_spec_with_args,
    rand_spec_with_related_columns,
    rand_spec_case_1_transformer,
    rand_spec_lambda_with_kwargs
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
def test_create_df_simple_with_inline_transformer(rand_spec_case_1_transformer, size):
  df_data = DataGenerator(rand_spec_case_1_transformer).size(size).get_df()
  assert df_data.shape[0] == size
  assert "created_at" in df_data.columns



@pytest.mark.parametrize("size", [10**1, 10**2, 10**3])
def test_pandas_df_transformer(size, rand_spec_with_args):
  df_data_1 = DataGenerator(rand_spec_with_args).size(size).get_df()
  transformers = [
    lambda df: df.assign(created_at=df["created_at"].apply(
      lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))),
  ]
  df_data_2 = DataGenerator(rand_spec_with_args).transformers(transformers).size(size).get_df()
  assert df_data_1.shape[0] == size
  assert df_data_2.shape[0] == size
  assert "created_at" in df_data_2.columns



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


# def test_create_pandas_df_wsl(df_size, rand_spec_case_wsl, wsl_transformer):
#   df_data = DataGenerator(rand_spec_case_wsl).generate_pandas_df(df_size).size(df_size).get_df()
#   pd.set_option('display.max_colwidth', None)
#   assert df_data.shape[0] == df_size

