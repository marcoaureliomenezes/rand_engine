import time

from rand_engine.main.data_generator import DataGenerator
from tests.fixtures.f2_templates import (
    web_server_logs,
    update_transformer
)


from tests.fixtures.f3_integrations import (
    create_output_dir,
    df_size,
    microbatch_size,
    batch_size,
    size_in_mb
)


def test_generate_template_webserver_logs(df_size, web_server_logs):
  metadata = web_server_logs.metadata()
  df_data = DataGenerator(metadata).size(df_size).get_df()
  assert df_data.shape[0] == df_size


def test_generate_template_webserver_logs_with_transformers(df_size, web_server_logs):
  metadata = web_server_logs.metadata()
  transformers = web_server_logs.transformers()
  df_data = DataGenerator(metadata).transformers(transformers).size(df_size).get_df()
  assert df_data.shape[0] == df_size