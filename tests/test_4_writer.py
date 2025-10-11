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
    df_size,
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
  df_size,
  rand_spec_case_1,
  base_path_files_test,
  format_type,
  compression,
  file_name
):
  path = f"{base_path_files_test}/{format_type}/{file_name}"
  _ = (
    RandEngine(rand_spec_case_1)
      .write(size=df_size)
      .format(format_type)
      .option("compression", compression)
      .mode("overwrite")
      .load(path)
  )
  assert True
 


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


