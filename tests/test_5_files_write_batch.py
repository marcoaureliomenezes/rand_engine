import pytest
import os
import pandas as pd
import glob
import time
import threading

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_data_generator_specs_right import (
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
    ("csv", None, "single_file/default/clients"),
    ("csv", "gzip", "single_file/gzip/clients.csv"),
    ("csv", "zip", "single_file/zip/clients.csv.zip"),
    ("csv", "bz2", "single_file/bz2/clients.csv.bz2"),
    ("csv", "xz", "single_file/xz/clients.csv.xz"),
    ("json", None, "single_file/default/clients.json"),
    ("json", "gzip", "single_file/gzip/clients.json"),
    ("json", "zip", "single_file/zip/clients.json.zip"),
    ("json", "bz2", "single_file/bz2/clients.json.bz2"),
    ("json", "xz", "single_file/xz/clients.json.xz"),
    ("parquet", None, "single_file/default/clients.parquet"),
    ("parquet", "gzip", "single_file/gzip/clients.parquet"),
    ("parquet", "snappy", "single_file/snappy/clients.parquet"),
    ("parquet", "zstd", "single_file/zstd/clients.parquet"),
    ("parquet", "brotli", "single_file/brotli/clients.parquet"),
    ("parquet", "lz4", "single_file/lz4/clients.parquet"),
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
      .mode("overwrite")
      .save(path)
  )
  assert True
 

@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "multi_files_overwrite/default/clients"),
    ("csv", "gzip", "multi_files_overwrite/gzip/clients.csv"),
    ("csv", "zip", "multi_files_overwrite/zip/clients.csv.zip"),
    ("csv", "bz2", "multi_files_overwrite/bz2/clients.csv.bz2"),
    ("csv", "xz", "multi_files_overwrite/xz/clients.csv.xz"),
    ("json", None, "multi_files_overwrite/default/clients.json"),
    ("json", "gzip", "multi_files_overwrite/gzip/clients.json"),
    ("json", "zip", "multi_files_overwrite/zip/clients.json.zip"),
    ("json", "bz2", "multi_files_overwrite/bz2/clients.json.bz2"),
    ("json", "xz", "multi_files_overwrite/xz/clients.json.xz"),
    ("parquet", None, "multi_files_overwrite/default/clients.parquet"),
    ("parquet", "gzip", "multi_files_overwrite/gzip/clients.parquet"),
    ("parquet", "snappy", "multi_files_overwrite/snappy/clients.parquet"),
    ("parquet", "zstd", "multi_files_overwrite/zstd/clients.parquet"),
    ("parquet", "brotli", "multi_files_overwrite/brotli/clients.parquet"),
    ("parquet", "lz4", "multi_files_overwrite/lz4/clients.parquet"),
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
      .option("numFiles", 2)
      .mode("overwrite")
      .save(path)
  )
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .write
      .size(df_size)
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 2)
      .mode("overwrite")
      .save(path)
  )
  base_path = os.path.dirname(path)
  file_name = os.path.basename(path).split(".")[0]
  full_path = f"{base_path}/{file_name}"
  files = glob.glob(f"{full_path}/part_*")
  assert len(files) == 2


@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "multi_files_append/default/clients"),
    ("csv", "gzip", "multi_files_append/gzip/clients.csv"),
    ("csv", "zip", "multi_files_append/zip/clients.csv.zip"),
    ("csv", "bz2", "multi_files_append/bz2/clients.csv.bz2"),
    ("csv", "xz", "multi_files_append/xz/clients.csv.xz"),
    ("json", None, "multi_files_append/default/clients.json"),
    ("json", "gzip", "multi_files_append/gzip/clients.json"),
    ("json", "zip", "multi_files_append/zip/clients.json.zip"),
    ("json", "bz2", "multi_files_append/bz2/clients.json.bz2"),
    ("json", "xz", "multi_files_append/xz/clients.json.xz"),
    ("parquet", None, "multi_files_append/default/clients.parquet"),
    ("parquet", "gzip", "multi_files_append/gzip/clients.parquet"),
    ("parquet", "snappy", "multi_files_append/snappy/clients.parquet"),
    ("parquet", "zstd", "multi_files_append/zstd/clients.parquet"),
    ("parquet", "brotli", "multi_files_append/brotli/clients.parquet"),
    ("parquet", "lz4", "multi_files_append/lz4/clients.parquet"),
])
def test_writing_multiple_files_append(
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
      .option("numFiles", 2)
      .mode("overwrite")
      .save(path)
  )
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .write
      .size(df_size)
      .format(format_type)
      .option("compression", compression)
      .option("numFiles", 2)
      .mode("append")
      .save(path)
  )
  base_path = os.path.dirname(path)
  file_name = os.path.basename(path).split(".")[0]
  full_path = f"{base_path}/{file_name}"
  files = glob.glob(f"{full_path}/part_*")
  assert len(files) == 4