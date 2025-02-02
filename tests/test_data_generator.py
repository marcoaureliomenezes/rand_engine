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


def test_generate_csv(dataframe_size, rand_spec_case_1, parms_file_writer):
  DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["csv_none"]["format"]) \
    .load(parms_file_writer["csv_none"]["path"])
  df_to_assert = pd.read_csv(parms_file_writer["csv_none"]["path"])
  assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))

def test_generate_csv_gzip(dataframe_size, rand_spec_case_1, parms_file_writer):
  DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["csv_gzip"]["format"]) \
    .option("compression", parms_file_writer["csv_gzip"]["compression"]) \
    .load(parms_file_writer["csv_gzip"]["path"])
  df_to_assert = pd.read_csv(f'{parms_file_writer["csv_gzip"]["path"]}.gzip', compression=parms_file_writer["csv_gzip"]["compression"])
  assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))


def test_generate_csv_zip(dataframe_size, rand_spec_case_1, parms_file_writer):
  DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["csv_zip"]["format"]) \
    .option("compression", parms_file_writer["csv_zip"]["compression"]) \
    .load(parms_file_writer["csv_zip"]["path"])
  df_to_assert = pd.read_csv(f'{parms_file_writer["csv_zip"]["path"]}.zip', compression=parms_file_writer["csv_zip"]["compression"])
  assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))


def test_generate_parquet(dataframe_size, rand_spec_case_1, parms_file_writer):
  DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["parquet_none"]["format"]) \
    .load(parms_file_writer["parquet_none"]["path"])
  df_to_assert = pd.read_parquet(parms_file_writer["parquet_none"]["path"])
  assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))
    

def test_generate_csvs(microbatch_size, rand_spec_case_1, parms_file_writer, size_in_mb):
  DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["csvs_gzip"]["format"]) \
    .incr_load(parms_file_writer["csvs_gzip"]["path"], size_in_mb)
  files = glob.glob(f'{parms_file_writer["csvs_gzip"]["path"]}/*')
  df_to_assert = pd.concat([pd.read_csv(file) for file in files])
  print(df_to_assert)
  size_dir = [os.path.getsize(path) for path in glob.glob(f'{parms_file_writer["csvs_gzip"]["path"]}/*')]
  real_size_mb = sum(size_dir)/ 2**20
  assert real_size_mb >= size_in_mb and real_size_mb <= size_in_mb * 1.3


def test_generate_parquets(microbatch_size, rand_spec_case_1, parms_file_writer, size_in_mb):
  DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).write() \
    .mode("overwrite") \
    .format(parms_file_writer["parquets_none"]["format"]) \
    .incr_load(parms_file_writer["parquets_none"]["path"], size_in_mb)
  df_to_assert = pd.read_parquet(f'{parms_file_writer["parquets_none"]["path"]}')
  size_dir = [os.path.getsize(path) for path in glob.glob(f'{parms_file_writer["parquets_none"]["path"]}/*')]
  real_size_mb = sum(size_dir)/ 2**20
  print(df_to_assert)
  assert real_size_mb >= size_in_mb and real_size_mb <= size_in_mb * 1.3
  
