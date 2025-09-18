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


# def test_generate_csv(dataframe_size, rand_spec_case_1, parms_file_writer):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["csv_none"]["format"]) \
#     .load(parms_file_writer["csv_none"]["path"])
#   df_to_assert = pd.read_csv(parms_file_writer["csv_none"]["path"])
#   assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))

# def test_generate_csv_gzip(dataframe_size, rand_spec_case_1, parms_file_writer):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["csv_gzip"]["format"]) \
#     .option("compression", parms_file_writer["csv_gzip"]["compression"]) \
#     .load(parms_file_writer["csv_gzip"]["path"])
#   df_to_assert = pd.read_csv(f'{parms_file_writer["csv_gzip"]["path"]}.gzip', compression=parms_file_writer["csv_gzip"]["compression"])
#   assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))


# def test_generate_csv_zip(dataframe_size, rand_spec_case_1, parms_file_writer):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["csv_zip"]["format"]) \
#     .option("compression", parms_file_writer["csv_zip"]["compression"]) \
#     .load(parms_file_writer["csv_zip"]["path"])
#   df_to_assert = pd.read_csv(f'{parms_file_writer["csv_zip"]["path"]}.zip', compression=parms_file_writer["csv_zip"]["compression"])
#   assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))


# def test_generate_parquet(dataframe_size, rand_spec_case_1, parms_file_writer):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["parquet_none"]["format"]) \
#     .load(parms_file_writer["parquet_none"]["path"])
#   df_to_assert = pd.read_parquet(parms_file_writer["parquet_none"]["path"])
#   assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))
    

# def test_generate_csvs(microbatch_size, rand_spec_case_1, parms_file_writer, size_in_mb):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["csvs_gzip"]["format"]) \
#     .incr_load(parms_file_writer["csvs_gzip"]["path"], size_in_mb)
#   files = glob.glob(f'{parms_file_writer["csvs_gzip"]["path"]}/*')
#   df_to_assert = pd.concat([pd.read_csv(file) for file in files])
#   print(df_to_assert)
#   size_dir = [os.path.getsize(path) for path in glob.glob(f'{parms_file_writer["csvs_gzip"]["path"]}/*')]
#   real_size_mb = sum(size_dir)/ 2**20
#   assert real_size_mb >= size_in_mb and real_size_mb <= size_in_mb * 1.3


# def test_generate_parquets(microbatch_size, rand_spec_case_1, parms_file_writer, size_in_mb):
#   DataGenerator(rand_spec_case_1).generate_pandas_df(microbatch_size).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["parquets_none"]["format"]) \
#     .incr_load(parms_file_writer["parquets_none"]["path"], size_in_mb)
#   df_to_assert = pd.read_parquet(f'{parms_file_writer["parquets_none"]["path"]}')
#   size_dir = [os.path.getsize(path) for path in glob.glob(f'{parms_file_writer["parquets_none"]["path"]}/*')]
#   real_size_mb = sum(size_dir)/ 2**20
#   print(df_to_assert)
#   assert real_size_mb >= size_in_mb and real_size_mb <= size_in_mb * 1.3
  

def test_generate_json(dataframe_size, rand_spec_case_1, parms_file_writer):
  def transformer(df):
    # transform all pandas columns of type Timestamp to string in the format 'YYYY-MM-DDTHH:MM:SS'
    for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
      df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
    return df
  DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size, transformer=transformer).write() \
    .mode("overwrite") \
    .format(parms_file_writer["json_none"]["format"]) \
    .option("encoding", "utf-8") \
    .option("orient", "records") \
    .load(parms_file_writer["json_none"]["path"])
  df_to_assert = pd.read_json(parms_file_writer["json_none"]["path"])
  assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))
  time.sleep(100)
