import random
import pytest
from rand_engine.templates.web_server_logs import WebServerLogs



@pytest.fixture(scope="module")
def web_server_logs():
  return WebServerLogs()

