"""
Tests for CommonValidator - validates SparkGenerator specs.
Covers common methods shared between DataGenerator and SparkGenerator.
"""

import pytest
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
