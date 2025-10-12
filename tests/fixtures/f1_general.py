from datetime import datetime as dt
import pytest
import faker
import numpy as np

from rand_engine.core.core import Core
from rand_engine.utils.distincts import DistinctUtils


@pytest.fixture(scope="function")
def default_size():
    return 10**4


@pytest.fixture(scope="function")
def rand_spec_case_1():
  fake = faker.Faker(locale="pt_BR")
  return {
    "id":        dict(method=Core.gen_unique_identifiers, kwargs=dict(strategy="zint")),
    "age":         dict(method=Core.gen_ints, kwargs=dict(min=0, max=100)),
    "salary":      dict(method=Core.gen_floats, kwargs=dict(min=0, max=10**3, round=2)),
    "height":      dict(method=Core.gen_floats_normal, kwargs=dict(mean=10**3, std=10**1, round=2)),
    "is_active":   dict(method=Core.gen_distincts, kwargs=dict(distinct=[True, False])),
    "plan":        dict(method=Core.gen_distincts, kwargs=dict(distinct=["free", "standard", "premium"])),
    "profession":  dict(method=Core.gen_distincts, kwargs=dict(distinct=[fake.job() for _ in range(100)])),
    "created_at":  dict(method=Core.gen_unix_timestamps, kwargs=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
  }


@pytest.fixture(scope="function")
def rand_spec_case_2():
  fake = faker.Faker(locale="pt_BR")
  return {
    "id":        dict(method=Core.gen_unique_identifiers),
    "age":        dict(method=Core.gen_ints, args=[0, 100]),
    "salary":     dict(method=Core.gen_floats, args=[0, 10**3, 2]),
    "height":     dict(method=Core.gen_floats_normal, args=[10**3, 10**1, 2]),
    "is_active":  dict(method=Core.gen_distincts, args=[[True, False]]),
    "plan":       dict(method=Core.gen_distincts, args=[["free", "standard", "premium"]]),
    "profession": dict(method=Core.gen_distincts, args=[[fake.job() for _ in range(100)]]),
    "created_at": dict(method=Core.gen_unix_timestamps, args=["01-01-2020", "31-12-2020", "%d-%m-%Y"]),
  }


@pytest.fixture(scope="function")
def rand_spec_case_1_transformer():
  return {
    "id":        dict(method=Core.gen_unique_identifiers, args=["zint"]),
    "age":        dict(method=Core.gen_ints, args=[0, 100]),
    "salary":     dict(method=Core.gen_floats, args=[0, 10**3, 2]),
    "plan":       dict(method=Core.gen_distincts, args=[["free", "standard", "premium"]], transformers=[lambda x: x.upper()]),
    "created_at": dict(
                    method=Core.gen_unix_timestamps,
                    args=["01-01-2020", "31-12-2020", "%d-%m-%Y"],
                    transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")]),
  }



@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark():
  spec_handle_1 = {"daily": 70,"weekly":20, "monthly": 10}
  spec_handle_2 = {"mobile": ["IOS","Android"], "Desktop": ["Windows", "MacOS", "Linux"]}
  spec_handle_3 = {
    "GET /home": [("200", 7),("400", 2), ("500", 1)],
    "GET /login": [("200", 5),("400", 3), ("500", 1)],
    "POST /login": [("201", 4),("404", 2), ("500", 1)],
    "GET /logout": [("200", 3),("400", 1), ("400", 1)]
  }
  return {
    "id":        dict(method=Core.gen_unique_identifiers, args=["zint"]),
    "plan":       dict(method=Core.gen_distincts, args=[["free", "standard", "premium"]]),
    "frequency": dict(
      method=Core.gen_distincts, 
      args=[DistinctUtils.handle_distincts_lvl_1(spec_handle_1)] 
    ),
    "device_os": dict(
      method=     Core.gen_distincts,
      splitable=  True,
      cols=       ["device", "platform"],
      sep=        ";",
      kwargs=      dict(distinct=DistinctUtils.handle_distincts_lvl_2(spec_handle_2))
    ),
    "http_request_http_status": dict(
      method=       Core.gen_distincts,
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      kwargs=        dict(distinct=DistinctUtils.handle_distincts_lvl_3(spec_handle_3))
    ),
  }

@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark():
  spec_handle_2 = {"mobile": ["IOS","Android"], "Desktop": ["Windows", "MacOS", "Linux"]}
  distincts = DistinctUtils.handle_distincts_lvl_2(spec_handle_2)
  return {
    "id":        dict(method=Core.gen_unique_identifiers, args=["zint"]),
    "device_os": dict(
      method=     Core.gen_distincts,
      splitable=  True,
      cols=       ["device", "platform"],
      sep=        ";",
      kwargs=      dict(distinct=distincts)
    ),
    # "http_request_http_status": dict(
    #   method=       Core.gen_distincts,
    #   splitable=    True,
    #   cols=         ["http_request", "http_status"],
    #   sep=          ";",
    #   kwargs=        dict(distinct=DistinctUtils.handle_distincts_lvl_3(spec_handle_3))
    # ),
  }

@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark_baseline():
  return {
    "id":        dict(method=Core.gen_unique_identifiers, args=["zint"]),
    "device": dict(method=Core.gen_distincts, args=[["mobile", "desktop"]]),
    "platform": dict(method=Core.gen_distincts, args=[["IOS", "Android", "Windows", "MacOS", "Linux"]]),
    "http_request": dict(method=Core.gen_distincts, args=[["GET /home", "GET /login", "POST /login", "GET /logout"]]),
    "http_status": dict(method=Core.gen_distincts, args=[["200", "201", "400", "404", "500"]]),
  }


@pytest.fixture(scope="function")
def rand_spec_case_21():


  metadata = {
    "campo_simples_proporcional": {
      "method": Core.gen_distincts,
      "parms": dict(distinct=DistinctUtils.handle_distincts_lvl_1(spec_handle_1, 1))
    },
    "campos_correlacionados": {
      "method":     Core.gen_distincts,
      "splitable":  True,
      "cols":       ["categoria_produto", "tipo_produto"],
      "sep":        ";",
      "parms":      dict(distinct=DistinctUtils.handle_distincts_lvl_2(spec_handle_2, sep=";"))
    },
    "campos_correlacionados_proporcionais": dict(
      method=       Core.gen_distincts,
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      parms=        dict(distinct=DistinctUtils.handle_distincts_lvl_3(spec_handle_3))
    )
  }
  return metadata


@pytest.fixture(scope="function")
def rand_spec_case_wsl():
  metadata = {
    "ip_address": dict(
      method=Core.gen_complex_distincts,
      parms=dict(
        pattern="x.x.x.x",  replacement="x", 
        templates=[
          {"method": Core.gen_distincts, "parms": dict(distinct=["172", "192", "10"])},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=128)}
        ]
      )),
    "identificador": dict(method=Core.gen_distincts, parms=dict(distinct=["-"])),
    "user": dict(method=Core.gen_distincts, parms=dict(distinct=["-"])),
    "datetime": dict(
      method=Core.gen_datetimes,
      parms=dict(start='2024-07-05', end='2024-07-06', format_in="%Y-%m-%d", format_out="%d/%b/%Y:%H:%M:%S")
    ),
    "http_version": dict(
      method=Core.gen_distincts,
      parms=dict(distinct=DistinctUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1))
    ),
    "campos_correlacionados_proporcionais": dict(
      method=       Core.gen_distincts,
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
    "object_size": dict(method=Core.gen_ints, parms=dict(min=0, max=10000)),
  }
  return metadata

