
from datetime import datetime as dt    
import time

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f2_templates import update_transformer
from tests.fixtures.f1_general import (
    rand_spec_case_1,
    rand_spec_case_2,
    rand_spec_case_1_transformer,
    rand_engine_splitable_benchmark,
    rand_engine_splitable_benchmark_baseline,
)

from tests.fixtures.f3_integrations import (
    df_size,
    microbatch_size,
    batch_size,
)


def test_pandas_df_kwargs(df_size, rand_spec_case_1):
  """
  This test checks if the DataGenerator can generate a pandas DataFrame with the specified number of rows
  using keyword arguments.
  """
  df_data = DataGenerator(rand_spec_case_1).size(df_size).get_df()
  assert df_data.shape[0] == df_size




def test_create_stream_dict(microbatch_size, rand_spec_case_1):
  counter, start_time = 0, time.time()
  stream = DataGenerator(rand_spec_case_1).size(microbatch_size).stream_dict(min_throughput=5, max_throughput=10)
  for record in stream:
    elapsed_time = time.time() - start_time
    counter += 1
    if elapsed_time > 1: break
#   assert counter > 5
#   assert counter <= 10
#   assert type(record) == dict
