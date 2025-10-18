from datetime import datetime as dt

from rand_engine.utils.update import Changer
from rand_engine.templates.i_random_spec import IRandomSpec




class WebServerLogs(IRandomSpec):
  """
  Template for generating web server access logs in Apache/Nginx format.
  
  Generates realistic log entries with:
  - IP addresses
  - Timestamps  
  - HTTP requests and status codes (correlated)
  - HTTP versions (weighted distribution)
  - Response sizes
  
  Example output:
    172.45.123.89 - - [15/Oct/2024:14:23:45 -0700] "GET /home HTTP/1.1" 200 1234
  """

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
          pattern="x.x.x.x",
          replacement="x", 
          templates=[
            {"method": "distincts", "parms": dict(distincts=["172", "192", "10"])},
            {"method": "integers", "parms": dict(min=0, max=255)},
            {"method": "integers", "parms": dict(min=0, max=255)},
            {"method": "integers", "parms": dict(min=0, max=128)}
          ]
        )
      ),
      "identificador": dict(
        method="distincts",
        kwargs=dict(distincts=["-"])
      ),
      "user": dict(
        method="distincts",
        kwargs=dict(distincts=["-"])
      ),
      "datetime": dict(
        method="unix_timestamps",
        kwargs=dict(start='2024-07-05', end='2024-07-06', format="%Y-%m-%d"),
        transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%d/%b/%Y:%H:%M:%S")]
      ),
      "http_version": dict(
        method="distincts_prop",
        kwargs=dict(distincts={"HTTP/1.1": 7, "HTTP/1.0": 3})
      ),
      "request_status": dict(
        method="distincts_map_prop",
        cols=["http_request", "http_status"],
        kwargs=dict(distincts={
          "GET /home": [("200", 7), ("400", 2), ("500", 1)],
          "GET /login": [("200", 5), ("400", 3), ("500", 1)],
          "POST /login": [("201", 4), ("404", 2), ("500", 1)],
          "GET /logout": [("200", 3), ("400", 1), ("500", 1)]
        })
      ),
      "object_size": dict(method="integers", kwargs=dict(min=0, max=10000)),
    }


  def transformers(self):
    """
    Applies transformations to combine all fields into Apache Common Log Format.
    
    Format: IP - - [datetime timezone] "request version" status size
    Example: 172.45.123.89 - - [15/Oct/2024:14:23:45 -0700] "GET /home HTTP/1.1" 200 1234
    
    Returns:
        List of transformer functions to be applied sequentially
    """
    _transformers = [
      lambda df: df.assign(
        log_entry=
          df['ip_address'] + ' ' + 
          df['identificador'] + ' ' + 
          df['user'] + ' [' + 
          df['datetime'] + ' -0700] "' + 
          df['http_request'] + ' ' + 
          df['http_version'] + '" ' + 
          df['http_status'] + ' ' + 
          df['object_size'].astype(str)
      ),
      # Keep only the final log entry column
      lambda df: df[['log_entry']]
    ]
    return _transformers