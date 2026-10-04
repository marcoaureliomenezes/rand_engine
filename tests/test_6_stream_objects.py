
from datetime import datetime as dt    
from itertools import islice
import pytest

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f1_data_generator_specs_right import rand_spec_with_args

from tests.fixtures.f3_integrations import (
    df_size,
    batch_size,
)


def test_pandas_df_kwargs(df_size, rand_spec_with_args):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using keyword arguments.
  """
  df_data = DataGenerator(rand_spec_with_args).size(df_size).get_df()
  assert df_data.shape[0] == df_size




@pytest.mark.parametrize("size", [3, lambda: 3])
def test_create_stream_dict(size, rand_spec_with_args):
  """Intent: CONTRACT — writer-size-not-from-generator: stream_dict resolves int and callable size."""
  stream = DataGenerator(rand_spec_with_args).size(size).stream_dict(min_throughput=1000, max_throughput=1000)
  records = list(islice(stream, 3))
  assert [set(r) for r in records] == [set(rand_spec_with_args) | {"timestamp_created"}] * 3
