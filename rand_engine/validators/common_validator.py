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

    # ========================================================================
    # HIGH-LEVEL VALIDATION METHODS (for SparkGenerator)
    # ========================================================================
    
    @classmethod
    def validate_spark_spec(cls, spec: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Validates a complete SparkGenerator specification.
        
        Args:
            spec: Specification dictionary {column_name: {method: ..., kwargs: ...}}
        
        Returns:
            List of strings describing found errors with correction examples
        """
        errors = []
        
        # Validate that spec is a dictionary
        if not isinstance(spec, dict):
            errors.append(
                f"❌ Spec must be a dictionary, got {type(spec).__name__}\n"
                f"   Correct example:\n"
                f"   spec = {{'age': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}}}"
            )
            return errors
        
        # Validate that spec is not empty
        if len(spec) == 0:
            errors.append(
                "❌ Spec cannot be empty\n"
                "   Minimal example:\n"
                "   spec = {'id': {'method': 'int_zfilled', 'kwargs': {'length': 8}}}"
            )
            return errors
        
        # Validate each column
        for col_name, col_config in spec.items():
            errors.extend(cls._validate_spark_column(col_name, col_config))
        
        return errors
    
    @classmethod
    def _validate_spark_column(cls, col_name: str, col_config: Any) -> List[str]:
        """Validates individual Spark column configuration."""
        errors = []
        
        # Validate that col_config is a dictionary
        if not isinstance(col_config, dict):
            errors.append(
                f"❌ Column '{col_name}': configuration must be a dictionary, got {type(col_config).__name__}\n"
                f"   Fix to:\n"
                f"   '{col_name}': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}"
            )
            return errors
        
        # Validate presence of 'method' field
        if "method" not in col_config:
            errors.append(
                f"❌ Column '{col_name}': field 'method' is required\n"
                f"   Fix to:\n"
                f"   '{col_name}': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}"
            )
            return errors
        
        method = col_config["method"]
        
        # Validate that method is a valid string
        if not isinstance(method, str):
            if callable(method):
                errors.append(
                    f"❌ Column '{col_name}': use string identifier instead of callable\n"
                    f"   Old format (not recommended): {{'method': SparkCore.gen_ints, ...}}\n"
                    f"   New format (correct): {{'method': 'integers', ...}}"
                )
            else:
                errors.append(
                    f"❌ Column '{col_name}': 'method' must be string, got {type(method).__name__}\n"
                    f"   Available methods: {', '.join(sorted(cls.METHOD_SPECS.keys()))}"
                )
            return errors
        
        # Check if method exists in CommonValidator (SparkGenerator only uses common methods)
        if method not in cls.METHOD_SPECS:
            # Allow advanced methods with warning (they return NULL in Spark)
            advanced_methods = ["distincts_map", "distincts_multi_map", "distincts_map_prop", "complex_distincts", "distincts_external"]
            if method in advanced_methods:
                errors.append(
                    f"⚠️  Column '{col_name}': method '{method}' is a dummy in SparkGenerator (returns NULL)\n"
                    f"   This method is only fully implemented in DataGenerator\n"
                    f"   Available SparkGenerator methods: {', '.join(sorted(cls.METHOD_SPECS.keys()))}"
                )
                return errors
            else:
                available_methods = ", ".join(f"'{m}'" for m in sorted(cls.METHOD_SPECS.keys()))
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' does not exist\n"
                    f"   Available methods: {available_methods}"
                )
                return errors
        
        # Validate kwargs vs args format
        has_kwargs = "kwargs" in col_config
        has_args = "args" in col_config
        
        if has_kwargs and has_args:
            errors.append(
                f"❌ Column '{col_name}': cannot have both 'kwargs' and 'args' simultaneously\n"
                f"   Use only 'kwargs' (recommended)"
            )
            return errors
        
        if not has_kwargs and not has_args:
            errors.append(
                f"❌ Column '{col_name}': method '{method}' requires 'kwargs' or 'args'"
            )
            return errors
        
        # Convert legacy 'args' to 'kwargs' for validation
        if has_args:
            if not isinstance(col_config["args"], (list, tuple)):
                errors.append(
                    f"❌ Column '{col_name}': 'args' must be list or tuple, got {type(col_config['args']).__name__}\n"
                    f"   Or better yet, use 'kwargs' (recommended format)"
                )
                return errors
            # Legacy format - skip detailed validation
            return errors
        
        # Use validate_column for kwargs validation
        validation_config = {"method": method, "kwargs": col_config["kwargs"]}
        column_errors = cls.validate_column(col_name, validation_config)
        errors.extend(column_errors)
        
        return errors
    
    @classmethod
    def validate_spark_and_raise(cls, spec: Dict[str, Dict[str, Any]]) -> None:
        """
        Validates Spark spec and raises educational exception if there are errors.
        
        Use this for SparkGenerator specs that require validation.
        
        Args:
            spec: Spark specification dictionary
        
        Raises:
            SpecValidationError: If spec contains errors, with detailed messages
        """
        from rand_engine.validators.exceptions import SpecValidationError
        
        errors = cls.validate_spark_spec(spec)
        if errors:
            separator = "\n" + "="*80 + "\n"
            error_message = (
                f"\n{'='*80}\n"
                f"SPARKGENERATOR SPEC VALIDATION ERROR\n"
                f"{'='*80}\n\n"
                f"Found {len(errors)} error(s) in specification:\n\n" +
                separator.join(errors) +
                f"\n\n{'='*80}\n"
                f"📚 Documentation: https://github.com/marcoaureliomenezes/rand_engine\n"
                f"{'='*80}\n"
            )
            raise SpecValidationError(error_message)
    
    @classmethod
    def validate_spark_with_warnings(cls, spec: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validates Spark spec and prints formatted errors if any.
        
        Returns:
            True if spec is valid, False otherwise
        """
        errors = cls.validate_spark_spec(spec)
        if errors:
            print(f"\n{'='*80}")
            print(f"❌ SPARK VALIDATION FAILED - {len(errors)} error(s) found")
            print(f"{'='*80}\n")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}\n")
            print(f"{'='*80}\n")
            return False
        
        print("\n✅ Spark spec validated successfully!\n")
        return True
