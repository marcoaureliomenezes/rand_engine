import pytest
import os


@pytest.fixture(scope="function")
def df_size():
    return 5

@pytest.fixture(scope="function")
def microbatch_size():
    return 10**5

@pytest.fixture(scope="function")
def batch_size():
    return 10**5


@pytest.fixture(scope="function")
def size_in_mb():
   return 20

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
def base_path_files_test():
  return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_outputs")
