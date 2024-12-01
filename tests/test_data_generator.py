import os
import time
import pandas as pd

from rand_engine.main.data_generator import DataGenerator

from tests.fixtures.fixtures_transformers import wsl_transformer
from tests.fixtures.fixtures_metadata import (
    metadata_case_0,
    metadata_case_1,
    metadata_case_2,
    metadata_case_wsl
)

from tests.fixtures.fixtures_integrations import (
    dataframe_size,
    microbatch_size,
    path_csv_test,
    size_in_mb
)



def test_create_pandas_df_const(dataframe_size, metadata_case_0):
  data_gen = DataGenerator()
  df_data = data_gen.create_pandas_df(dataframe_size, metadata_case_0)
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_variable(dataframe_size, metadata_case_1):
  data_gen = DataGenerator()
  df_data = data_gen.create_pandas_df(dataframe_size, metadata_case_1)
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_complex(dataframe_size, metadata_case_2):
  data_gen = DataGenerator()
  df_data = data_gen.create_pandas_df(dataframe_size, metadata_case_2)
  assert df_data.shape[0] == dataframe_size


def test_create_pandas_df_wsl(dataframe_size, metadata_case_wsl, wsl_transformer):
  data_gen = DataGenerator()
  df_data = data_gen.create_pandas_df(dataframe_size, metadata_case_wsl, transformer=wsl_transformer)
  pd.set_option('display.max_colwidth', None)
  assert df_data.shape[0] == dataframe_size


def test_create_streaming_records(microbatch_size, metadata_case_1):
  data_gen = DataGenerator()
  streaming = data_gen.create_streaming_records(
    microbatch_size=microbatch_size, 
    metadata=metadata_case_1,
    min_throughput=5,
    max_throughput=10)
  
  counter, start_time = 0, time.time()
  for record in streaming:
    elapsed_time = time.time() - start_time
    counter += 1
    if elapsed_time > 1: break
  assert counter > 5
  assert counter <= 10
  assert type(record) == dict


def test_create_file_with_streaming(microbatch_size, size_in_mb, metadata_case_1, path_csv_test):
  data_gen = DataGenerator()
  data_gen.create_csv_file(microbatch_size, size_in_mb, metadata_case_1, path=path_csv_test)
  file_size = os.path.getsize(path_csv_test)
  assert file_size > size_in_mb * 10**6

    

# def test_web_log_server_streaming(dataframe_size, metadata_case_web_log_server, web_server_log_transformer):
#   bulk_rand_engine = BulkRandEngine()
#   df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata_case_web_log_server)
#   df_transformed = web_server_log_transformer(df)
#   for record in bulk_rand_engine.create_streaming_series(df_transformed):
#       print(record)


# def test_create_file(metadata_case_web_log_server, web_server_log_transformer):
#     bulk_rand_engine = BulkRandEngine()
#     path_test = './test_outputs/test.log'
#     bulk_rand_engine.microbatch_file_with_streaming(path_test, metadata_case_web_log_server, web_server_log_transformer, 10**3, 10**7)

