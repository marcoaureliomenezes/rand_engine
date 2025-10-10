import pytest
import numpy as np
from random import randint

from rand_engine.utils.update import Changer
from rand_engine.interfaces.i_random_spec import IRandomSpec
from rand_engine.core import Core
from rand_engine.utils.distincts import DistinctUtils




class WebServerLog(IRandomSpec):

  def __init__(self):
    pass

  def debugger(self):
    """Debug method for testing purposes."""
    pass

  def metadata(self):
    return {
    "ip_address": dict(
      method=Core.gen_complex_distincts,
      kwargs=dict(
        pattern="x.x.x.x",  replacement="x", 
        templates=[
          {"method": Core.gen_distincts, "parms": dict(distinct=["172", "192", "10"])},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=128)}
        ]
      )),
    "identificador": dict(method=Core.gen_distincts, kwargs=dict(distinct=["-"])),
    "user": dict(method=Core.gen_distincts, kwargs=dict(distinct=["-"])),
    # "datetime": dict(
    #   method=Core.gen_datetimes,
    #   parms=dict(start='2024-07-05', end='2024-07-06', format_in="%Y-%m-%d", format_out="%d/%b/%Y:%H:%M:%S")
    # ),
    "http_version": dict(
      method=Core.gen_distincts,
      kwargs=dict(distinct=DistinctUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1))
    ),
    "campos_correlacionados_proporcionais": dict(
      method=       Core.gen_distincts,
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      kwargs=        dict(distinct=DistinctUtils.handle_distincts_lvl_3({
                        "GET /home": [("200", 7),("400", 2), ("500", 1)],
                        "GET /login": [("200", 5),("400", 3), ("500", 1)],
                        "POST /login": [("201", 4),("404", 2), ("500", 1)],
                        "GET /logout": [("200", 3),("400", 1), ("400", 1)]
        }))
    ),
    "object_size": dict(method=Core.gen_ints, kwargs=dict(min=0, max=10000)),
  }


  def transformer(self, df):
    df['wsl'] = df['ip_address'] + ' ' + df['identificador'] + ' ' + df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
                        df['http_request'] + ' ' + df['http_version'] + '" ' + ' ' + df['http_status'] + ' ' + df['object_size'].astype(str)


@pytest.fixture(scope="module")
def web_server_log():
  return WebServerLog()

# @pytest.fixture(scope="function")
# def wsl_transformer():
#   return lambda df: df['ip_address'] + ' ' + df['identificador'] + ' ' + df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
#                         df['http_request'] + ' ' + df['http_version'] + '" ' + df['http_status'] + ' ' + df['object_size'].astype(str)



# @pytest.fixture(scope="function")
# def update_transformer():
#   transformer = Changer(cols_to_change=["campo_float", "campo_int"]).updater
#   return transformer