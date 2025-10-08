from datetime import datetime as dt
import pytest
import faker
import numpy as np

from rand_engine.core import Core
from rand_engine.utils.distincts import DistinctUtils


@pytest.fixture(scope="function")
def default_size():
    return 10**4


@pytest.fixture(scope="function")
def rand_spec_case_1():
  fake = faker.Faker(locale="pt_BR")
  fake.seed_instance(42)  # Seed para esta instância específica
  metadata = {
    "campo_int":            dict(method=Core.gen_ints, parms=dict(min=0, max=100)),
    "campo_float":          dict(method=Core.gen_floats, parms=dict(min=0, max=10**3, round=2)),
    "campo_float_normal":   dict(method=Core.gen_floats_normal, parms=dict(mean=10**3, std=10**1, round=2)),
    "campo_booleano":       dict(method=Core.gen_distincts_typed, parms=dict(distinct=[True, False])),
    "campo_categorico":     dict(method=Core.gen_distincts_typed, parms=dict(distinct=["valor_1", "valor_2", "valor_3"])),
    "campo_categorico_2":   dict(method=Core.gen_distincts_typed, parms=dict(distinct=[fake.job() for _ in range(100)])),
    "signup_timestamp":     dict(method=Core.gen_unix_timestamps, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
  }
  return metadata



@pytest.fixture(scope="function")
def rand_spec_case_1_transformer():
  fake = faker.Faker(locale="pt_BR")
  fake.seed_instance(42)  # Seed para esta instância específica
  metadata = {
    "campo_int":            dict(method=Core.gen_ints, parms=dict(min=0, max=100)),
    "campo_float":          dict(method=Core.gen_floats, parms=dict(min=0, max=10**3, round=2)),
    "campo_float_normal":   dict(method=Core.gen_floats_normal, parms=dict(mean=10**3, std=10**1, round=2)),
    "campo_booleano":       dict(method=Core.gen_distincts_typed, parms=dict(distinct=[True, False])),
    "campo_categorico":     dict(
      method=Core.gen_distincts_typed, parms=dict(distinct=["valor_1", "valor_2", "valor_3"]),
      transformers=[lambda x: x.upper()]
      ),
    "campo_categorico_2":   dict(method=Core.gen_distincts_typed, parms=dict(distinct=[fake.job() for _ in range(100)])),
    "signup_timestamp":     dict(
      method=Core.gen_unix_timestamps, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y"),
      transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")]
    ),
  }
  return metadata



@pytest.fixture(scope="function")
def rand_spec_case_2():
  spec_handle_1 = {"Junior": 70,"Pleno":35, "Senior": 12, "Staff": 7}
  spec_handle_2 = {"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
  spec_handle_3 = {
    "GET /home": [("200", 7),("400", 2), ("500", 1)],
    "GET /login": [("200", 5),("400", 3), ("500", 1)],
    "POST /login": [("201", 4),("404", 2), ("500", 1)],
    "GET /logout": [("200", 3),("400", 1), ("400", 1)]
  } 

  metadata = {
    "campo_simples_proporcional": {
      "method": Core.gen_distincts_typed,
      "parms": dict(distinct=DistinctUtils.handle_distincts_lvl_1(spec_handle_1, 1))
    },
    "campos_correlacionados": {
      "method":     Core.gen_distincts_typed,
      "splitable":  True,
      "cols":       ["categoria_produto", "tipo_produto"],
      "sep":        ";",
      "parms":      dict(distinct=DistinctUtils.handle_distincts_lvl_2(spec_handle_2, sep=";"))
    },
    "campos_correlacionados_proporcionais": dict(
      method=       Core.gen_distincts_typed,
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
          {"method": Core.gen_distincts_typed, "parms": dict(distinct=["172", "192", "10"])},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
          {"method": Core.gen_ints, "parms": dict(min=0, max=128)}
        ]
      )),
    "identificador": dict(method=Core.gen_distincts_typed, parms=dict(distinct=["-"])),
    "user": dict(method=Core.gen_distincts_typed, parms=dict(distinct=["-"])),
    "datetime": dict(
      method=Core.gen_datetimes,
      parms=dict(start='2024-07-05', end='2024-07-06', format_in="%Y-%m-%d", format_out="%d/%b/%Y:%H:%M:%S")
    ),
    "http_version": dict(
      method=Core.gen_distincts_typed,
      parms=dict(distinct=DistinctUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1))
    ),
    "campos_correlacionados_proporcionais": dict(
      method=       Core.gen_distincts_typed,
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

