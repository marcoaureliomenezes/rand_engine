import pytest


@pytest.fixture(scope="function")
def dataframe_size():
    return 5

@pytest.fixture(scope="function")
def microbatch_size():
    return 10**3

@pytest.fixture(scope="function")
def size_in_mb():
   return 128


@pytest.fixture(scope="function")
def path_csv_test():
   return "test_outputs/test.csv"
