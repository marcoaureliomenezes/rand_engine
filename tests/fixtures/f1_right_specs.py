import pytest
import faker
from datetime import datetime as dt, timedelta


@pytest.fixture(scope="function")
def default_size():
    return 10**4


@pytest.fixture(scope="function")
def rand_spec_with_kwargs():
    """
    Comprehensive spec using ONLY kwargs for all methods.
    Tests: integers, floats, floats_normal, distincts, uuid4, booleans.
    """
    return {
        "id": dict(method="uuid4", kwargs={}),
        "age": dict(method="integers", kwargs=dict(min=18, max=65)),
        "score": dict(method="floats", kwargs=dict(min=0.0, max=100.0, decimals=2)),
        "rating": dict(method="floats_normal", kwargs=dict(mean=7.5, std=1.5, decimals=1)),
        "category": dict(method="distincts", kwargs=dict(distincts=["A", "B", "C", "D"])),
        "is_active": dict(method="booleans", kwargs=dict(true_prob=0.8)),
    }
 

@pytest.fixture(scope="function")
def rand_spec_lambda_with_kwargs():
    """Lambda spec with kwargs - Returns callable that generates spec."""
    return lambda: {
        "transaction_id": dict(method="uuid4", kwargs={}),
        "amount": dict(method="floats", kwargs=dict(min=10.0, max=1000.0, decimals=2)),
        "status": dict(method="distincts", kwargs=dict(distincts=["pending", "completed", "failed"])),
    }


@pytest.fixture(scope="function")
def rand_spec_with_args():
    """
    Spec using ONLY args (not kwargs).
    Tests that args parameter works correctly.
    """
    return {
        "id": dict(method="int_zfilled", args=[10]),
        "priority": dict(method="distincts", args=[["low", "medium", "high"]]),
        "temperature": dict(method="floats", args=[20.0, 30.0, 1]),
    }


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
                          ["agro", "mineração", "petróleo", "pecuária"],
                          [0.25, 0.15],
                          [None],
                          ["01", "02"]], 
                      "setor_2": [
                          ["indústria", "construção"],
                          [0.30, 0.20, 0.10],
                          ["micro", "pequena", "média"],
                          ["03", "04", "05"]
                    ]
        })),
    }


@pytest.fixture(scope="function")
def rand_spec_with_transformers():
    """
    Spec testing embedded transformers on columns.
    Transformers are applied after generation.
    """
    return {
        "id": dict(method="int_zfilled", kwargs=dict(length=6)),
        "timestamp": dict(
            method="unix_timestamps",
            kwargs=dict(start='2024-01-01', end='2024-12-31', date_format="%Y-%m-%d"),
            transformers=[lambda ts: dt.fromtimestamp(ts).strftime("%d/%b/%Y:%H:%M:%S")]
        ),
        "email": dict(
            method="distincts",
            kwargs=dict(distincts=["john.doe", "jane.smith", "bob.jones"]),
            transformers=[lambda name: f"{name}@example.com"]
        ),
        "price": dict(
            method="floats",
            kwargs=dict(min=10.0, max=100.0, decimals=2),
            transformers=[
                lambda val: val * 1.1,  # Add 10% tax
                lambda val: round(val, 2)  # Round again after tax
            ]
        ),
    }


@pytest.fixture(scope="function")
def rand_spec_all_methods():
    """
    Comprehensive spec using ALL available DataGenerator methods.
    Tests complete coverage of all generation capabilities.
    """
    return {
        # NPCore methods
        "id": dict(method="integers", kwargs=dict(min=1, max=1000000)),
        "code": dict(method="int_zfilled", kwargs=dict(length=8)),
        "price": dict(method="floats", kwargs=dict(min=1.0, max=1000.0, decimals=2)),
        "rating": dict(method="floats_normal", kwargs=dict(mean=4.0, std=0.8, decimals=1)),
        "category": dict(method="distincts", kwargs=dict(distincts=["A", "B", "C"])),
        "tier": dict(method="distincts_prop", kwargs=dict(distincts={"gold": 10, "silver": 30, "bronze": 60})),
        "created_at": dict(method="unix_timestamps", kwargs=dict(start="2024-01-01", end="2024-12-31", date_format="%Y-%m-%d")),
        "uuid": dict(method="uuid4", kwargs={}),
        "is_verified": dict(method="booleans", kwargs=dict(true_prob=0.7)),
        
        # PyCore methods - correlated columns
        "device_os": dict(
            method="distincts_map",
            cols=["device", "os"],
            kwargs=dict(distincts={
                "mobile": ["android", "ios"],
                "desktop": ["windows", "macos", "linux"]
            })
        ),
        "trade_details": dict(
            method="distincts_map_prop",
            cols=["trade_type", "trade_side"],
            kwargs=dict(distincts={
                "EQUITY": [("BUY", 6), ("SELL", 4)],
                "FX": [("BUY", 5), ("SELL", 5)]
            })
        ),
        "company_data": dict(
            method="distincts_multi_map",
            cols=["industry", "sub_industry", "company_size"],
            kwargs=dict(distincts={
                "tech": [
                    ["software", "hardware"],
                    [0.7, 0.3],
                    ["small", "medium", "large"]
                ]
            })
        ),
        "ip_address": dict(
            method="complex_distincts",
            kwargs=dict(
                pattern="x.x.x.x",
                replacement="x",
                templates=[
                    {"method": "distincts", "kwargs": dict(distincts=["192", "172", "10"])},
                    {"method": "integers", "kwargs": dict(min=0, max=255)},
                    {"method": "integers", "kwargs": dict(min=0, max=255)},
                    {"method": "integers", "kwargs": dict(min=1, max=254)}
                ]
            )
        ),
    }


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

