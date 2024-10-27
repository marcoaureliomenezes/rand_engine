import pytest

from datetime import datetime as dt
import numpy as np
import faker

from rand_engine.core.distinct_core import DistinctCore
from rand_engine.core.numeric_core import NumericCore
from rand_engine.core.datetime_core import DatetimeCore

from rand_engine.core.distinct_utils import DistinctUtils



@pytest.fixture(scope="function")
def dataframe_size():
    return 5

@pytest.fixture(scope="function")
def metadata_case_constant():
  metadata = {
    "campo_string": dict(method=lambda size, distinct:    np.random.choice(distinct, size), parms=dict(distinct=["valor_fixo"])),
    "campo_int": dict(method=lambda size, distinct:       np.random.choice(distinct, size), parms=dict(distinct=[420])),
    "campo_double": dict(method=lambda size, distinct:    np.random.choice(distinct, size), parms=dict(distinct=[3.14])),
    "campo_booleano": dict(method=lambda size, distinct:  np.random.choice(distinct, size), parms=dict(distinct=[True])),
    "campo_datetime": dict(method=lambda size, distinct:  np.random.choice(distinct, size), parms=dict(distinct=[dt.now()]))
    }
  return metadata


@pytest.fixture(scope="function")
def metadata_cases_variable_simple():
  fake = faker.Faker(locale="pt_BR")
  metadata = {
    "campo_cont":           dict(method=lambda size, value: [value for _ in range(size)], parms=dict(value="valor_fixo")),
    "campo_int":            dict(method=NumericCore.gen_ints, parms=dict(min=0, max=100)),
    "campo_float":          dict(method=NumericCore.gen_floats, parms=dict(min=0, max=10**3, round=2)),
    "campo_float_normal":   dict(method=NumericCore.gen_floats_normal, parms=dict(mean=10**3, std=10**1, round=2)),
    "campo_booleano":       dict(method=DistinctCore.gen_distincts_typed, parms=dict(distinct=[True, False])),
    "campo_categorico":     dict(method=DistinctCore.gen_distincts_typed, parms=dict(distinct=["valor_1", "valor_2", "valor_3"])),
    "campo_categorico_2":   dict(method=DistinctCore.gen_distincts_typed, parms=dict(distinct=[fake.job() for _ in range(100)])),
    "signup_date":          dict(method=DatetimeCore.gen_timestamps, parms=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
  }
  return metadata


@pytest.fixture(scope="function")
def metadata_cases_variable_complex():
  metadata = {
    "campo_simples_proporcional": {
      "method": DistinctCore.gen_distincts_typed,
      "parms": dict(distinct=DistinctUtils.handle_distincts_lvl_1({"Junior": 70,"Pleno":35, "Senior": 12, "Staff": 7}, 1))
    },
    "campos_correlacionados": {
      "method":     DistinctCore.gen_distincts_typed,
      "splitable":  True,
      "cols":       ["categoria_produto", "tipo_produto"],
      "sep":        ";",
      "parms":      dict(distinct=DistinctUtils.handle_distincts_lvl_2({"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}, sep=";"))
    },
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
    )
  }
  return metadata



@pytest.fixture(scope="function")
def metadata_case_web_log_server():
  metadata = {
    "ip_address": dict(
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
  return metadata

