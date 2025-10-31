"""
Spark Specification (specs) validator for Rand Engine v1.0.

This module provides comprehensive validation with educational messages for Spark specs,
helping users learn how to use SparkGenerator correctly.

SparkGenerator uses PySpark and SparkCore methods for distributed data generation.

This validator delegates to:
- CommonValidator: Methods shared between DataGenerator and SparkGenerator

IMPORTANT NOTES:
----------------
1. Common methods use unified parameters (date_format, int_type/dtype, decimals, true_prob, distincts)
2. All Spark methods receive (spark, F, df, col_name, **kwargs) signature  
3. Advanced PyCore methods (distincts_map, distincts_multi_map, distincts_map_prop, complex_distincts) 
   have dummy implementations in SparkCore that return NULL values for API compatibility only
"""

from typing import Dict, List, Any, Optional
from rand_engine.validators.exceptions import SpecValidationError
from rand_engine.validators.common_validator import CommonValidator


class SparkSpecValidator:
    """
    Educational Spark data specification validator for Rand Engine.
    
    Delegates validation to CommonValidator for shared methods.
    Provides descriptive messages with correct usage examples for each
    available SparkCore method, helping users learn quickly.
    """
    
    # Complete mapping of Spark methods - uses CommonValidator + dummy methods
    METHOD_SPECS = {
        **CommonValidator.METHOD_SPECS,
        # Dummy methods for API compatibility - return NULL in Spark
        "distincts_map": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {"required": {}, "optional": {}},
            "example": {"mapped": {"method": "distincts_map", "kwargs": {}}}
        },
        "distincts_multi_map": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {"required": {}, "optional": {}},
            "example": {"multi_mapped": {"method": "distincts_multi_map", "kwargs": {}}}
        },
        "distincts_map_prop": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {"required": {}, "optional": {}},
            "example": {"map_prop": {"method": "distincts_map_prop", "kwargs": {}}}
        },
        "complex_distincts": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {"required": {}, "optional": {}},
            "example": {"complex": {"method": "complex_distincts", "kwargs": {}}}
        }
    }
    
    # Legacy METHOD_SPECS maintained for reference
    _LEGACY_METHOD_SPECS = {
        "integers": {
            "description": "Generates random integers within a range (Spark distributed)",
            "params": {
                "required": {"min": int, "max": int},
                "optional": {"dtype": str, "int_type": str}
            },
            "example": {
                "age": {
                    "method": "integers",
                    "kwargs": {"min": 18, "max": 65, "dtype": "int"}
                }
            }
        },
        "int_zfilled": {
            "description": "Generates numeric strings with leading zeros (IDs, codes) - Spark version",
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
            "description": "Generates random decimal numbers within a range (Spark distributed)",
            "params": {
                "required": {"min": (int, float), "max": (int, float)},
                "optional": {"decimals": int}
            },
            "example": {
                "price": {
                    "method": "floats",
                    "kwargs": {"min": 0.0, "max": 1000.0, "decimals": 2}
                }
            }
        },
        "floats_normal": {
            "description": "Generates decimal numbers with normal (Gaussian) distribution (Spark)",
            "params": {
                "required": {"mean": (int, float), "std": (int, float)},
                "optional": {"decimals": int}
            },
            "example": {
                "height": {
                    "method": "floats_normal",
                    "kwargs": {"mean": 170.0, "std": 10.0, "decimals": 2}
                }
            }
        },
        "booleans": {
            "description": "Generates boolean values (True/False) with configurable probability (Spark)",
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
            "description": "Randomly selects values from a list (uniform distribution) - Spark version",
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
            "description": "Selects values from a dictionary with proportional weights (Spark)",
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
        "uuid4": {
            "description": "Generates UUID version 4 identifiers (random) - Spark native",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "id": {
                    "method": "uuid4",
                    "kwargs": {}
                }
            }
        },
        "dates": {
            "description": "Generates random date strings within a time period (Spark formatted)",
            "params": {
                "required": {"start": str, "end": str, "date_format": str},
                "optional": {}
            },
            "example": {
                "created_at": {
                    "method": "dates",
                    "kwargs": {
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "date_format": "%Y-%m-%d"
                    }
                }
            }
        },
        "unix_timestamps": {
            "description": "Generates random Unix timestamps within a time period (Spark internal)",
            "params": {
                "required": {"start": str, "end": str, "date_format": str},
                "optional": {}
            },
            "example": {
                "timestamp": {
                    "method": "unix_timestamps",
                    "kwargs": {
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "date_format": "%Y-%m-%d"
                    }
                }
            }
        },
        "distincts_map": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "mapped": {
                    "method": "distincts_map",
                    "kwargs": {}
                }
            }
        },
        "distincts_multi_map": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "multi_mapped": {
                    "method": "distincts_multi_map",
                    "kwargs": {}
                }
            }
        },
        "distincts_map_prop": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "map_prop": {
                    "method": "distincts_map_prop",
                    "kwargs": {}
                }
            }
        },
        "complex_distincts": {
            "description": "Dummy method for API compatibility - returns NULL values",
            "params": {
                "required": {},
                "optional": {}
            },
            "example": {
                "complex": {
                    "method": "complex_distincts",
                    "kwargs": {}
                }
            }
        }
    }
    
    @classmethod
    def validate(cls, spec: Dict[str, Any]) -> List[str]:
        """
        Validates a Spark specification and returns list of error/warning messages.
        
        Args:
            spec: Dictionary mapping column names to their generation configs
            
        Returns:
            List of validation error messages (empty if valid)
            
        Example:
            >>> errors = SparkSpecValidator.validate(my_spec)
            >>> if errors:
            >>>     for error in errors:
            >>>         print(error)
        """
        errors = []
        
        # 1. Check if spec is a dictionary
        if not isinstance(spec, dict):
            errors.append(
                f"❌ Specification must be a dictionary, got {type(spec).__name__}\n"
                "   Correct format:\n"
                "   spec = {'column_name': {'method': 'integers', 'kwargs': {...}}}"
            )
            return errors
        
        # 2. Check if spec is not empty
        if not spec:
            errors.append("⚠️  Specification is empty. Add at least one column definition.")
            return errors
        
        # 3. Validate each column
        for col_name, col_config in spec.items():
            errors.extend(cls._validate_column(col_name, col_config))
        
        return errors
    
    @classmethod
    def _validate_column(cls, col_name: str, col_config: Any) -> List[str]:
        """Validates a single column configuration - delegates to CommonValidator."""
        errors = []
        
        # Check if column config is a dict
        if not isinstance(col_config, dict):
            errors.append(
                f"❌ Column '{col_name}': configuration must be dictionary, got {type(col_config).__name__}\n"
                "   Correct format:\n"
                f"   '{col_name}': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}"
            )
            return errors
        
        # Check for 'method' key
        if "method" not in col_config:
            errors.append(
                f"❌ Column '{col_name}': missing required 'method' key\n"
                "   Add method specification:\n"
                f"   '{col_name}': {{'method': 'integers', 'kwargs': {{...}}}}"
            )
            return errors
        
        method = col_config["method"]
        
        # Check if method is a string
        if not isinstance(method, str):
            errors.append(
                f"❌ Column '{col_name}': 'method' must be string, got {type(method).__name__}"
            )
            return errors
        
        # Check if method is supported
        if method not in cls.METHOD_SPECS:
            available_methods = ", ".join(sorted(cls.METHOD_SPECS.keys()))
            errors.append(
                f"❌ Column '{col_name}': unknown method '{method}'\n"
                f"   Available Spark methods: {available_methods}"
            )
            return errors
        
        # Check if kwargs exists
        if "kwargs" not in col_config:
            errors.append(
                f"❌ Column '{col_name}': missing 'kwargs' dictionary"
            )
            return errors
        
        # DELEGATE TO CommonValidator for shared methods
        common_errors = CommonValidator.validate_column(col_name, col_config)
        if common_errors:
            errors.extend(common_errors)
        
        # Validate transformers if present (not part of common validator)
        if "transformers" in col_config:
            errors.extend(cls._validate_transformers(col_name, col_config["transformers"]))
        
        return errors
    
    @classmethod
    def _validate_kwargs(cls, col_name: str, method: str, col_config: Dict, method_spec: Dict) -> List[str]:
        """
        Legacy method kept for backward compatibility.
        Validation is now delegated to CommonValidator in _validate_column.
        """
        # This method is now handled by CommonValidator in _validate_column
        return []
    
    @classmethod
    def _validate_transformers(cls, col_name: str, transformers: Any) -> List[str]:
        """Validates transformers configuration."""
        errors = []
        
        if not isinstance(transformers, list):
            errors.append(
                f"❌ Column '{col_name}': 'transformers' must be list, got {type(transformers).__name__}\n"
                "   Example: 'transformers': [lambda x: x.upper()]"
            )
            return errors
        
        for i, transformer in enumerate(transformers):
            if not callable(transformer):
                errors.append(
                    f"❌ Column '{col_name}': transformer at index {i} must be callable\n"
                    "   Use lambda or function: lambda x: x.upper()"
                )
        
        return errors
    
    @staticmethod
    def _check_type(value: Any, expected_type: Any) -> bool:
        """Checks if value matches expected type (handles tuples of types)."""
        if isinstance(expected_type, tuple):
            return isinstance(value, expected_type)
        return isinstance(value, expected_type)
    
    @staticmethod
    def _get_type_name(type_spec: Any) -> str:
        """Gets friendly name for type specification."""
        if isinstance(type_spec, tuple):
            types = [t.__name__ for t in type_spec]
            return " or ".join(types)
        return type_spec.__name__
    
    @staticmethod
    def _format_example(example: Dict) -> str:
        """Formats example dict as readable string."""
        import json
        return json.dumps(example, indent=4)
    
    @classmethod
    def validate_and_raise(cls, spec: Dict[str, Any]) -> None:
        """
        Validates specification and raises SpecValidationError if invalid.
        
        Use this when you want to fail fast on invalid specs.
        
        Args:
            spec: Spark specification to validate
            
        Raises:
            SpecValidationError: If specification is invalid
            
        Example:
            >>> try:
            >>>     SparkSpecValidator.validate_and_raise(my_spec)
            >>> except SpecValidationError as e:
            >>>     print(f"Invalid spec: {e}")
        """
        errors = cls.validate(spec)
        if errors:
            error_msg = "\n\n".join(errors)
            raise SpecValidationError(f"Spark specification validation failed:\n\n{error_msg}")
