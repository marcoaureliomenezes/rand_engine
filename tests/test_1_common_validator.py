"""
Tests for CommonValidator - validates SparkGenerator specs.
Covers common methods shared between DataGenerator and SparkGenerator.
"""

from datetime import date, datetime
from decimal import Decimal

import numpy as np
import pytest
from rand_engine import DataGenerator
from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.exceptions import SpecValidationError


class TestValidSparkSpecs:
    """Test validation of valid Spark specifications."""
    
    def test_valid_spec_integers(self):
        """Test valid spec with integers method."""
        spec = {
            "age": {
                "method": "integers",
                "kwargs": {"min": 18, "max": 65}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_zint(self):
        """Test valid spec with int_zfilled method."""
        spec = {
            "code": {
                "method": "int_zfilled",
                "kwargs": {"length": 8}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_floats(self):
        """Test valid spec with floats method."""
        spec = {
            "price": {
                "method": "floats",
                "kwargs": {"min": 0.0, "max": 1000.0, "decimals": 2}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_floats_normal(self):
        """Test valid spec with floats_normal method."""
        spec = {
            "height": {
                "method": "floats_normal",
                "kwargs": {"mean": 170.0, "std": 10.0, "decimals": 2}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_booleans(self):
        """Test valid spec with booleans method."""
        spec = {
            "is_active": {
                "method": "booleans",
                "kwargs": {"true_prob": 0.7}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_distincts(self):
        """Test valid spec with distincts method."""
        spec = {
            "category": {
                "method": "distincts",
                "kwargs": {"distincts": ["A", "B", "C"]}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_distincts_prop(self):
        """Test valid spec with distincts_prop method."""
        spec = {
            "device": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"mobile": 70, "desktop": 30}}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_uuid4(self):
        """Test valid spec with uuid4 method."""
        spec = {
            "id": {
                "method": "uuid4",
                "kwargs": {}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0
    
    def test_valid_spec_dates(self):
        """Test valid spec with dates method using unified date_format parameter."""
        spec = {
            "created_at": {
                "method": "dates",
                "kwargs": {
                    "start": "2020-01-01",
                    "end": "2024-12-31",
                    "date_format": "%Y-%m-%d"
                }
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 0


class TestInvalidSparkSpecs:
    """Test validation catches invalid Spark specifications."""
    
    def test_invalid_missing_method(self):
        """Test error when method key is missing."""
        spec = {
            "age": {
                "kwargs": {"min": 0, "max": 100}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 1
        assert "field 'method' is required" in errors[0]
    
    def test_invalid_method_unknown(self):
        """Test error when method is unknown."""
        spec = {
            "age": {
                "method": "unknown_method",
                "kwargs": {}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 1
        assert "does not exist" in errors[0]
    
    def test_invalid_missing_required_param(self):
        """Test error when required parameter is missing."""
        spec = {
            "age": {
                "method": "integers",
                "kwargs": {"min": 0}
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 1
        assert "requires parameter 'max'" in errors[0]
    
    def test_invalid_floats_normal_missing_param(self):
        """Test error when floats_normal is missing required parameter."""
        spec = {
            "height": {
                "method": "floats_normal",
                "kwargs": {"mean": 170.0}  # Missing 'std'
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 1
        assert "requires parameter 'std'" in errors[0]
    
    def test_invalid_dates_wrong_param_name(self):
        """'format' is not a dates parameter; date_format is optional."""
        spec = {
            "created_at": {
                "method": "dates",
                "kwargs": {
                    "start": "2020-01-01",
                    "end": "2024-12-31",
                    "format": "%Y-%m-%d"
                }
            }
        }
        errors = CommonValidator.validate_spark_spec(spec)
        assert len(errors) == 1
        assert any("unknown parameters" in error.lower() and "'format'" in error for error in errors)


class TestValidateAndRaise:
    """Test validate_and_raise method."""
    
    def test_validate_and_raise_valid(self):
        """Test that valid spec doesn't raise exception."""
        spec = {
            "age": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 100}
            }
        }
        CommonValidator.validate_spark_and_raise(spec)
    
    def test_validate_and_raise_invalid(self):
        """Test that invalid spec raises SpecValidationError."""
        spec = {
            "age": {
                "method": "invalid_method",
                "kwargs": {}
            }
        }
        with pytest.raises(SpecValidationError) as exc_info:
            CommonValidator.validate_spark_and_raise(spec)
    
        assert "SPARKGENERATOR SPEC VALIDATION ERROR" in str(exc_info.value)
        assert "does not exist" in str(exc_info.value)

    def test_validate_and_raise_advanced_method_only_warns(self):
        """Advanced methods are allowed in SparkGenerator with a warning (docs/2_SPARK_GENERATOR.md)."""
        spec = {"device_os": {"method": "distincts_map", "cols": ["device", "os"],
                              "kwargs": {"distincts": {"smartphone": ["android", "ios"]}}}}
        with pytest.warns(UserWarning, match="'distincts_map' is a dummy in SparkGenerator"):
            CommonValidator.validate_spark_and_raise(spec)

    @pytest.mark.parametrize("config, message", [
        ({"method": "distincts_external", "kwargs": {}}, "does not exist"),
        ({"method": "integers", "kwargs": {"min": 1, "max": 5, "dtype": "int"}}, "unknown parameters: 'dtype'"),
        ({"method": "uuid4", "args": []}, "does not support 'args'"),
        ({"method": "pk", "kwargs": {"style": "sequence"}}, "(?s)^(?!.*does not exist).*'pk'.*NumPy engine only in 0.7.0.*DataGenerator"),
        ({"method": "fk", "kwargs": {}}, "(?s)^(?!.*does not exist).*'fk'.*NumPy engine only in 0.7.0.*DataGenerator"),
    ])
    def test_validate_and_raise_unsupported_advanced_spec(self, config, message):
        """Specs Spark cannot run raise at validation, not in get_df."""
        with pytest.raises(SpecValidationError, match=message):
            CommonValidator.validate_spark_and_raise({"c": config})


def test_validated_spec_without_kwargs_generates(spark_session, spark_functions):
    """The validator's own uuid4 example (no kwargs) validates and generates (validator-engine-schema-drift)."""
    from rand_engine.main.spark_generator import SparkGenerator
    df = SparkGenerator(spark_session, spark_functions, {"id": {"method": "uuid4"}}).size(3).get_df()
    assert df.count() == 3


@pytest.mark.parametrize("fmt", ["%b %d %Y", "%Y-%m-%d %%"])
def test_dates_format_outside_supported_directives_is_refused_by_both_engines(fmt):
    """AC14.1: one check site; the message names the supported set."""
    from rand_engine.validators.advanced_validator import AdvancedValidator
    spec = {"d": {"method": "dates", "kwargs": {"start": "Jan 01 2020", "end": "Dec 31 2024", "date_format": fmt}}}
    for errors in (AdvancedValidator.validate(spec), CommonValidator.validate_spark_spec(spec)):
        assert len(errors) == 1
        assert "%Y %m %d %H %M %S %f" in errors[0]


def test_unix_timestamps_format_is_not_restricted():
    spec = {"t": {"method": "unix_timestamps", "kwargs": {"start": "Jan 01 2020", "end": "Dec 31 2024", "date_format": "%b %d %Y"}}}
    assert CommonValidator.validate_spark_spec(spec) == []


def _caught_validation(call):
    try:
        call()
    except Exception as error:
        return error
    return None


@pytest.mark.parametrize(("method", "kwargs"), [
    ("floats", {"min": 100, "max": 900, "decimals": -1}),
    ("floats_normal", {"mean": 100, "std": 10, "decimals": -1}),
    ("floats_normal", {"mean": float("inf"), "std": 1, "decimals": 2}),
    ("floats_normal", {"mean": 0, "std": float("inf"), "decimals": 2}),
])
def test_legacy_float_domains_remain_accepted_and_generatable(method, kwargs):
    try:
        frame = DataGenerator({"value": {"method": method, "kwargs": kwargs}}, seed=7).size(3).get_df()
    except SpecValidationError as error:
        frame = error

    assert not isinstance(frame, SpecValidationError)
    assert frame.columns.tolist() == ["value"]
    assert len(frame) == 3


def test_legacy_normal_negative_std_remains_invalid():
    error = _caught_validation(
        lambda: DataGenerator({
            "value": {
                "method": "floats_normal",
                "kwargs": {"mean": 0, "std": -1, "decimals": 2},
            }
        })
    )

    assert isinstance(error, SpecValidationError)
    assert "'std'" in str(error)


@pytest.mark.parametrize(("method", "parameter"), [
    ("exponential", "scale"),
    ("lognormal", "mean"),
    ("lognormal", "std"),
    ("poisson", "lam"),
    ("zipf", "a"),
])
def test_huge_new_distribution_parameters_are_collected(method, parameter):
    caught = None
    try:
        DataGenerator({"value": {"method": method, "kwargs": {parameter: 10**1000}}})
    except (SpecValidationError, OverflowError) as error:
        caught = error

    assert isinstance(caught, SpecValidationError)
    assert "Column 'value'" in str(caught)
    assert f"'{parameter}'" in str(caught)


@pytest.mark.parametrize("value", [
    None,
    True,
    7,
    1.5,
    "outlier",
    b"outlier",
    date(2026, 10, 8),
    datetime(2026, 10, 8, 12, 30),
    Decimal("1.25"),
])
def test_anomaly_values_accept_the_declared_scalar_family(value):
    DataGenerator({
        "value": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 10},
            "anomaly_rate": 1,
            "anomaly_values": [value],
        }
    })


def test_anomaly_values_reject_arbitrary_objects():
    caught = None
    try:
        DataGenerator({
            "value": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 10},
                "anomaly_rate": 1,
                "anomaly_values": [object()],
            }
        })
    except SpecValidationError as error:
        caught = error

    assert isinstance(caught, SpecValidationError)
    assert "Column 'value'" in str(caught)
    assert "'anomaly_values'" in str(caught)


def test_wrong_numeric_types_are_collected_before_semantic_checks():
    specs = {
        "integer_value": {"method": "integers", "kwargs": {"min": "low", "max": 10}},
        "float_value": {"method": "floats", "kwargs": {"min": "low", "max": "high", "decimals": "two"}},
        "normal_value": {"method": "floats_normal", "kwargs": {"mean": "mean", "std": "std", "decimals": "two"}},
        "boolean_value": {"method": "booleans", "kwargs": {"true_prob": "abc"}},
        "exponential_value": {"method": "exponential", "kwargs": {"scale": "scale", "decimals": "two"}},
        "lognormal_value": {"method": "lognormal", "kwargs": {"mean": "mean", "std": "std", "decimals": "two"}},
        "poisson_value": {"method": "poisson", "kwargs": {"lam": "lam"}},
        "zipf_value": {"method": "zipf", "kwargs": {"a": "a"}},
    }

    error = _caught_validation(lambda: DataGenerator(specs))

    assert isinstance(error, SpecValidationError)
    message = str(error)
    for column, parameters in {
        "integer_value": ("min",),
        "float_value": ("min", "max", "decimals"),
        "normal_value": ("mean", "std", "decimals"),
        "boolean_value": ("true_prob",),
        "exponential_value": ("scale", "decimals"),
        "lognormal_value": ("mean", "std", "decimals"),
        "poisson_value": ("lam",),
        "zipf_value": ("a",),
    }.items():
        assert f"Column '{column}'" in message
        for parameter in parameters:
            assert f"'{parameter}'" in message


@pytest.mark.parametrize(("method", "kwargs", "parameter"), [
    ("exponential", {"scale": 0}, "scale"),
    ("exponential", {"decimals": -1}, "decimals"),
    ("exponential", {"decimals": 1.5}, "decimals"),
    ("lognormal", {"std": -1}, "std"),
    ("lognormal", {"decimals": -1}, "decimals"),
    ("poisson", {"lam": -1}, "lam"),
    ("zipf", {"a": 1}, "a"),
])
def test_new_distribution_domains_are_rejected_before_generation(method, kwargs, parameter):
    error = _caught_validation(lambda: DataGenerator({"value": {"method": method, "kwargs": kwargs}}))

    assert isinstance(error, SpecValidationError)
    message = str(error)
    assert f"Column 'value'" in message
    assert f"'{parameter}'" in message
    assert "does not exist" not in message


@pytest.mark.parametrize(("modifier", "value"), [
    ("null_rate", "often"),
    ("null_rate", -0.1),
    ("null_rate", 1.1),
    ("anomaly_rate", "often"),
    ("anomaly_rate", -0.1),
    ("anomaly_rate", 1.1),
])
def test_modifier_rates_require_real_probabilities(modifier, value):
    column = {"method": "integers", "kwargs": {"min": 0, "max": 10}, modifier: value}
    error = _caught_validation(lambda: DataGenerator({"value": column}))

    assert isinstance(error, SpecValidationError)
    message = str(error)
    assert "Column 'value'" in message
    assert f"'{modifier}'" in message


@pytest.mark.parametrize(("config", "message_parts"), [
    ({"method": "exponential", "kwargs": {}}, ("exponential", "DataGenerator")),
    ({"method": "lognormal", "kwargs": {}}, ("lognormal", "DataGenerator")),
    ({"method": "poisson", "kwargs": {}}, ("poisson", "DataGenerator")),
    ({"method": "zipf", "kwargs": {}}, ("zipf", "DataGenerator")),
    ({"method": "constant", "kwargs": {"value": 1}}, ("constant", "DataGenerator")),
    ({"method": "integers", "kwargs": {"min": 0, "max": 10}, "null_rate": 0.1}, ("null_rate", "DataGenerator")),
    ({"method": "integers", "kwargs": {"min": 0, "max": 10}, "anomaly_rate": 0.1, "anomaly_values": [99]}, ("anomaly_rate", "DataGenerator")),
    ({"method": "integers", "kwargs": {"min": 0, "max": 10, "int_type": "uint64"}}, ("uint64", "Spark")),
])
def test_spark_refuses_numpy_only_features_before_execution(config, message_parts):
    error = _caught_validation(lambda: CommonValidator.validate_spark_and_raise({"value": config}))

    assert isinstance(error, SpecValidationError)
    message = str(error)
    assert "Column 'value'" in message
    for part in message_parts:
        assert part in message


@pytest.mark.xfail(strict=True, reason="J2.S1.T1 RED: float lattice validation is not implemented")
@pytest.mark.parametrize(("minimum", "maximum", "decimals"), [
    (9.991, 9.991, 2),
    (10, 0, 2),
    (float("-inf"), 1, 2),
    (0, float("inf"), 2),
    (float("nan"), 1, 2),
])
def test_invalid_or_empty_float_lattices_are_collected_during_public_construction(minimum, maximum, decimals):
    error = _caught_validation(lambda: DataGenerator({
        "value": {
            "method": "floats",
            "kwargs": {"min": minimum, "max": maximum, "decimals": decimals},
        }
    }))

    assert isinstance(error, SpecValidationError)
    message = str(error)
    assert "Column 'value'" in message
    assert "floats" in message


@pytest.mark.xfail(strict=True, reason="J2.S1.T1 RED: unrepresentable Poisson lambda validates")
def test_poisson_lambda_beyond_numpy_int64_result_domain_is_collected_before_generation():
    unrepresentable_lam = float(2**63)
    with pytest.raises(ValueError):
        np.random.default_rng(0).poisson(lam=unrepresentable_lam, size=1)

    error = _caught_validation(lambda: DataGenerator({
        "value": {"method": "poisson", "kwargs": {"lam": unrepresentable_lam}}
    }))
    assert isinstance(error, SpecValidationError)
    assert "Column 'value'" in str(error)
    assert "'lam'" in str(error)
