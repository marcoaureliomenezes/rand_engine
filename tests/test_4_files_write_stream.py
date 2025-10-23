import os
import pandas as pd
import glob
import time
import threading
import pytest

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_right_specs import (
    rand_spec_with_kwargs,
    rand_spec_with_args
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
    ("csv", None, "/streaming/default/clients"),
    ("csv", "gzip", "/streaming/gzip/clients"),
    ("csv", "zip", "/streaming/zip/clients"),
    ("csv", "bz2", "/streaming/bz2/clients"),
    ("json", None, "/streaming/default/clients"),
    ("json", "gzip", "/streaming/gzip/clients"),
    ("json", "zip", "/streaming/zip/clients"),
    ("json", "bz2", "/streaming/bz2/clients"),
    ("parquet", None, "/streaming/default/clients"),
    ("parquet", "gzip", "/streaming/gzip/clients"),
    ("parquet", "snappy", "/streaming/snappy/clients"),
    ("parquet", "zstd", "/streaming/zstd/clients"),
    ("parquet", "brotli", "/streaming/brotli/clients"),

    ])
def test_writing_multiple_files(
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  start_time = time.time()
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .writeStream
      .size(10**1)
      .mode("overwrite")
      .format(format_type)
      .option("compression", compression)
      .option("timeout", 0.1)
      .trigger(frequency=0.01)
      .start(path)
  )

  elapsed_time = time.time() - start_time
  files = glob.glob(f"{path}/*")
  assert elapsed_time > 0.1 and elapsed_time < 0.3
  assert len(files) < 10 and len(files) >= 2


@pytest.mark.parametrize("format_type,compression,file_path", [
    ("csv", None, "/streaming/default/clients"),
    ("csv", "gzip", "/streaming/gzip/clients"),
    ("csv", "zip", "/streaming/zip/clients"),
    ("csv", "bz2", "/streaming/bz2/clients"),
    ("json", None, "/streaming/default/clients"),
    ("json", "gzip", "/streaming/gzip/clients"),
    ("json", "zip", "/streaming/zip/clients"),
    ("json", "bz2", "/streaming/bz2/clients"),
    ("parquet", None, "/streaming/default/clients"),
    ("parquet", "gzip", "/streaming/gzip/clients"),
    ("parquet", "snappy", "/streaming/snappy/clients"),
    ("parquet", "zstd", "/streaming/zstd/clients"),
    ("parquet", "brotli", "/streaming/brotli/clients"),

    ])
def test_writing_multiple_files_append(
  rand_spec_with_kwargs,
  base_path_files_test,
  format_type,
  compression,
  file_path
):
  path = f"{base_path_files_test}/{format_type}/{file_path}"
  start_time = time.time()
  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .writeStream
      .size(10**1)
      .mode("overwrite")
      .format(format_type)
      .option("compression", compression)
      .option("timeout", 0.1)
      .trigger(frequency=0.01)
      .start(path)
  )

  _ = (
    DataGenerator(rand_spec_with_kwargs)
      .writeStream
      .size(10**1)
      .mode("append")
      .format(format_type)
      .option("compression", compression)
      .option("timeout", 0.1)
      .trigger(frequency=0.01)
      .start(path)
  )

  elapsed_time = time.time() - start_time
  files = glob.glob(f"{path}/*")
  assert elapsed_time > 0.1 and elapsed_time < 0.5
  assert len(files) < 20 and len(files) >= 3