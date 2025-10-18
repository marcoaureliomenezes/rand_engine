"""
Specification (specs) validator for Rand Engine v1.0.

This module provides comprehensive validation with educational messages for specs,
helping users learn how to use the library correctly.
"""

from typing import Dict, List, Any, Optional, Callable
from rand_engine.validators.exceptions import SpecValidationError


class SpecValidator:
    """
    Educational data specification validator for Rand Engine.
    
    Provides descriptive messages with correct usage examples for each
    available method, helping users learn quickly.
    """
    
    # Complete mapping of methods with their signatures and examples
    METHOD_SPECS = {
        "integers": {
            "description": "Generates random integers within a range",
            "params": {
                "required": {"min": int, "max": int},
                "optional": {"int_type": str}
            },
            "example": {
                "age": {
                    "method": "integers",
                    "kwargs": {"min": 18, "max": 65}
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
                "optional": {"round": int}
            },
            "example": {
                "price": {
                    "method": "floats",
                    "kwargs": {"min": 0, "max": 1000, "round": 2}
                }
            }
        },
        "floats_normal": {
            "description": "Generates decimal numbers with normal (Gaussian) distribution",
            "params": {
                "required": {"mean": (int, float), "std": (int, float)},
                "optional": {"round": int}
            },
            "example": {
                "height": {
                    "method": "floats_normal",
                    "kwargs": {"mean": 170, "std": 10, "round": 2}
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
        "distincts_map": {
            "description": "Generates correlated pairs (category, value) - 2 columns",
            "params": {
                "required": {"distincts": dict},  # {category: [values], ...}
                "optional": {}
            },
            "requires_cols": True,
            "example": {
                "device_os": {
                    "method": "distincts_map",
                    "cols": ["device_type", "os_type"],
                    "kwargs": {"distincts": {
                        "smartphone": ["android", "ios"],
                        "desktop": ["windows", "linux"]
                    }}
                }
            }
        },
        "distincts_map_prop": {
            "description": "Generates correlated pairs with weights - 2 columns",
            "params": {
                "required": {"distincts": dict},  # {category: [(value, weight), ...], ...}
                "optional": {}
            },
            "requires_cols": True,
            "example": {
                "product_status": {
                    "method": "distincts_map_prop",
                    "cols": ["product", "status"],
                    "kwargs": {"distincts": {
                        "notebook": [("new", 80), ("used", 20)],
                        "smartphone": [("new", 90), ("used", 10)]
                    }}
                }
            }
        },
        "distincts_multi_map": {
            "description": "Generates Cartesian combinations of multiple lists - N columns",
            "params": {
                "required": {"distincts": dict},  # {category: [[list1], [list2], ...], ...}
                "optional": {}
            },
            "requires_cols": True,
            "example": {
                "company": {
                    "method": "distincts_multi_map",
                    "cols": ["sector", "sub_sector", "size"],
                    "kwargs": {"distincts": {
                        "technology": [
                            ["software", "hardware"],
                            ["small", "medium", "large"]
                        ]
                    }}
                }
            }
        },
        "complex_distincts": {
            "description": "Generates complex strings with replaceable patterns (e.g., IPs, URLs)",
            "params": {
                "required": {
                    "pattern": str,
                    "replacement": str,
                    "templates": list
                },
                "optional": {}
            },
            "example": {
                "ip_address": {
                    "method": "complex_distincts",
                    "kwargs": {
                        "pattern": "x.x.x.x",
                        "replacement": "x",
                        "templates": [
                            {"method": "distincts", "parms": {"distincts": ["192", "10"]}},
                            {"method": "integers", "parms": {"min": 0, "max": 255}},
                            {"method": "integers", "parms": {"min": 0, "max": 255}},
                            {"method": "integers", "parms": {"min": 1, "max": 254}}
                        ]
                    }
                }
            }
        },
        "unix_timestamps": {
            "description": "Generates random Unix timestamps within a time period",
            "params": {
                "required": {"start": str, "end": str, "format": str},
                "optional": {}
            },
            "example": {
                "created_at": {
                    "method": "unix_timestamps",
                    "kwargs": {
                        "start": "01-01-2024",
                        "end": "31-12-2024",
                        "format": "%d-%m-%Y"
                    }
                }
            }
        },
        "unique_ids": {
            "description": "Generates unique identifiers (UUIDs or zerofilled integers)",
            "params": {
                "required": {},
                "optional": {"strategy": str, "length": int}  # strategy: uuid4, uuid1, zint
            },
            "example": {
                "id": {
                    "method": "unique_ids",
                    "kwargs": {"strategy": "zint", "length": 12}
                }
            }
        }
    }

    @staticmethod
    def validate(spec: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Validates a specification and returns a list of detailed errors with examples.
        
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
                "   spec = {'id': {'method': 'unique_ids', 'kwargs': {'strategy': 'zint'}}}"
            )
            return errors
        
        # Validate each column
        for col_name, col_config in spec.items():
            errors.extend(SpecValidator._validate_column(col_name, col_config))
        
        return errors

    @staticmethod
    def _validate_column(col_name: str, col_config: Any) -> List[str]:
        """Validates individual column configuration with educational messages."""
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
                    f"   Old format (not recommended): {{'method': NPCore.gen_ints, ...}}\n"
                    f"   New format (correct): {{'method': 'integers', ...}}"
                )
            else:
                errors.append(
                    f"❌ Column '{col_name}': 'method' must be string, got {type(method).__name__}\n"
                    f"   Available methods: {', '.join(sorted(SpecValidator.METHOD_SPECS.keys()))}"
                )
            return errors
        
        # Validate that the method exists
        if method not in SpecValidator.METHOD_SPECS:
            available_methods = ", ".join(f"'{m}'" for m in sorted(SpecValidator.METHOD_SPECS.keys()))
            errors.append(
                f"❌ Column '{col_name}': method '{method}' does not exist\n"
                f"   Available methods: {available_methods}\n"
                f"   Did you mean one of these?\n" +
                SpecValidator._suggest_similar_method(method)
            )
            return errors
        
        method_spec = SpecValidator.METHOD_SPECS[method]
        
        # Validate kwargs vs args format
        has_kwargs = "kwargs" in col_config
        has_args = "args" in col_config
        
        if has_kwargs and has_args:
            example = SpecValidator._format_example(col_name, method_spec["example"])
            errors.append(
                f"❌ Column '{col_name}': cannot have both 'kwargs' and 'args' simultaneously\n"
                f"   Use only 'kwargs' (recommended):\n{example}"
            )
            return errors
        
        if not has_kwargs and not has_args:
            example = SpecValidator._format_example(col_name, method_spec["example"])
            errors.append(
                f"❌ Column '{col_name}': method '{method}' requires 'kwargs' or 'args'\n"
                f"   Correct example:\n{example}"
            )
            return errors
        
        # Validate kwargs (recommended format)
        if has_kwargs:
            kwargs_errors = SpecValidator._validate_kwargs(
                col_name, method, col_config["kwargs"], method_spec
            )
            errors.extend(kwargs_errors)
        
        # Validate args (legacy format)
        if has_args:
            if not isinstance(col_config["args"], (list, tuple)):
                errors.append(
                    f"❌ Column '{col_name}': 'args' must be list or tuple, got {type(col_config['args']).__name__}\n"
                    f"   Or better yet, use 'kwargs' (recommended format)"
                )
        
        # Validate cols for methods that require it
        if method_spec.get("requires_cols"):
            if "cols" not in col_config:
                example = SpecValidator._format_example(col_name, method_spec["example"])
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' requires 'cols' field\n"
                    f"   Correct example:\n{example}"
                )
            elif not isinstance(col_config["cols"], list):
                errors.append(
                    f"❌ Column '{col_name}': 'cols' must be list, got {type(col_config['cols']).__name__}"
                )
            elif len(col_config["cols"]) == 0:
                errors.append(
                    f"❌ Column '{col_name}': 'cols' cannot be empty"
                )
        
        # Validate transformers
        if "transformers" in col_config:
            transformers_errors = SpecValidator._validate_transformers(col_name, col_config["transformers"])
            errors.extend(transformers_errors)
        
        # Validate PK configuration
        if "pk" in col_config:
            pk_errors = SpecValidator._validate_pk(col_name, col_config["pk"])
            errors.extend(pk_errors)
        
        return errors

    @staticmethod
    def _validate_kwargs(
        col_name: str,
        method: str,
        kwargs: Any,
        method_spec: Dict
    ) -> List[str]:
        """Validates kwargs for a specific method."""
        errors = []
        
        if not isinstance(kwargs, dict):
            errors.append(
                f"❌ Column '{col_name}': 'kwargs' must be dictionary, got {type(kwargs).__name__}"
            )
            return errors
        
        required_params = method_spec["params"]["required"]
        optional_params = method_spec["params"]["optional"]
        
        # Check required parameters
        for param_name, param_type in required_params.items():
            if param_name not in kwargs:
                example = SpecValidator._format_example(col_name, method_spec["example"])
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' requires parameter '{param_name}'\n"
                    f"   Description: {method_spec['description']}\n"
                    f"   Correct example:\n{example}"
                )
                continue
            
            # Validate parameter type
            value = kwargs[param_name]
            if isinstance(param_type, tuple):
                if not isinstance(value, param_type):
                    type_names = " or ".join(t.__name__ for t in param_type)
                    errors.append(
                        f"❌ Column '{col_name}': parameter '{param_name}' must be {type_names}, "
                        f"got {type(value).__name__}"
                    )
            else:
                if not isinstance(value, param_type):
                    errors.append(
                        f"❌ Column '{col_name}': parameter '{param_name}' must be {param_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        # Check unknown parameters
        all_valid_params = set(required_params.keys()) | set(optional_params.keys())
        unknown_params = set(kwargs.keys()) - all_valid_params
        
        if unknown_params:
            valid_params_str = ", ".join(f"'{p}'" for p in sorted(all_valid_params))
            unknown_list = ", ".join(f"'{p}'" for p in unknown_params)
            errors.append(
                f"⚠️  Column '{col_name}': unknown parameters: {unknown_list}\n"
                f"   Valid parameters for '{method}': {valid_params_str}"
            )
        
        return errors

    @staticmethod
    def _validate_transformers(col_name: str, transformers: Any) -> List[str]:
        """Validates transformers."""
        errors = []
        
        if not isinstance(transformers, list):
            errors.append(
                f"❌ Column '{col_name}': 'transformers' must be list, got {type(transformers).__name__}\n"
                f"   Correct example:\n"
                f"   'transformers': [lambda x: x.upper(), lambda x: x.strip()]"
            )
            return errors
        
        for i, transformer in enumerate(transformers):
            if not callable(transformer):
                errors.append(
                    f"❌ Column '{col_name}': transformer[{i}] must be callable (function/lambda), "
                    f"got {type(transformer).__name__}\n"
                    f"   Example: lambda x: x.upper()"
                )
        
        return errors

    @staticmethod
    def _validate_pk(col_name: str, pk_config: Any) -> List[str]:
        """Validates Primary Key configuration."""
        errors = []
        
        if not isinstance(pk_config, dict):
            errors.append(
                f"❌ Column '{col_name}': 'pk' must be dictionary, got {type(pk_config).__name__}\n"
                f"   Correct example:\n"
                f"   'pk': {{'name': 'users', 'datatype': 'VARCHAR(12)', 'checkpoint': ':memory:'}}"
            )
            return errors
        
        required_pk_fields = ["name", "datatype"]
        for field in required_pk_fields:
            if field not in pk_config:
                errors.append(
                    f"❌ Column '{col_name}': 'pk' requires field '{field}'\n"
                    f"   Example: 'pk': {{'name': 'users', 'datatype': 'VARCHAR(12)'}}"
                )
        
        return errors

    @staticmethod
    def _suggest_similar_method(method: str) -> str:
        """Suggests similar methods based on name similarity."""
        suggestions = []
        method_lower = method.lower()
        
        for valid_method in SpecValidator.METHOD_SPECS.keys():
            if method_lower in valid_method or valid_method in method_lower:
                suggestions.append(valid_method)
        
        if not suggestions:
            # Get first 3 methods as generic suggestion
            suggestions = list(SpecValidator.METHOD_SPECS.keys())[:3]
        
        result = []
        for suggested in suggestions[:3]:
            spec = SpecValidator.METHOD_SPECS[suggested]
            result.append(f"   • '{suggested}': {spec['description']}")
        
        return "\n".join(result)

    @staticmethod
    def _format_example(col_name: str, example: Dict) -> str:
        """Formats usage example in a readable way."""
        # Get first item from example
        example_key = list(example.keys())[0]
        example_value = example[example_key]
        
        # Replace key with provided col_name
        lines = [f"   '{col_name}': {{"]
        
        # Add method
        lines.append(f"       'method': '{example_value['method']}',")
        
        # Add cols if exists
        if 'cols' in example_value:
            cols_str = str(example_value['cols']).replace("'", '"')
            lines.append(f"       'cols': {cols_str},")
        
        # Add kwargs
        if 'kwargs' in example_value:
            lines.append(f"       'kwargs': {{")
            for key, value in example_value['kwargs'].items():
                if isinstance(value, str):
                    lines.append(f"           '{key}': '{value}',")
                elif isinstance(value, dict):
                    # Format dict in readable way
                    dict_str = str(value).replace("'", '"')
                    lines.append(f"           '{key}': {dict_str},")
                elif isinstance(value, list):
                    # Format list in readable way
                    list_str = str(value).replace("'", '"')
                    lines.append(f"           '{key}': {list_str},")
                else:
                    lines.append(f"           '{key}': {value},")
            lines.append(f"       }}")
        
        lines.append(f"   }}")
        
        return "\n".join(lines)

    @staticmethod
    def validate_and_raise(spec: Dict[str, Dict[str, Any]]) -> None:
        """
        Validates spec and raises educational exception if there are errors.
        
        Args:
            spec: Specification dictionary
        
        Raises:
            SpecValidationError: If spec contains errors, with detailed messages
        """
        errors = SpecValidator.validate(spec)
        if errors:
            separator = "\n" + "="*80 + "\n"
            error_message = (
                f"\n{'='*80}\n"
                f"SPEC VALIDATION ERROR\n"
                f"{'='*80}\n\n"
                f"Found {len(errors)} error(s) in specification:\n\n" +
                separator.join(errors) +
                f"\n\n{'='*80}\n"
                f"📚 Documentation: https://github.com/marcoaureliomenezes/rand_engine\n"
                f"{'='*80}\n"
            )
            raise SpecValidationError(error_message)

    @staticmethod
    def validate_with_warnings(spec: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validates spec and prints formatted errors if any.
        
        Returns:
            True if spec is valid, False otherwise
        """
        errors = SpecValidator.validate(spec)
        if errors:
            print(f"\n{'='*80}")
            print(f"❌ VALIDATION FAILED - {len(errors)} error(s) found")
            print(f"{'='*80}\n")
            for i, error in enumerate(errors, 1):
                print(f"{i}. {error}\n")
            print(f"{'='*80}\n")
            return False
        
        print("\n✅ Spec validated successfully!\n")
        return True
