"""
Fixtures with WRONG specifications to test validation in DataGenerator.

These specs are intentionally incorrect to validate that the SpecValidator
properly catches errors and raises appropriate exceptions.
"""

import pytest


@pytest.fixture(scope="function")
def wrong_spec_not_dict():
    """Spec is not a dictionary - should be a dict."""
    return ["this", "is", "a", "list", "not", "a", "dict"]


@pytest.fixture(scope="function")
def wrong_spec_empty():
    """Empty spec - must have at least one column."""
    return {}


@pytest.fixture(scope="function")
def wrong_spec_missing_method():
    """Column configuration missing 'method' field."""
    return {
        "age": {
            "kwargs": {"min": 0, "max": 100}
            # Missing 'method' field
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_unknown_method():
    """Method name doesn't exist."""
    return {
        "age": {
            "method": "generate_integers",  # Wrong method name
            "kwargs": {"min": 0, "max": 100}
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_method_not_string():
    """Method field is not a string."""
    return {
        "age": {
            "method": 12345,  # Should be string
            "kwargs": {"min": 0, "max": 100}
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_missing_required_param():
    """Missing required parameter 'max' for integers method."""
    return {
        "age": {
            "method": "integers",
            "kwargs": {"min": 0}  # Missing 'max'
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_wrong_param_type():
    """Parameter has wrong type - should be int, got str."""
    return {
        "age": {
            "method": "integers",
            "kwargs": {"min": "zero", "max": "hundred"}  # Should be int
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_both_kwargs_and_args():
    """Cannot have both 'kwargs' and 'args' simultaneously."""
    return {
        "age": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 100},
            "args": [0, 100]  # Can't have both
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_missing_kwargs_and_args():
    """Missing both 'kwargs' and 'args' - need at least one."""
    return {
        "age": {
            "method": "integers"
            # Missing both 'kwargs' and 'args'
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_method_requires_cols():
    """Method 'distincts_map' requires 'cols' field but it's missing."""
    return {
        "device_os": {
            "method": "distincts_map",
            "kwargs": {"distincts": {
                "smartphone": ["android", "ios"],
                "desktop": ["windows", "linux"]
            }}
            # Missing 'cols' field
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_cols_not_list():
    """'cols' field must be a list, not a string."""
    return {
        "device_os": {
            "method": "distincts_map",
            "cols": "device_type",  # Should be list like ["device_type", "os_type"]
            "kwargs": {"distincts": {
                "smartphone": ["android", "ios"]
            }}
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_transformers_not_list():
    """Transformers must be a list, not a single function."""
    return {
        "name": {
            "method": "distincts",
            "kwargs": {"distincts": ["john", "mary", "peter"]},
            "transformers": lambda x: x.upper()  # Should be a list
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_transformer_not_callable():
    """Transformer must be callable (function/lambda), not a string."""
    return {
        "name": {
            "method": "distincts",
            "kwargs": {"distincts": ["john", "mary", "peter"]},
            "transformers": ["not_a_function"]  # Should be callable
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_kwargs_not_dict():
    """'kwargs' must be a dictionary, not a list."""
    return {
        "age": {
            "method": "integers",
            "kwargs": [0, 100]  # Should be dict like {"min": 0, "max": 100}
        }
    }


@pytest.fixture(scope="function")
def wrong_spec_column_not_dict():
    """Column configuration must be a dictionary, not a string."""
    return {
        "age": "this should be a dict"  # Should be {"method": "integers", "kwargs": {...}}
    }

