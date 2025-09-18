import os
import time
import glob
import pandas as pd

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.fixtures_transformers import wsl_transformer
from tests.fixtures.fixtures_random_spec import (
    rand_spec_case_0,
    rand_spec_case_1,
    rand_spec_case_2,
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


def test_create_pandas_df_const(dataframe_size, rand_spec_case_0):
  df_data = DataGenerator(rand_spec_case_0).generate_pandas_df(dataframe_size).get_df()
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_variable(dataframe_size, rand_spec_case_1):
  df_data = DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).get_df()
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_complex(dataframe_size, rand_spec_case_2):
  df_data = DataGenerator(rand_spec_case_2).generate_pandas_df(dataframe_size).get_df()
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_wsl(dataframe_size, rand_spec_case_wsl, wsl_transformer):
  df_data = DataGenerator(rand_spec_case_wsl).generate_pandas_df(dataframe_size).get_df()
  pd.set_option('display.max_colwidth', None)
  assert df_data.shape[0] == dataframe_size


def test_create_stream_dict(microbatch_size, rand_spec_case_1):
  counter, start_time = 0, time.time()
  stream = DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).stream_dict(min_throughput=5, max_throughput=10)
  for record in stream:
    elapsed_time = time.time() - start_time
    counter += 1
    if elapsed_time > 1: break
  assert counter > 5
  assert counter <= 10
  assert type(record) == dict

