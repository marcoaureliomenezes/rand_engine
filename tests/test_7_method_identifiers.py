"""
Tests for method identifier validation in SpecValidator
"""
import pytest
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.exceptions import SpecValidationError
from rand_engine.core._np_core import NPCore


def test_valid_string_method_identifier():
    """Test that valid string identifiers pass validation."""
    spec = {
        "age": {"method": "integers", "kwargs": {"min": 0, "max": 100}},
        "salary": {"method": "floats", "kwargs": {"min": 0, "max": 10000}},
        "active": {"method": "booleans"},
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0, f"Should have no errors, got: {errors}"


def test_invalid_string_method_identifier():
    """Test that invalid string identifiers are rejected."""
    spec = {
        "age": {"method": "invalid_method", "kwargs": {"min": 0, "max": 100}}
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "invalid method identifier 'invalid_method'" in errors[0]
    assert "'integers'" in errors[0]  # Should suggest valid methods


def test_callable_method_still_works():
    """Test that callable methods (old format) still work."""
    spec = {
        "age": {"method": NPCore.gen_ints, "kwargs": {"min": 0, "max": 100}}
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_mixed_string_and_callable_methods():
    """Test that mixing string and callable methods works."""
    spec = {
        "id": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
        "age": {"method": NPCore.gen_ints, "kwargs": {"min": 0, "max": 100}},
        "salary": {"method": "floats", "kwargs": {"min": 0, "max": 10000}},
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_all_valid_identifiers():
    """Test all valid method identifiers."""
    spec = {
        "col_int": {"method": "integers", "kwargs": {"min": 0, "max": 100}},
        "col_int_zfilled": {"method": "int_zfilled", "kwargs": {"min": 0, "max": 100, "length": 4}},
        "col_float": {"method": "floats", "kwargs": {"min": 0, "max": 100}},
        "col_float_normal": {"method": "floats_normal", "kwargs": {"mean": 50, "std": 10}},
        "col_distincts": {"method": "distincts", "kwargs": {"distincts": ["A", "B", "C"]}},
        "col_unix_timestamps": {"method": "unix_timestamps", "kwargs": {"start": "01-01-2020", "end": "31-12-2020"}},
        "col_unique_ids": {"method": "unique_ids", "kwargs": {"strategy": "zint"}},
        "col_bool": {"method": "booleans"},
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0, f"All valid identifiers should pass, got errors: {errors}"


def test_validate_and_raise_with_invalid_identifier():
    """Test that validate_and_raise raises exception for invalid identifier."""
    spec = {
        "age": {"method": "nonexistent_method", "kwargs": {"min": 0, "max": 100}}
    }
    
    with pytest.raises(SpecValidationError) as exc_info:
        SpecValidator.validate_and_raise(spec)
    
    assert "invalid method identifier 'nonexistent_method'" in str(exc_info.value)


def test_typo_in_method_identifier():
    """Test helpful error message for typos."""
    spec = {
        "age": {"method": "integer", "kwargs": {"min": 0, "max": 100}}  # Typo: should be "integers"
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "invalid method identifier 'integer'" in errors[0]
    assert "Valid identifiers are:" in errors[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
