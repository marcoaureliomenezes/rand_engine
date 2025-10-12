from datetime import datetime as dt    
import time

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f2_templates import update_transformer
from tests.fixtures.f1_general import (
    rand_spec_case_1,
    rand_spec_case_2,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark,
    rand_engine_splitable_benchmark_baseline,
)

from tests.fixtures.f3_integrations import (
    df_size,
    microbatch_size,
    batch_size,
)


def test_pandas_df_kwargs(df_size, rand_spec_case_1):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using keyword arguments.
  """
  df_data = DataGenerator(rand_spec_case_1).size(df_size).get_df()
  assert df_data.shape[0] == df_size


def test_pandas_df_args(df_size, rand_spec_case_2):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using positional arguments.
  """
  df_data = DataGenerator(rand_spec_case_2).size(df_size).get_df()
  print(df_data)
  assert df_data.shape[0] == df_size


def test_pandas_df_internal_transformer(df_size, rand_spec_case_1_transformer):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using a transformer function.
  """
  df_data = DataGenerator(rand_spec_case_1_transformer).size(df_size).get_df()
  assert df_data.shape[0] == df_size


def test_pandas_df_constant(df_size, rand_spec_case_1):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using a constant seed.
  """
  df_data_1 = DataGenerator(rand_spec_case_1, seed=True).size(df_size).get_df()
  df_data_2 = DataGenerator(rand_spec_case_1, seed=True).size(df_size).get_df()
  assert df_data_1.equals(df_data_2)
  assert df_data_1.shape == df_data_2.shape


def test_pandas_df_constant_uuid(df_size, rand_spec_case_2):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using a constant seed.
  """
  df_data_1 = DataGenerator(rand_spec_case_2, seed=True).size(df_size).get_df()
  df_data_2 = DataGenerator(rand_spec_case_2, seed=True).size(df_size).get_df()
  assert df_data_1.equals(df_data_2)
  assert df_data_1.shape == df_data_2.shape


def test_pandas_df_variable(df_size, rand_spec_case_1):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using a variable seed.
  """
  df_data_1 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
  df_data_2 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
  assert df_data_1.shape == df_data_2.shape
  assert  not df_data_1.equals(df_data_2)


def test_pandas_df_transformer(df_size, rand_spec_case_1, update_transformer):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows 
  using a global transformer function.
  """
  df_data_1 = DataGenerator(rand_spec_case_1).size(df_size).get_df()
  transformers = [
    lambda df: df.assign(created_at=df["created_at"].apply(
      lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))),
  ]
  df_data_2 = DataGenerator(rand_spec_case_1).transformers(transformers).size(df_size).get_df()
  assert df_data_1.shape[0] == df_size
  assert df_data_2.shape[0] == df_size
  assert "created_at" in df_data_2.columns



def test_splitable_benchmark_baseline(df_size, rand_engine_splitable_benchmark_baseline):
  df_size = 10**6
  start_time = time.time()
  df_data = DataGenerator(rand_engine_splitable_benchmark_baseline).size(df_size).get_df()
  print(f"Elapsed time: {time.time() - start_time} seconds")
  assert df_data.shape[0] == df_size


def test_splitable_benchmark(df_size, rand_engine_splitable_benchmark):
  df_size = 10**6
  start_time = time.time()
  df_data = DataGenerator(rand_engine_splitable_benchmark).size(df_size).get_df()
  print(f"Elapsed time: {time.time() - start_time} seconds")
  assert df_data.shape[0] == df_size


# def test_create_pandas_df_wsl(df_size, rand_spec_case_wsl, wsl_transformer):
#   df_data = DataGenerator(rand_spec_case_wsl).generate_pandas_df(df_size).size(df_size).get_df()
#   pd.set_option('display.max_colwidth', None)
#   assert df_data.shape[0] == df_size



