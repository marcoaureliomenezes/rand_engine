"""Intent: CONTRACT — writer-options-consumed-by-use (timeout/trigger read with defaults, never consumed)."""
import os
import pandas as pd
import glob
import time
import threading
import pytest
from types import SimpleNamespace
from rand_engine.file_handlers import _writer_stream

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_data_generator_specs_right import (
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
  assert elapsed_time > 0.1
  assert len(files) >= 1


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
  writer = (
    DataGenerator(rand_spec_with_kwargs)
      .writeStream
      .size(10**1)
      .format(format_type)
      .option("compression", compression)
      .option("timeout", 0.1)
      .trigger(frequency=0.01)
  )
  writer.mode("overwrite").start(path)
  writer.mode("append").start(path)

  elapsed_time = time.time() - start_time
  files = glob.glob(f"{path}/*")
  assert 0.2 < elapsed_time < 5
  assert len(files) >= 2


def test_stream_defaults_timeout_20s_trigger_1s(rand_spec_with_kwargs, base_path_files_test, monkeypatch):
  clock = {"now": 0.0}
  def sleep(seconds): clock["now"] += seconds
  monkeypatch.setattr(_writer_stream, "time", SimpleNamespace(time=lambda: clock["now"], sleep=sleep))
  path = f"{base_path_files_test}/csv/streaming/defaults/clients"
  DataGenerator(rand_spec_with_kwargs).writeStream.size(7).format("csv").start(path)
  files = glob.glob(f"{path}/*")
  assert len(files) == 21  # one file per 1 s tick until the clock passes 20 s
  assert len(pd.read_csv(files[0])) == 7
