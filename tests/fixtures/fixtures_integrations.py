import pytest

from rand_engine.core.distinct_core import DistinctCore
from rand_engine.core.numeric_core import NumericCore
from rand_engine.core.datetime_core import DatetimeCore
from rand_engine.main.dataframe_builder import BulkRandEngine
from rand_engine.core.distinct_utils import DistinctUtils


@pytest.fixture(scope="function")
def test_web_log_server(dataframe_size):
  bulk_rand_engine = BulkRandEngine()
  metadata = {
    "ip": dict(
      method=DistinctCore.gen_complex_distincts,
      parms=dict(
        pattern="x.x.x.x",  replacement="x", 
        templates=[
          {"method": DistinctCore.gen_distincts_typed, "parms": dict(distinct=["172", "192", "10"])},
          {"method": NumericCore.gen_ints, "parms": dict(min=0, max=255)},
          {"method": NumericCore.gen_ints, "parms": dict(min=0, max=255)},
          {"method": NumericCore.gen_ints, "parms": dict(min=0, max=128)}
        ]
      )),
    "identificador": dict(method=DistinctCore.gen_distincts_typed, parms=dict(distinct=["-"])),
    "user": dict(method=DistinctCore.gen_distincts_typed, parms=dict(distinct=["-"])),
    "datetime": dict(
      method=DatetimeCore.gen_datetimes, 
      parms=dict(start='2024-07-05', end='2024-07-06', format_in="%Y-%m-%d", format_out="%d/%b/%Y:%H:%M:%S")
    ),
    "http_version": dict(
      method=DistinctCore.gen_distincts_typed,
      parms=dict(distinct=DistinctUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1))
    ),
    "campos_correlacionados_proporcionais": dict(
      method=       DistinctCore.gen_distincts_typed,
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      parms=        dict(distinct=DistinctUtils.handle_distincts_lvl_3({
                        "GET /home": [("200", 7),("400", 2), ("500", 1)],
                        "GET /login": [("200", 5),("400", 3), ("500", 1)],
                        "POST /login": [("201", 4),("404", 2), ("500", 1)],
                        "GET /logout": [("200", 3),("400", 1), ("400", 1)]
        }))
    ),
    "object_size": dict(method=NumericCore.gen_ints, parms=dict(min=0, max=10000)),
  }
  df = bulk_rand_engine.create_pandas_df(dataframe_size, metadata)
  df_web_server_log = df['ip'] + ' ' + df['identificador'] + ' ' + df['user'] + ' [' + df['datetime'] + ' -0700] "' + \
                      df['http_request'] + ' ' + df['http_version'] + '" ' + df['http_status'] + ' ' + df['object_size'].astype(str)
  
  
  pd.set_option('display.max_colwidth', None)
  print(df_web_server_log)