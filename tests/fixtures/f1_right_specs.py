import pytest
import faker
from datetime import datetime as dt, timedelta
from rand_engine.utils.distincts_utils import DistinctsUtils


@pytest.fixture(scope="function")
def default_size():
    return 10**4



@pytest.fixture(scope="function")
def rand_spec_with_kwargs():
  fake = faker.Faker(locale="pt_BR")
  return {
    "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
    "age":         dict(method="integers", kwargs=dict(min=0, max=100)),
    "salary":      dict(method="floats", kwargs=dict(min=0, max=10**3, round=2)),
    "height":      dict(method="floats_normal", kwargs=dict(mean=10**3, std=10**1, round=2)),
    "is_active":   dict(method="booleans", kwargs=dict(true_prob=0.7)),
    "plan":        dict(method="distincts", kwargs=dict(distincts=["free", "standard", "premium"])),
    "profession":  dict(method="distincts", kwargs=dict(distincts=[fake.job() for _ in range(5)])),
    "created_at":  dict(method="unix_timestamps", kwargs=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
    "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
  }
 
@pytest.fixture(scope="function")
def rand_spec_lambda_with_kwargs():
  fake = faker.Faker(locale="pt_BR")
  return lambda: {
    "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
    "age":         dict(method="integers", kwargs=dict(min=0, max=100)),
    "salary":      dict(method="floats", kwargs=dict(min=0, max=10**3, round=2)),
    "height":      dict(method="floats_normal", kwargs=dict(mean=10**3, std=10**1, round=2)),
    "is_active":   dict(method="booleans", kwargs=dict(true_prob=0.7)),
    "plan":        dict(method="distincts", kwargs=dict(distincts=["free", "standard", "premium"])),
    "profession":  dict(method="distincts", kwargs=dict(distincts=[fake.job() for _ in range(5)])),
    "created_at":  dict(method="unix_timestamps", kwargs=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
    "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
  }

@pytest.fixture(scope="function")
def rand_spec_with_args():
  fake = faker.Faker(locale="pt_BR")
  return {
    "id":        dict(method="unique_ids", args=["zint", 8]),
    "age":        dict(method="integers", args=[0, 100]),
    "salary":     dict(method="floats", args=[0, 10**3, 2]),
    "height":     dict(method="floats_normal", args=[10**3, 10**1, 2]),
    "is_active":  dict(method="booleans", args=[0.7]),
    "plan":       dict(method="distincts", args=[["free", "standard", "premium"]]),
    "profession": dict(method="distincts", args=[[fake.job() for _ in range(100)]]),
    "created_at": dict(method="unix_timestamps", args=["01-01-2020", "31-12-2020", "%d-%m-%Y"]),
  }


@pytest.fixture(scope="function")
def rand_spec_with_related_columns():
  return {
    "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
    "age":         dict(method="integers", kwargs=dict(min=0, max=100)),
    "device_plat": dict(
                    method="distincts_map", cols = ["device_type", "os_type"],
                    kwargs=dict(distincts={
                       "smartphone": ["android","IOS"], 
                       "desktop": ["linux", "windows"]
    })),
    "deriv_tip": dict(
                    method="distincts_map_prop", cols = ["op", "tip_op"],
                    kwargs=dict(distincts={
                       "OPC": [ ("C_OPC", 8), ("V_OPC", 2)], 
                       "SWP": [ ("C_SWP", 6), ("V_SWP", 4)]
    })),
    "empresa": dict(
                    method="distincts_multi_map", cols = ["setor", "sub_setor", "porte", "codigo_municipio"],
                    kwargs=dict(distincts={
                      "setor_1": [
                          ["agro", "mineração", "petróleo", "pecuária"], [0.25, 0.15], [None], ["01", "02"]], 
                         "setor_2": [
                          ["indústria", "construção"], [0.30, 0.20, 0.10], ["micro", "pequena", "média"], ["03", "04", "05"]]
    })),
  }

@pytest.fixture(scope="function")
def rand_spec_case_1_transformer():
  return {
    "id":        dict(method="unique_ids", args=["zint"]),
    "age":        dict(method="integers", args=[0, 100]),
    "salary":     dict(method="floats", args=[0, 10**3, 2]),
    "plan":       dict(method="distincts", args=[["free", "standard", "premium"]], transformers=[lambda x: x.upper()]),
    "created_at": dict(
                    method="unix_timestamps",
                    args=["01-01-2020", "31-12-2020", "%d-%m-%Y"],
                    transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")]),
  }




@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark():
  spec_handle_2 = {"mobile": ["IOS","Android"], "Desktop": ["Windows", "MacOS", "Linux"]}
  distincts = DistinctsUtils.handle_distincts_lvl_2(spec_handle_2)
  return {
    "id":        dict(method="unique_ids", args=["zint"]),
    "device_os": dict(
      method=     "distincts",
      splitable=  True,
      cols=       ["device", "platform"],
      sep=        ";",
      kwargs=      dict(distincts=distincts)
    ),
    # "http_request_http_status": dict(
    #   method=       "distincts",
    #   splitable=    True,
    #   cols=         ["http_request", "http_status"],
    #   sep=          ";",
    #   kwargs=        dict(distincts=DistinctsUtils.handle_distincts_lvl_3(spec_handle_3))
    # ),
  }

@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark_baseline():
  return {
    "id":        dict(method="unique_ids", args=["zint"]),
    "device": dict(method="distincts", args=[["mobile", "desktop"]]),
    "platform": dict(method="distincts", args=[["IOS", "Android", "Windows", "MacOS", "Linux"]]),
    "http_request": dict(method="distincts", args=[["GET /home", "GET /login", "POST /login", "GET /logout"]]),
    "http_status": dict(method="distincts", args=[["200", "201", "400", "404", "500"]]),
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
    "id":        dict(method= "unique_ids", args=["zint"]),
    "plan":       dict(method="distincts", args=[["free", "standard", "premium"]]),
    "frequency": dict(
      method="distincts", 
      args=[DistinctsUtils.handle_distincts_lvl_1(spec_handle_1)] 
    ),
    "device_os": dict(
      method=     "distincts",
      splitable=  True,
      cols=       ["device", "platform"],
      sep=        ";",
      kwargs=      dict(distincts=DistinctsUtils.handle_distincts_lvl_2(spec_handle_2))
    ),
    "http_request_http_status": dict(
      method=       "distincts",
      splitable=    True,
      cols=         ["http_request", "http_status"],
      sep=          ";",
      kwargs=        dict(distincts=DistinctsUtils.handle_distincts_lvl_3(spec_handle_3))
    ),
  }



# @pytest.fixture(scope="function")
# def rand_spec_case_21():


#   metadata = {
#     "campo_simples_proporcional": {
#       "method": "distincts",
#       "parms": dict(distincts=DistinctsUtils.handle_distincts_lvl_1(spec_handle_1, 1))
#     },
#     "campos_correlacionados": {
#       "method":     "distincts",
#       "splitable":  True,
#       "cols":       ["categoria_produto", "tipo_produto"],
#       "sep":        ";",
#       "parms":      dict(distincts=DistinctsUtils.handle_distincts_lvl_2(spec_handle_2, sep=";"))
#     },
#     "campos_correlacionados_proporcionais": dict(
#       method=       "distincts",
#       splitable=    True,
#       cols=         ["http_request", "http_status"],
#       sep=          ";",
#       parms=        dict(distincts=DistinctsUtils.handle_distincts_lvl_3(spec_handle_3))
#     )
#   }
#   return metadata


# @pytest.fixture(scope="function")
# def rand_spec_case_wsl():
#   metadata = {
#     "ip_address": dict(
#       method=Core.gen_complex_distincts,
#       parms=dict(
#         pattern="x.x.x.x",  replacement="x", 
#         templates=[
#           {"method": "distincts", "parms": dict(distincts=["172", "192", "10"])},
#           {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
#           {"method": Core.gen_ints, "parms": dict(min=0, max=255)},
#           {"method": Core.gen_ints, "parms": dict(min=0, max=128)}
#         ]
#       )),
#     "identificador": dict(method="distincts", parms=dict(distincts=["-"])),
#     "user": dict(method="distincts", parms=dict(distincts=["-"])),
#     "datetime": dict(
#       method=Core.gen_datetimes,
#       parms=dict(start='2024-07-05', end='2024-07-06', format_in="%Y-%m-%d", format_out="%d/%b/%Y:%H:%M:%S")
#     ),
#     "http_version": dict(
#       method="distincts",
#       parms=dict(distincts=DistinctsUtils.handle_distincts_lvl_1({"HTTP/1.1": 7, "HTTP/1.0": 3}, 1))
#     ),
#     "campos_correlacionados_proporcionais": dict(
#       method=       "distincts",
#       splitable=    True,
#       cols=         ["http_request", "http_status"],
#       sep=          ";",
#       parms=        dict(distincts=DistinctsUtils.handle_distincts_lvl_3({
#                         "GET /home": [("200", 7),("400", 2), ("500", 1)],
#                         "GET /login": [("200", 5),("400", 3), ("500", 1)],
#                         "POST /login": [("201", 4),("404", 2), ("500", 1)],
#                         "GET /logout": [("200", 3),("400", 1), ("400", 1)]
#         }))
#     ),
#     "object_size": dict(method=Core.gen_ints, parms=dict(min=0, max=10000)),
#   }
#   return metadata

