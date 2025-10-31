"""
Common Specification Validator for Rand Engine.

This module provides shared validation logic for methods that are common to both
DataGenerator (NPCore) and SparkGenerator (SparkCore).

Methods validated here:
- integers, int_zfilled
- floats, floats_normal
- booleans
- distincts, distincts_prop
- dates, unix_timestamps
- uuid4

IMPORTANT DIFFERENCES HANDLED:
------------------------------
1. integers: Accepts both 'int_type' (NPCore) and 'dtype' (SparkCore)
   - NPCore int_type: ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
   - SparkCore dtype: ["int", "bigint", "long", "integer"]

2. dates/unix_timestamps: Unified to use 'date_format' parameter
   - Both cores now accept 'date_format' parameter
   - SparkCore maintains backward compatibility with 'formato'
"""

from typing import Dict, List, Any


class CommonValidator:
    """
    Shared validation logic for methods available in both NPCore and SparkCore.
    """
    
    # Complete mapping of common methods with their signatures and examples
    METHOD_SPECS = {
        "integers": {
            "description": "Generates random integers within a range",
            "params": {
                "required": {"min": int, "max": int},
                "optional": {"int_type": str, "dtype": str}  # NPCore uses int_type, SparkCore uses dtype
            },
            "validation": {
                "int_type": ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64'],
                "dtype": ["int", "bigint", "long", "integer"]
            },
            "example": {
                "age": {
                    "method": "integers",
                    "kwargs": {"min": 18, "max": 65, "int_type": "int32"}  # or dtype="int" for Spark
                }
            }
        },
        "int_zfilled": {
            "description": "Generates numeric strings with leading zeros (IDs, codes)",
            "params": {
                "required": {"length": int},
                "optional": {}
            },
            "example": {
                "code": {
                    "method": "int_zfilled",
                    "kwargs": {"length": 8}
                }
            }
        },
        "floats": {
            "description": "Generates random decimal numbers within a range",
            "params": {
                "required": {"min": (int, float), "max": (int, float)},
                "optional": {"decimals": int}
            },
            "example": {
                "price": {
                    "method": "floats",
                    "kwargs": {"min": 0, "max": 1000, "decimals": 2}
                }
            }
        },
        "floats_normal": {
            "description": "Generates decimal numbers with normal (Gaussian) distribution",
            "params": {
                "required": {"mean": (int, float), "std": (int, float)},
                "optional": {"decimals": int}
            },
            "example": {
                "height": {
                    "method": "floats_normal",
                    "kwargs": {"mean": 170, "std": 10, "decimals": 2}
                }
            }
        },
        "booleans": {
            "description": "Generates boolean values (True/False) with configurable probability",
            "params": {
                "required": {},
                "optional": {"true_prob": float}
            },
            "example": {
                "active": {
                    "method": "booleans",
                    "kwargs": {"true_prob": 0.7}
                }
            }
        },
        "distincts": {
            "description": "Randomly selects values from a list (uniform distribution)",
            "params": {
                "required": {"distincts": list},
                "optional": {}
            },
            "example": {
                "plan": {
                    "method": "distincts",
                    "kwargs": {"distincts": ["free", "standard", "premium"]}
                }
            }
        },
        "distincts_prop": {
            "description": "Selects values from a dictionary with proportional weights",
            "params": {
                "required": {"distincts": dict},  # {value: weight, ...}
                "optional": {}
            },
            "example": {
                "device": {
                    "method": "distincts_prop",
                    "kwargs": {"distincts": {"mobile": 70, "desktop": 30}}
                }
            }
        },
        "unix_timestamps": {
            "description": "Generates random Unix timestamps within a time period",
            "params": {
                "required": {"start": str, "end": str, "date_format": str},
                "optional": {}
            },
            "example": {
                "created_at": {
                    "method": "unix_timestamps",
                    "kwargs": {
                        "start": "01-01-2024",
                        "end": "31-12-2024",
                        "date_format": "%d-%m-%Y"
                    }
                }
            }
        },
        "dates": {
            "description": "Generates random date strings within a time period (formatted)",
            "params": {
                "required": {"start": str, "end": str, "date_format": str},
                "optional": {}
            },
            "example": {
                "birth_date": {
                    "method": "dates",
                    "kwargs": {
                        "start": "1970-01-01",
                        "end": "2005-12-31",
                        "date_format": "%Y-%m-%d"
                    }
                }
            }
        },
        "uuid4": {
            "description": "Generates UUID version 4 identifiers (random)",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "id": {
                    "method": "uuid4"
                }
            }
        }
    }
    
    @classmethod
    def validate_column(cls, col_name: str, col_config: Dict[str, Any]) -> List[str]:
        """
        Validates a single column configuration.
        
        Args:
            col_name: Name of the column
            col_config: Dictionary with 'method' and 'kwargs'
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # 1. Check if column config is a dictionary
        if not isinstance(col_config, dict):
            errors.append(
                f"❌ Column '{col_name}': Configuration must be a dictionary\n"
                f"   Got: {type(col_config).__name__}"
            )
            return errors
        
        # 2. Check required fields
        if "method" not in col_config:
            errors.append(f"❌ Column '{col_name}': Missing 'method' field")
            return errors
        
        method = col_config["method"]
        
        # 3. Check if method is in common methods
        if method not in cls.METHOD_SPECS:
            # Not a common method - will be handled by advanced validator
            return []
        
        spec = cls.METHOD_SPECS[method]
        kwargs = col_config.get("kwargs", {})
        
        # 4. Check if kwargs is a dictionary
        if not isinstance(kwargs, dict):
            errors.append(
                f"❌ Column '{col_name}': 'kwargs' must be dictionary\n"
                f"   Got: {type(kwargs).__name__}"
            )
            return errors
        
        # 5. Validate required parameters
        required_params = spec["params"]["required"]
        for param, param_type in required_params.items():
            if param not in kwargs:
                example = spec["example"]
                type_name = cls._get_type_name(param_type)
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' requires parameter '{param}'\n"
                    f"   Expected type: {type_name}\n"
                    f"   Correct example:\n{cls._format_example(example)}"
                )
            else:
                # Type validation
                value = kwargs[param]
                if not cls._check_type(value, param_type):
                    type_name = cls._get_type_name(param_type)
                    errors.append(
                        f"⚠️  Column '{col_name}': parameter '{param}' must be {type_name}\n"
                        f"   Got: {type(value).__name__}"
                    )
        
        # 6. Validate optional parameters and check for unknown parameters
        optional_params = spec["params"]["optional"]
        all_valid_params = set(required_params.keys()) | set(optional_params.keys())
        
        unknown_params = set(kwargs.keys()) - all_valid_params
        if unknown_params:
            unknown_list = "', '".join(unknown_params)
            valid_list = ", ".join(f"'{p}'" for p in sorted(all_valid_params))
            errors.append(
                f"⚠️  Column '{col_name}': unknown parameters: '{unknown_list}'\n"
                f"   Valid parameters for '{method}': {valid_list}"
            )
        
        # Type validation for optional params that are present
        for param, value in kwargs.items():
            if param in optional_params:
                # Type validation for optional params
                param_type = optional_params[param]
                if not cls._check_type(value, param_type):
                    type_name = cls._get_type_name(param_type)
                    errors.append(
                        f"⚠️  Column '{col_name}': parameter '{param}' must be {type_name}\n"
                        f"   Got: {type(value).__name__}"
                    )
        
        # 7. Special validation for integers method (int_type vs dtype)
        if method == "integers":
            validation = spec.get("validation", {})
            
            # Check int_type if present
            if "int_type" in kwargs:
                allowed = validation["int_type"]
                if kwargs["int_type"] not in allowed:
                    errors.append(
                        f"⚠️  Column '{col_name}': Invalid 'int_type' value\n"
                        f"   Got: '{kwargs['int_type']}'\n"
                        f"   Allowed for NPCore: {allowed}"
                    )
            
            # Check dtype if present
            if "dtype" in kwargs:
                allowed = validation["dtype"]
                if kwargs["dtype"] not in allowed:
                    errors.append(
                        f"⚠️  Column '{col_name}': Invalid 'dtype' value\n"
                        f"   Got: '{kwargs['dtype']}'\n"
                        f"   Allowed for SparkCore: {allowed}"
                    )
            
            # Both int_type and dtype present (unusual but valid for cross-compatibility)
            if "int_type" in kwargs and "dtype" in kwargs:
                errors.append(
                    f"⚠️  Column '{col_name}': Both 'int_type' and 'dtype' specified\n"
                    f"   This is allowed but unusual. Use 'int_type' for DataGenerator, 'dtype' for SparkGenerator"
                )
        
        # 8. Special validation for booleans true_prob range
        if method == "booleans" and "true_prob" in kwargs:
            prob = kwargs["true_prob"]
            if not (0 <= prob <= 1):
                errors.append(
                    f"⚠️  Column '{col_name}': 'true_prob' must be between 0 and 1\n"
                    f"   Got: {prob}"
                )
        
        # 9. Special validation for distincts (non-empty list)
        if method == "distincts" and "distincts" in kwargs:
            distincts_list = kwargs["distincts"]
            if not isinstance(distincts_list, list):
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' must be a list\n"
                    f"   Got: {type(distincts_list).__name__}"
                )
            elif len(distincts_list) == 0:
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' list cannot be empty"
                )
        
        # 10. Special validation for distincts_prop (non-empty dict with numeric values)
        if method == "distincts_prop" and "distincts" in kwargs:
            distincts_dict = kwargs["distincts"]
            if not isinstance(distincts_dict, dict):
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' must be a dictionary for distincts_prop\n"
                    f"   Got: {type(distincts_dict).__name__}"
                )
            elif len(distincts_dict) == 0:
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' dictionary cannot be empty"
                )
            else:
                # Check that all values are integers (weights)
                for key, weight in distincts_dict.items():
                    if not isinstance(weight, int):
                        errors.append(
                            f"⚠️  Column '{col_name}': Weight for '{key}' must be an integer\n"
                            f"   Got: {type(weight).__name__} ({weight})"
                        )
        
        return errors
    
    @classmethod
    def _check_type(cls, value: Any, expected_type) -> bool:
        """
        Check if value matches expected type.
        Handles both single types and tuples of types.
        """
        if isinstance(expected_type, tuple):
            return isinstance(value, expected_type)
        return isinstance(value, expected_type)
    
    @classmethod
    def _get_type_name(cls, type_spec: Any) -> str:
        """Gets friendly name for type specification."""
        if isinstance(type_spec, tuple):
            types = [t.__name__ for t in type_spec]
            return " or ".join(types)
        return type_spec.__name__
    
    @classmethod
    def _format_example(cls, example: Dict) -> str:
        """Format example dictionary for display."""
        import json
        return "   " + json.dumps(example, indent=6).replace("\n", "\n   ")
