import random
import pytest
from rand_engine.templates.web_server_logs import WebServerLogs, Changer



@pytest.fixture(scope="module")
def web_server_logs():
  return WebServerLogs()




@pytest.fixture(scope="function")
def update_transformer():
  transformer = Changer(cols_to_change=["campo_float", "campo_int"]).updater
  return transformer
