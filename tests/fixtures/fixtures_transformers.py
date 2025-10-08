import pytest
import numpy as np
from random import randint

from rand_engine.utils.update import Changer

@pytest.fixture(scope="function")
def wsl_transformer():
  return lambda df: df['ip_address'] + ' ' + df['identificador'] + ' ' + df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
                        df['http_request'] + ' ' + df['http_version'] + '" ' + df['http_status'] + ' ' + df['object_size'].astype(str)



@pytest.fixture(scope="function")
def update_transformer():
  transformer = Changer(cols_to_change=["campo_float", "campo_int"]).updater
  return transformer