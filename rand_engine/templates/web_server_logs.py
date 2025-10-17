import pytest
from datetime import datetime as dt
from random import randint

from rand_engine.utils.update import Changer
from rand_engine.templates.i_random_spec import IRandomSpec
from rand_engine.utils.distincts_utils import DistinctsUtils




class WebServerLogs(IRandomSpec):

  def __init__(self):
    pass

  def debugger(self):
    """Debug method for testing purposes."""
    pass

  def metadata(self):
    return {
    "ip_address": dict(
      method="complex_distincts",
      kwargs=dict(
        pattern="x.x.x.x",  replacement="x", 
        templates=[
          {"method": "distincts", "parms": dict(distincts=["172", "192", "10"])},
          {"method": "integers", "parms": dict(min=0, max=255)},
          {"method": "integers", "parms": dict(min=0, max=255)},
          {"method": "integers", "parms": dict(min=0, max=128)}
        ]
      )),
    "identificador": dict(method="distincts", args=[["-"]]),
    "user": dict(method="distincts", args=[["-"]]),
    "datetime": dict(
      method="unix_timestamps",
      args=['2024-07-05', '2024-07-06', "%Y-%m-%d"],
      transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%d/%b/%Y:%H:%M:%S")]
    ),
    "http_version": dict(
      method="distincts",
      args=[DistinctsUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1)]
    ),
    "campos_correlacionados_proporcionais": dict(
      method=       "distincts",
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      kwargs=        dict(distincts=DistinctsUtils.handle_distincts_lvl_3({
                        "GET /home": [("200", 7),("400", 2), ("500", 1)],
                        "GET /login": [("200", 5),("400", 3), ("500", 1)],
                        "POST /login": [("201", 4),("404", 2), ("500", 1)],
                        "GET /logout": [("200", 3),("400", 1), ("400", 1)]
        }))
    ),
    "object_size": dict(method="integers", kwargs=dict(min=0, max=10000)),
  }


  def transformers(self):
    _transformers = [
      lambda df: df['ip_address'] + ' ' + df['identificador'] + ' ' + \
        df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
        df['http_request'] + ' ' + df['http_version'] + '" ' + \
        df['http_status'] + ' ' + df['object_size'].astype(str),
    ]
    return _transformers