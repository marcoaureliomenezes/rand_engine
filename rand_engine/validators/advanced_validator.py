"""
Advanced Specification Validator for Rand Engine.

This module provides validation logic for advanced methods that are specific to
DataGenerator (PyCore). These methods are NOT available in SparkGenerator.

Methods validated here:
- distincts_map: Correlated pairs (category, value) - generates 2 columns
- distincts_multi_map: Cartesian combinations - generates N columns
- distincts_map_prop: Correlated pairs with weights - generates 2 columns
- complex_distincts: Complex string patterns (IPs, URLs, etc.)
- distincts_external: Values from external DuckDB tables

NOTE: SparkGenerator has dummy implementations of these methods that return NULL values
for API compatibility only.
"""

from typing import Dict, List, Any


class AdvancedValidator:
    """
    Validation logic for advanced methods specific to DataGenerator (PyCore).
    """
    
    # Complete mapping of advanced methods with their signatures and examples
    METHOD_SPECS = {
        "distincts_map": {
            "description": "Generates correlated pairs (category, value) - 2 columns",
            "params": {
                "required": {"distincts": dict},  # {category: [values], ...}
                "optional": {}
            },
            "requires_cols": True,
            "expected_cols": 2,
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
            "expected_cols": 2,
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
            "expected_cols": "N+1",  # Category + N value columns
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
                            {"method": "distincts", "kwargs": {"distincts": ["192", "10"]}},
                            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                            {"method": "integers", "kwargs": {"min": 0, "max": 255}},
                            {"method": "integers", "kwargs": {"min": 1, "max": 254}}
                        ]
                    }
                }
            }
        },
        "distincts_external": {
            "description": "Selects random values from an external database table (DuckDB)",
            "params": {
                "required": {"name": str, "fields": list, "watermark": str},
                "optional": {"db_path": str}  # Default: ":memory:"
            },
            "example": {
                "category_id": {
                    "method": "distincts_external",
                    "kwargs": {
                        "name": "categories",
                        "fields": ["category_id"],
                        "watermark": "1 DAY",
                        "db_path": "warehouse.duckdb"
                    }
                }
            }
        }
    }
    
    @classmethod
    def validate_column(cls, col_name: str, col_config: Dict[str, Any]) -> List[str]:
        """
        Validates a single column configuration for advanced methods.
        
        Args:
            col_name: Name of the column
            col_config: Dictionary with 'method', 'kwargs', and optionally 'cols'
            
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
        
        # 3. Check if method is in advanced methods
        if method not in cls.METHOD_SPECS:
            # Not an advanced method - will be handled by common validator
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
        
        # 5. Check 'cols' requirement for multi-column methods
        if spec.get("requires_cols", False):
            if "cols" not in col_config:
                errors.append(
                    f"❌ Column '{col_name}': Method '{method}' requires 'cols' field\n"
                    f"   Example:\n{cls._format_example(spec['example'])}"
                )
            else:
                cols = col_config["cols"]
                if not isinstance(cols, list):
                    errors.append(
                        f"❌ Column '{col_name}': 'cols' must be list\n"
                        f"   Got: {type(cols).__name__}"
                    )
                else:
                    expected_cols = spec.get("expected_cols")
                    if expected_cols and expected_cols != "N+1":
                        if len(cols) != expected_cols:
                            errors.append(
                                f"⚠️  Column '{col_name}': Method '{method}' expects {expected_cols} columns\n"
                                f"   Got: {len(cols)} columns {cols}"
                            )
        
        # 6. Validate required parameters
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
        
        # 7. Validate optional parameters and check for unknown parameters
        optional_params = spec["params"]["optional"]
        all_valid_params = set(required_params.keys()) | set(optional_params.keys())
        
        for param, value in kwargs.items():
            if param not in all_valid_params:
                errors.append(
                    f"⚠️  Column '{col_name}': Unknown parameter '{param}' for method '{method}'\n"
                    f"   Valid parameters: {', '.join(all_valid_params)}"
                )
            elif param in optional_params:
                # Type validation for optional params
                param_type = optional_params[param]
                if not cls._check_type(value, param_type):
                    errors.append(
                        f"⚠️  Column '{col_name}': Parameter '{param}' has wrong type\n"
                        f"   Expected: {param_type}, Got: {type(value).__name__}"
                    )
        
        # 8. Special validation for distincts_map
        if method == "distincts_map" and "distincts" in kwargs:
            distincts_dict = kwargs["distincts"]
            if not isinstance(distincts_dict, dict):
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' must be a dictionary\n"
                    f"   Got: {type(distincts_dict).__name__}"
                )
            else:
                # Validate structure: {category: [values], ...}
                for category, values in distincts_dict.items():
                    if not isinstance(values, list):
                        errors.append(
                            f"⚠️  Column '{col_name}': Values for category '{category}' must be a list\n"
                            f"   Got: {type(values).__name__}"
                        )
        
        # 9. Special validation for distincts_map_prop
        if method == "distincts_map_prop" and "distincts" in kwargs:
            distincts_dict = kwargs["distincts"]
            if not isinstance(distincts_dict, dict):
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' must be a dictionary\n"
                    f"   Got: {type(distincts_dict).__name__}"
                )
            else:
                # Validate structure: {category: [(value, weight), ...], ...}
                for category, value_weight_pairs in distincts_dict.items():
                    if not isinstance(value_weight_pairs, list):
                        errors.append(
                            f"⚠️  Column '{col_name}': Value-weight pairs for '{category}' must be a list\n"
                            f"   Got: {type(value_weight_pairs).__name__}"
                        )
                    else:
                        for item in value_weight_pairs:
                            if not isinstance(item, (tuple, list)) or len(item) != 2:
                                errors.append(
                                    f"⚠️  Column '{col_name}': Each item must be a (value, weight) pair\n"
                                    f"   Got: {item}"
                                )
                            elif not isinstance(item[1], int):
                                errors.append(
                                    f"⚠️  Column '{col_name}': Weight must be an integer\n"
                                    f"   Got: {type(item[1]).__name__} ({item[1]})"
                                )
        
        # 10. Special validation for distincts_multi_map
        if method == "distincts_multi_map" and "distincts" in kwargs:
            distincts_dict = kwargs["distincts"]
            if not isinstance(distincts_dict, dict):
                errors.append(
                    f"⚠️  Column '{col_name}': 'distincts' must be a dictionary\n"
                    f"   Got: {type(distincts_dict).__name__}"
                )
            else:
                # Validate structure: {category: [[list1], [list2], ...], ...}
                for category, list_of_lists in distincts_dict.items():
                    if not isinstance(list_of_lists, list):
                        errors.append(
                            f"⚠️  Column '{col_name}': Values for '{category}' must be a list of lists\n"
                            f"   Got: {type(list_of_lists).__name__}"
                        )
                    else:
                        for sublist in list_of_lists:
                            if not isinstance(sublist, list):
                                errors.append(
                                    f"⚠️  Column '{col_name}': Each element must be a list\n"
                                    f"   Got: {type(sublist).__name__}"
                                )
        
        # 11. Special validation for complex_distincts
        if method == "complex_distincts":
            pattern = kwargs.get("pattern", "")
            replacement = kwargs.get("replacement", "")
            templates = kwargs.get("templates", [])
            
            if pattern and replacement and templates:
                count_replacements = pattern.count(replacement)
                if count_replacements != len(templates):
                    errors.append(
                        f"⚠️  Column '{col_name}': Pattern has {count_replacements} '{replacement}' occurrences\n"
                        f"   but {len(templates)} templates provided. They must match."
                    )
                
                # Validate each template is a proper method spec
                for idx, template in enumerate(templates):
                    if not isinstance(template, dict):
                        errors.append(
                            f"⚠️  Column '{col_name}': Template {idx} must be a dictionary\n"
                            f"   Got: {type(template).__name__}"
                        )
                    elif "method" not in template:
                        errors.append(
                            f"⚠️  Column '{col_name}': Template {idx} missing 'method' field"
                        )
                    elif "kwargs" not in template:
                        errors.append(
                            f"⚠️  Column '{col_name}': Template {idx} missing 'kwargs' field"
                        )
        
        # 12. Special validation for distincts_external
        if method == "distincts_external":
            if "fields" in kwargs:
                fields = kwargs["fields"]
                if not isinstance(fields, list):
                    errors.append(
                        f"⚠️  Column '{col_name}': 'fields' must be a list\n"
                        f"   Got: {type(fields).__name__}"
                    )
                elif len(fields) == 0:
                    errors.append(
                        f"⚠️  Column '{col_name}': 'fields' list cannot be empty"
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
