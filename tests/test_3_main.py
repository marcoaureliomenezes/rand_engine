import numpy as np

from rand_engine.main import DataGenerator
from tests.fixtures.fixtures_transformers import update_transformer
from tests.fixtures.fixtures import (
    rand_spec_case_1,
    rand_spec_case_1_transformer,
    rand_spec_case_wsl
)

from tests.fixtures.fixtures_integrations import (
    create_output_dir,
    dataframe_size,
    microbatch_size,
    batch_size,
    parms_file_writer,
    size_in_mb
)


def test_pandas_df(dataframe_size, rand_spec_case_1):
  df_data = DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).get_df()
  #print(df_data)
  assert df_data.shape[0] == dataframe_size

def test_pandas_df_transformer(dataframe_size, rand_spec_case_1_transformer):
  df_data = DataGenerator(rand_spec_case_1_transformer).generate_pandas_df(dataframe_size).get_df()
  #print(df_data)
  assert df_data.shape[0] == dataframe_size
# def test_pandas_df_constant(dataframe_size, rand_spec_case_1):
#   df_data_1 = DataGenerator(rand_spec_case_1, seed=42).generate_pandas_df(dataframe_size).get_df()
#   df_data_2 = DataGenerator(rand_spec_case_1, seed=42).generate_pandas_df(dataframe_size).get_df()
#   assert df_data_1.equals(df_data_2)
#   assert df_data_1.shape == df_data_2.shape


# def test_pandas_df_variable(dataframe_size, rand_spec_case_1):
#   df_data_1 = DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).get_df()
#   df_data_2 = DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).get_df()
#   assert df_data_1.shape == df_data_2.shape
#   assert  not df_data_1.equals(df_data_2)


def test_pandas_df_transformer(dataframe_size, rand_spec_case_1, update_transformer):
  from datetime import datetime as dt
  df_data_1 = DataGenerator(rand_spec_case_1, seed=42).generate_pandas_df(dataframe_size).get_df()

  transformers = [
    lambda df: df.assign(campo_uuid=df.index.to_series().apply(lambda x: f"uuid-{x:05d}")),
    lambda df: df.assign(signup_datetime=df["signup_timestamp"].apply(lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")))
  ]
  df_data_2 = (
    DataGenerator(rand_spec_case_1, seed=42)
      .generate_pandas_df(dataframe_size, transformers=transformers)
      .get_df()
  )
  assert df_data_1.shape[0] == dataframe_size


# def test_create_pandas_df_wsl(dataframe_size, rand_spec_case_wsl, wsl_transformer):
#   df_data = DataGenerator(rand_spec_case_wsl).generate_pandas_df(dataframe_size).get_df()
#   pd.set_option('display.max_colwidth', None)
#   assert df_data.shape[0] == dataframe_size


# def test_create_stream_dict(microbatch_size, rand_spec_case_1):
#   counter, start_time = 0, time.time()
#   stream = DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).stream_dict(min_throughput=5, max_throughput=10)
#   for record in stream:
#     elapsed_time = time.time() - start_time
#     counter += 1
#     if elapsed_time > 1: break
#   assert counter > 5
#   assert counter <= 10
#   assert type(record) == dict

