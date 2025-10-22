import pytest
import os
import pandas as pd
import glob
import time
import threading

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_right_specs import (
    rand_spec_with_kwargs,
    rand_spec_with_args,
    rand_spec_case_1_transformer,
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


@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "/single_file/default/clients"),
    ("csv", "gzip", "/single_file/gzip/clients.csv"),
    ("csv", "gzip", "/single_file/gzip/clients.csv.gzip"),
    ("csv", "zip", "/single_file/zip/clients.csv.zip"),
    ("json", None, "/single_file/default/clients.json"),
    ("json", "gzip", "/single_file/gzip/clients.json"),
    ("parquet", None, "/single_file/default/clients.parquet"),
    ("parquet", "gzip", "/single_file/gzip/clients.parquet")
])
def test_writing_single_file(
  df_size,
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .write
      .size(df_size)
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 1)
      .mode("overwrite")
      .save(path)
  )
  assert True
 

@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "/multi_files/default/clients"),
    ("csv", "gzip", "/multi_files/gzip/clients.csv"),
    ("csv", "gzip", "/multi_files/gzip/clients.csv.gzip"),
    ("csv", "zip", "/multi_files/zip/clients.csv.zip"),
    ("json", None, "/multi_files/default/clients.json"),
    ("json", "gzip", "/multi_files/gzip/clients.json"),
    ("parquet", None, "/multi_files/default/clients.parquet"),
    ("parquet", "gzip", "/multi_files/gzip/clients.parquet"),
    # ("parquet", "snappy", "arquivo.parquet")
])
def test_writing_multiple_files(
  df_size,
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .write
      .size(df_size)
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 5)
      .mode("overwrite")
      .save(path)
  )
  assert True
