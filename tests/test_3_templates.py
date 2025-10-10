import time

from rand_engine.main import RandEngine
from tests.fixtures.f2_templates import (
    web_server_log
)


from tests.fixtures.f3_integrations import (
    create_output_dir,
    dataframe_size,
    microbatch_size,
    batch_size,
    parms_file_writer,
    size_in_mb
)


def test_pandas_df_kwargs(dataframe_size, web_server_log):
  metadata = web_server_log.metadata()
  df_data = RandEngine(metadata).get_df(dataframe_size)
  print(df_data.head(5))
  assert df_data.shape[0] == dataframe_size