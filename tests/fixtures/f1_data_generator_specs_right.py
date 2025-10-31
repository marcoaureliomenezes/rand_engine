import pytest
import faker
from datetime import datetime as dt, timedelta
from rand_engine.examples import CommonRandSpecs


@pytest.fixture(scope="function")
def default_size():
    return 10**4


@pytest.fixture(scope="function")
def rand_spec_with_kwargs():
    """Simple spec with kwargs - Use CommonRandSpecs.customers() instead."""
    return CommonRandSpecs.customers()
 

@pytest.fixture(scope="function")
def rand_spec_lambda_with_kwargs():
    """Lambda spec with kwargs - Returns callable that generates customers spec."""
    return lambda: CommonRandSpecs.customers()


@pytest.fixture(scope="function")
def rand_spec_with_args():
    """Spec using args instead of kwargs - Use CommonRandSpecs.customers() instead."""
    return CommonRandSpecs.customers()


@pytest.fixture(scope="function")
def rand_spec_with_related_columns():
    """Spec with correlated columns - Combined from RandSpecs."""
    
    # Combine specs to include all correlation types
    return {
        "id":        dict(method="int_zfilled", kwargs=dict(length=8)),
        "age":       dict(method="integers", kwargs=dict(min=0, max=100)),
        # From simple_client_2 - distincts_map
        "device_plat": dict(
                    method="distincts_map", cols = ["device_type", "os_type"],
                    kwargs=dict(distincts={
                       "smartphone": ["android","IOS"], 
                       "desktop": ["linux", "windows"]
        })),
        # From simple_client_3 - distincts_map_prop
        "deriv_tip": dict(
                    method="distincts_map_prop", cols = ["op", "tip_op"],
                    kwargs=dict(distincts={
                       "OPC": [ ("C_OPC", 8), ("V_OPC", 2)], 
                       "SWP": [ ("C_SWP", 6), ("V_SWP", 4)]
        })),
        # From simple_client_4 - distincts_multi_map
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
    """Spec with transformers - Use CommonRandSpecs.users() instead (has uppercase transformer)."""
    return CommonRandSpecs.users()



@pytest.fixture(scope="function")
def rand_engine_splitable_benchmark_baseline():
  return {
    "id":        dict(method="int_zfilled", kwargs=dict(length=8)),
    "device": dict(method="distincts", args=[["mobile", "desktop"]]),
    "platform": dict(method="distincts", args=[["IOS", "Android", "Windows", "MacOS", "Linux"]]),
    "http_request": dict(method="distincts", args=[["GET /home", "GET /login", "POST /login", "GET /logout"]]),
    "http_status": dict(method="distincts", args=[["200", "201", "400", "404", "500"]]),
  }


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

