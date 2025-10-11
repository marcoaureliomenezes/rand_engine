import time

from rand_engine.data_generator import DataGenerator
from tests.fixtures.f2_templates import (
    web_server_log
)


from tests.fixtures.f3_integrations import (
    create_output_dir,
    df_size,
    microbatch_size,
    batch_size,
    size_in_mb
)


def test_pandas_df_kwargs(df_size, web_server_log):
  metadata = web_server_log.metadata()
  df_data = DataGenerator(metadata).get_df(df_size)
  print(df_data.head(5))
  assert df_data.shape[0] == df_size


def test_pandas_df_kwargs(df_size, web_server_log):
  metadata = web_server_log.metadata()
  transformers = web_server_log.transformer()
  df_data = DataGenerator(metadata).transformers(transformers).get_df(df_size)
  print(df_data.head(5))
  assert df_data.shape[0] == df_size