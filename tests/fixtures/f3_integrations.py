import pytest


@pytest.fixture(scope="function")
def df_size():
    return 5

@pytest.fixture(scope="function")
def microbatch_size():
    return 10**4

@pytest.fixture(scope="function")
def batch_size():
    return 10**4


@pytest.fixture(scope="function")
def size_in_mb():
   return 20

@pytest.fixture(scope="function", autouse=True)
def create_output_dir(tmp_path):
  return tmp_path


@pytest.fixture(scope="function")
def base_path_files_test(create_output_dir):
  return str(create_output_dir)
