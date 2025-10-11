import time

from rand_engine.main import RandEngine
from tests.fixtures.f2_templates import update_transformer
from tests.fixtures.f1_general import (
    rand_spec_case_1,
    rand_spec_case_2,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark,
    rand_engine_splitable_benchmark_baseline,
)

from tests.fixtures.f3_integrations import (
    dataframe_size,
    microbatch_size,
    batch_size,
)


def test_pandas_df_kwargs(dataframe_size, rand_spec_case_1):
  df_data = RandEngine(rand_spec_case_1).get_df(dataframe_size)
  assert df_data.shape[0] == dataframe_size




def test_pandas_df_args(dataframe_size, rand_spec_case_2):
  df_data = RandEngine(rand_spec_case_2).get_df(dataframe_size)
  assert df_data.shape[0] == dataframe_size


def test_pandas_df_transformer(dataframe_size, rand_spec_case_1_transformer):
  df_data = RandEngine(rand_spec_case_1_transformer).get_df(dataframe_size)
  assert df_data.shape[0] == dataframe_size


def test_pandas_df_constant(dataframe_size, rand_spec_case_1):
  df_data_1 = RandEngine(rand_spec_case_1, seed=True).get_df(dataframe_size)
  df_data_2 = RandEngine(rand_spec_case_1, seed=True).get_df(dataframe_size)
  assert df_data_1.equals(df_data_2)
  assert df_data_1.shape == df_data_2.shape

def test_pandas_df_constant_uuid(dataframe_size, rand_spec_case_2):
  df_data_1 = RandEngine(rand_spec_case_2, seed=True).get_df(dataframe_size)
  df_data_2 = RandEngine(rand_spec_case_2, seed=True).get_df(dataframe_size)
  assert df_data_1.equals(df_data_2)
  assert df_data_1.shape == df_data_2.shape


def test_pandas_df_variable(dataframe_size, rand_spec_case_1):
  df_data_1 = RandEngine(rand_spec_case_1).get_df(dataframe_size)
  df_data_2 = RandEngine(rand_spec_case_1).get_df(dataframe_size)
  assert df_data_1.shape == df_data_2.shape
  assert  not df_data_1.equals(df_data_2)


def test_pandas_df_transformer(dataframe_size, rand_spec_case_1, update_transformer):
  from datetime import datetime as dt       
  df_data_1 = RandEngine(rand_spec_case_1).get_df(dataframe_size)
  transformers = [
    lambda df: df.assign(created_at=df["created_at"].apply(
      lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"))),
  ]
  df_data_2 = RandEngine(rand_spec_case_1).transformers(transformers).get_df(dataframe_size)
  assert df_data_1.shape[0] == dataframe_size
  assert df_data_2.shape[0] == dataframe_size
  assert "created_at" in df_data_2.columns



def test_splitable_benchmark_baseline(dataframe_size, rand_engine_splitable_benchmark_baseline):
  dataframe_size = 10**6
  start_time = time.time()
  df_data = RandEngine(rand_engine_splitable_benchmark_baseline).get_df(dataframe_size)
  print(f"Elapsed time: {time.time() - start_time} seconds")
  assert df_data.shape[0] == dataframe_size


def test_splitable_benchmark(dataframe_size, rand_engine_splitable_benchmark):
  dataframe_size = 10**6
  start_time = time.time()
  df_data = RandEngine(rand_engine_splitable_benchmark).get_df(dataframe_size)
  print(f"Elapsed time: {time.time() - start_time} seconds")
  assert df_data.shape[0] == dataframe_size


# def test_create_pandas_df_wsl(dataframe_size, rand_spec_case_wsl, wsl_transformer):
#   df_data = RandEngine(rand_spec_case_wsl).generate_pandas_df(dataframe_size).get_df()
#   pd.set_option('display.max_colwidth', None)
#   assert df_data.shape[0] == dataframe_size


# def test_create_stream_dict(microbatch_size, rand_spec_case_1):
#   counter, start_time = 0, time.time()
#   stream = RandEngine(rand_spec_case_1).generate_pandas_df(microbatch_size).stream_dict(min_throughput=5, max_throughput=10)
#   for record in stream:
#     elapsed_time = time.time() - start_time
#     counter += 1
#     if elapsed_time > 1: break
#   assert counter > 5
#   assert counter <= 10
#   assert type(record) == dict

