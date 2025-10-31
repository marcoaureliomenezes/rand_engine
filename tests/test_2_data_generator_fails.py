"""
Tests for DataGenerator with INVALID specifications.

These tests validate that the DataGenerator properly raises exceptions
when provided with incorrect spec configurations.
"""

import pytest
from rand_engine.main.data_generator import DataGenerator
from rand_engine.validators.exceptions import SpecValidationError
from tests.fixtures.f1_data_generator_specs_wrong import (
    wrong_spec_not_dict,
    wrong_spec_empty,
    wrong_spec_missing_method,
    wrong_spec_unknown_method,
    wrong_spec_method_not_string,
    wrong_spec_missing_required_param,
    wrong_spec_wrong_param_type,
    wrong_spec_both_kwargs_and_args,
    wrong_spec_missing_kwargs_and_args,
    wrong_spec_method_requires_cols,
    wrong_spec_cols_not_list,
    wrong_spec_transformers_not_list,
    wrong_spec_transformer_not_callable,
    wrong_spec_kwargs_not_dict,
    wrong_spec_column_not_dict,
)


def test_spec_not_dict(wrong_spec_not_dict):
    """Test that DataGenerator raises exception when spec is not a dictionary."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_not_dict, validate=True)
    
    assert "must be a dictionary" in str(exc_info.value)


def test_spec_empty(wrong_spec_empty):
    """Test that DataGenerator raises exception when spec is empty."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_empty, validate=True)
    
    assert "cannot be empty" in str(exc_info.value)


def test_spec_missing_method(wrong_spec_missing_method):
    """Test that DataGenerator raises exception when 'method' field is missing."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_missing_method, validate=True)
    
    assert "method" in str(exc_info.value).lower()
    assert "required" in str(exc_info.value).lower()


def test_spec_unknown_method(wrong_spec_unknown_method):
    """Test that DataGenerator raises exception when method doesn't exist."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_unknown_method, validate=True)
    
    assert "does not exist" in str(exc_info.value)
    assert "generate_integers" in str(exc_info.value)


def test_spec_method_not_string(wrong_spec_method_not_string):
    """Test that DataGenerator raises exception when method is not a string."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_method_not_string, validate=True)
    
    assert "must be string" in str(exc_info.value)


def test_spec_missing_required_param(wrong_spec_missing_required_param):
    """Test that DataGenerator raises exception when required parameter is missing."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_missing_required_param, validate=True)
    
    assert "requires parameter" in str(exc_info.value)
    assert "max" in str(exc_info.value)


def test_spec_wrong_param_type(wrong_spec_wrong_param_type):
    """Test that DataGenerator raises exception when parameter has wrong type."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_wrong_param_type, validate=True)
    
    assert "must be int" in str(exc_info.value)


def test_spec_both_kwargs_and_args(wrong_spec_both_kwargs_and_args):
    """Test that DataGenerator raises exception when both kwargs and args are present."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_both_kwargs_and_args, validate=True)
    
    assert "cannot have both" in str(exc_info.value)
    assert "simultaneously" in str(exc_info.value)


def test_spec_missing_kwargs_and_args(wrong_spec_missing_kwargs_and_args):
    """Test that DataGenerator raises exception when neither kwargs nor args are present."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_missing_kwargs_and_args, validate=True)
    
    assert "requires" in str(exc_info.value)
    assert ("kwargs" in str(exc_info.value) or "args" in str(exc_info.value))


def test_spec_method_requires_cols(wrong_spec_method_requires_cols):
    """Test that DataGenerator raises exception when 'cols' field is missing for methods that require it."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_method_requires_cols, validate=True)
    
    assert "requires" in str(exc_info.value)
    assert "cols" in str(exc_info.value)


def test_spec_cols_not_list(wrong_spec_cols_not_list):
    """Test that DataGenerator raises exception when 'cols' is not a list."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_cols_not_list, validate=True)
    
    assert "cols" in str(exc_info.value)
    assert "must be list" in str(exc_info.value)


def test_spec_transformers_not_list(wrong_spec_transformers_not_list):
    """Test that DataGenerator raises exception when transformers is not a list."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_transformers_not_list, validate=True)
    
    assert "transformers" in str(exc_info.value)
    assert "must be list" in str(exc_info.value)


def test_spec_transformer_not_callable(wrong_spec_transformer_not_callable):
    """Test that DataGenerator raises exception when transformer is not callable."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_transformer_not_callable, validate=True)
    
    assert "callable" in str(exc_info.value)


def test_spec_kwargs_not_dict(wrong_spec_kwargs_not_dict):
    """Test that DataGenerator raises exception when kwargs is not a dictionary."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_kwargs_not_dict, validate=True)
    
    assert "kwargs" in str(exc_info.value)
    assert "must be dictionary" in str(exc_info.value)


def test_spec_column_not_dict(wrong_spec_column_not_dict):
    """Test that DataGenerator raises exception when column configuration is not a dictionary."""
    with pytest.raises(SpecValidationError) as exc_info:
        DataGenerator(wrong_spec_column_not_dict, validate=True)
    
    assert "configuration must be a dictionary" in str(exc_info.value)


def test_multiple_wrong_specs_sequential():
    """Test multiple wrong specs in sequence to ensure validator works consistently."""
    wrong_specs = [
        {"age": {"method": "unknown_method", "kwargs": {"min": 0}}},
        {"age": {"kwargs": {"min": 0, "max": 100}}},  # Missing method
        {"age": "not_a_dict"},
    ]
    
    for spec in wrong_specs:
        with pytest.raises(SpecValidationError):
            DataGenerator(spec, validate=True)


def test_valid_spec_should_not_raise():
    """Test that a valid spec does NOT raise exception."""
    valid_spec = {
        "id": {"method": "int_zfilled", "kwargs": {"length": 8}},
        "age": {"method": "integers", "kwargs": {"min": 0, "max": 100}},
        "salary": {"method": "floats", "kwargs": {"min": 0, "max": 10000, "decimals": 2}},
    }
    
    # Should not raise any exception
    generator = DataGenerator(valid_spec, validate=True)
    df = generator.size(10).get_df()
    
    assert df.shape[0] == 10
    assert set(df.columns) == set(valid_spec.keys())
