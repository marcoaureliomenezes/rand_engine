"""Tests for SparkSpecValidator."""

import pytest
from rand_engine.validators.spark_spec_validator import SparkSpecValidator
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
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_zint(self):
        """Test valid spec with int_zfilled method."""
        spec = {
            "code": {
                "method": "int_zfilled",
                "kwargs": {"length": 8}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_floats(self):
        """Test valid spec with floats method."""
        spec = {
            "price": {
                "method": "floats",
                "kwargs": {"min": 0.0, "max": 1000.0, "decimals": 2}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_floats_normal(self):
        """Test valid spec with floats_normal method."""
        spec = {
            "height": {
                "method": "floats_normal",
                "kwargs": {"mean": 170.0, "std": 10.0, "decimals": 2}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_booleans(self):
        """Test valid spec with booleans method."""
        spec = {
            "is_active": {
                "method": "booleans",
                "kwargs": {"true_prob": 0.7}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_distincts(self):
        """Test valid spec with distincts method."""
        spec = {
            "category": {
                "method": "distincts",
                "kwargs": {"distincts": ["A", "B", "C"]}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_distincts_prop(self):
        """Test valid spec with distincts_prop method."""
        spec = {
            "device": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"mobile": 70, "desktop": 30}}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_uuid4(self):
        """Test valid spec with uuid4 method."""
        spec = {
            "id": {
                "method": "uuid4",
                "kwargs": {}
            }
        }
        errors = SparkSpecValidator.validate(spec)
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
        errors = SparkSpecValidator.validate(spec)
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
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 1
        assert "missing required 'method'" in errors[0]
    
    def test_invalid_method_unknown(self):
        """Test error when method is unknown."""
        spec = {
            "age": {
                "method": "unknown_method",
                "kwargs": {}
            }
        }
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 1
        assert "unknown method" in errors[0]
    
    def test_invalid_missing_required_param(self):
        """Test error when required parameter is missing."""
        spec = {
            "age": {
                "method": "integers",
                "kwargs": {"min": 0}
            }
        }
        errors = SparkSpecValidator.validate(spec)
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
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 1
        assert "requires parameter 'std'" in errors[0]
    
    def test_invalid_dates_wrong_param_name(self):
        """Test error when dates uses 'format' instead of unified 'date_format'."""
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
        errors = SparkSpecValidator.validate(spec)
        assert len(errors) == 2
        assert any("requires parameter 'date_format'" in error.lower() for error in errors)
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
        SparkSpecValidator.validate_and_raise(spec)
    
    def test_validate_and_raise_invalid(self):
        """Test that invalid spec raises SpecValidationError."""
        spec = {
            "age": {
                "method": "invalid_method",
                "kwargs": {}
            }
        }
        with pytest.raises(SpecValidationError) as exc_info:
            SparkSpecValidator.validate_and_raise(spec)
        
        assert "Spark specification validation failed" in str(exc_info.value)
        assert "unknown method" in str(exc_info.value)
