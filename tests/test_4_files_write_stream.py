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
    ("csv", "gzip", "/streaming/gzip/clients.csv"),
    ("csv", "gzip", "/streaming/gzip/clients.csv.gzip"),
    ("csv", "zip", "/streaming/zip/clients.csv.zip"),
    ("json", None, "/streaming/default/clients.json"),
    ("json", "gzip", "/streaming/gzip/clients.json"),
    ("parquet", None, "/streaming/default/clients.parquet"),
    ("parquet", "gzip", "/streaming/gzip/clients.parquet"),
    ("parquet", "snappy", "arquivo.parquet")
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
      .writeStream
      .size(df_size)
      .mode("overwrite")
      .format(format_type)
      .option("compression", compression)
      .option("timeout", 0.1)
      .trigger(frequency=0.01)
      .start(path)
  )
  assert True
