import pytest
import os


@pytest.fixture(scope="function")
def dataframe_size():
    return 5

@pytest.fixture(scope="function")
def microbatch_size():
    return 10**4

@pytest.fixture(scope="function")
def batch_size():
    return 10**5


@pytest.fixture(scope="function")
def size_in_mb():
   return 2

def delete_dir_recursive(path):
  if os.path.exists(path):
    for file in os.listdir(path):
      if os.path.isdir(os.path.join(path, file)):
        delete_dir_recursive(os.path.join(path, file))
      else: os.remove(os.path.join(path, file))
    os.rmdir(path)


@pytest.fixture(scope="module", autouse=True)
def create_output_dir():
  output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_outputs")
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  yield
  # delete the directory after the test recursively
  delete_dir_recursive(output_dir)


@pytest.fixture(scope="function")
def parms_file_writer():
  output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_outputs")
  return {
    "csv_none": {"path": f"{output_dir}/arquivo.csv", "format": "csv", "compression": None},
    "csv_gzip": {"path": f"{output_dir}/arquivo.csv", "format": "csv", "compression": "gzip"},
    "csvs_gzip": {"path": f"{output_dir}/csvs_gzip", "format": "csv", "compression": "gzip"},
    "csv_zip": {"path": f"{output_dir}/arquivo.csv", "format": "csv", "compression": "zip"},
    "json_none": {"path": f"{output_dir}/arquivo.json", "format": "json", "compression": None},
    "json_gzip": {"path": f"{output_dir}/arquivo.json", "format": "json", "compression": "gzip"},
    "parquet_none": {"path": f"{output_dir}/arquivo_parquet_none", "format": "parquet", "compression": None},
    "parquets_none": {"path": f"{output_dir}/arquivo_parquets", "format": "parquet", "compression": None},
    "parquet_gzip": {"path": f"{output_dir}/arquivo_parquet_gzip", "format": "parquet", "compression": "gzip"},
    "parquet_snappy": {"path": f"{output_dir}/arquivo_parquet_snappy", "format": "parquet", "compression": "snappy"}
  }
