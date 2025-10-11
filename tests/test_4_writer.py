import pytest
import os
import pandas as pd
import glob
import time

from rand_engine.main import RandEngine
from tests.fixtures.f1_general import (
    rand_spec_case_1,
    rand_spec_case_2,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark,
    rand_engine_splitable_benchmark_baseline,
)


from tests.fixtures.f3_integrations import (
    create_output_dir,
    dataframe_size,
    microbatch_size,
    batch_size,
    base_path_files_test,
    size_in_mb
)


@pytest.mark.parametrize("format_type,compression,file_name", [
    ("csv", None, "arquivo.csv"),
    ("csv", "gzip", "arquivo.csv"),
    ("csv", "zip", "arquivo.csv"),
    ("json", None, "arquivo.json"),
    ("json", "gzip", "arquivo.json"),
    ("parquet", None, "arquivo.parquet"),
    ("parquet", "gzip", "arquivo.parquet"),
    ("parquet", "snappy", "arquivo.parquet")
])
def test_pandas_df_kwargs(
  dataframe_size,
  rand_spec_case_1,
  base_path_files_test,
  format_type,
  compression,
  file_name
):
  path = f"{base_path_files_test}/{format_type}/{file_name}"
  _ = (
    RandEngine(rand_spec_case_1)
      .write(size=dataframe_size)
      .format(format_type)
      .option("compression", compression)
      .mode("overwrite")
      .load(path)
  )
  assert True
 


  #   "parquets_none": {"path": f"{output_dir}/arquivo_parquets", "format": "parquet", "compression": None},
  #   "csvs_gzip": {"path": f"{output_dir}/csvs_gzip", "format": "csv", "compression": "gzip"},

@pytest.mark.parametrize("format_type,compression,file_name", [
    ("csv", None, "arquivo.csv"),
    ("csv", "gzip", "arquivo.csv"),
    ("json", None, "arquivo.json"),
    ("json", "gzip", "arquivo.json"),
    ("parquet", None, "arquivo.parquet"),
    ("parquet", "snappy", "arquivo.parquet")
])
def test_generate_csvs(
  microbatch_size,
  rand_spec_case_1,
  size_in_mb,
  base_path_files_test,
  format_type,
  compression,
  file_name):
  path = f"{base_path_files_test}/{format_type}/{compression if compression else 'none'}/"
  _ = (
    RandEngine(rand_spec_case_1)
    .write(size=microbatch_size)
    .option("compression", compression)
    .mode("overwrite")
    .format(format_type)
    .incr_load(path, size_in_mb)
  )

  size_dir = [os.path.getsize(path) for path in glob.glob(f'{path}/*')]
  real_size_mb = sum(size_dir)/ 2**20
  assert real_size_mb >= size_in_mb and real_size_mb <= size_in_mb * 1.5


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
  

# def test_generate_json(dataframe_size, rand_spec_case_1, parms_file_writer):
#   def transformer(df):
#     # transform all pandas columns of type Timestamp to string in the format 'YYYY-MM-DDTHH:MM:SS'
#     for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
#       df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
#     return df
#   DataGenerator(rand_spec_case_1).generate_pandas_df(dataframe_size, transformer=transformer).write() \
#     .mode("overwrite") \
#     .format(parms_file_writer["json_none"]["format"]) \
#     .load(parms_file_writer["json_none"]["path"])
#   df_to_assert = pd.read_json(parms_file_writer["json_none"]["path"], lines=True)
#   assert df_to_assert.shape == (dataframe_size, len(rand_spec_case_1))
#   time.sleep(100)
