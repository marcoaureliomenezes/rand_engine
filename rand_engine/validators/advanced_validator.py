"""
Advanced Specification Validator for Rand Engine.

This module provides validation logic for advanced methods that are specific to
DataGenerator (PyCore). These methods are NOT available in SparkGenerator.

Methods validated here:
- distincts_map: Correlated pairs (category, value) - generates 2 columns
- distincts_multi_map: Cartesian combinations - generates N columns
- distincts_map_prop: Correlated pairs with weights - generates 2 columns
- complex_distincts: Complex string patterns (IPs, URLs, etc.)

NOTE: SparkGenerator has dummy implementations of these methods that return NULL values
for API compatibility only.
"""

import string
from typing import Dict, List, Any
from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.exceptions import SpecValidationError


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
        "pk": {
            "description": "Primary key: start + row_index * step, or start + a bijection of the row index over domain, unique by construction",
            "params": {
                "required": {},
                "optional": {"style": str, "start": int, "step": int, "domain": int, "key": int, "format": str}
            },
            "example": {
                "id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}
            }
        },
        "fk": {
            "description": "Foreign key: a parent pk value picked from the seed and the row index; skew > 0 is Zipf over scattered parents",
            "params": {
                "required": {"parent": dict, "parent_size": int},
                "optional": {"skew": (int, float)}
            },
            "example": {
                "parent_id": {"method": "fk", "kwargs": {
                    "parent": {"method": "pk", "kwargs": {"start": 1}},
                    "parent_size": 1000
                }}
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
        
        return errors
    
    @classmethod
    def _pk_errors(cls, col_name: str, col_config: Dict[str, Any]) -> List[str]:
        """Refuses a pk the FK side cannot rebuild from the spec alone, or one that is not unique."""
        kw = col_config.get("kwargs", {})
        if "args" in col_config or "transformers" in col_config:
            return [f"❌ Column '{col_name}': 'pk' takes only 'kwargs', never 'args' or 'transformers'"]
        if not isinstance(kw, dict):
            return []
        errors = []
        style = kw.get("style", "sequence")
        if style not in ("sequence", "permuted"):
            errors.append(f"❌ Column '{col_name}': pk style {style!r} is unknown; use 'sequence' or 'permuted'")
        if style == "permuted":
            domain, start = kw.get("domain"), kw.get("start", 0)
            if not isinstance(domain, int) or not 1 <= domain <= 2**62:
                errors.append(f"❌ Column '{col_name}': pk 'permuted' needs an integer 'domain' in [1, 2**62] (int64 Feistel)")
            elif isinstance(start, int) and not -2**63 <= start <= start + domain - 1 < 2**63:
                errors.append(f"❌ Column '{col_name}': pk start + domain leaves int64")
        foreign = sorted(set(kw) & ({"step"} if style == "permuted" else {"domain", "key"}))
        if foreign:
            errors.append(f"❌ Column '{col_name}': pk style {style!r} does not take {foreign}")
        if kw.get("step", 1) == 0:
            errors.append(f"❌ Column '{col_name}': pk 'step' must not be 0 (keys would repeat)")
        if "format" in kw:
            try:
                fields = [(f, spec, conv) for _, f, spec, conv in string.Formatter().parse(kw["format"]) if f is not None]
                ok = (len(fields) == 1 and fields[0][0] in ("", "0") and fields[0][2] is None
                      and "{" not in fields[0][1]
                      and (fields[0][1][-1:] if fields[0][1][-1:].isalpha() or fields[0][1][-1:] == "%" else "") in "bdoxXn")
                if ok:
                    kw["format"].format(0)
            except (ValueError, TypeError):
                ok = False
            if not ok:
                errors.append(f"❌ Column '{col_name}': pk 'format' needs exactly one integer replacement field, e.g. 'C-{{:08d}}'")
        return errors

    @classmethod
    def _fk_errors(cls, col_name: str, col_config: Dict[str, Any]) -> List[str]:
        """Refuses an fk whose parent pk cannot be rebuilt, or whose parent_size or skew is out of range."""
        if "args" in col_config:
            return [f"❌ Column '{col_name}': 'fk' takes only 'kwargs', never 'args'"]
        kw = col_config.get("kwargs", {})
        if not isinstance(kw, dict):
            return []
        parent, size, skew = kw.get("parent"), kw.get("parent_size"), kw.get("skew", 0)
        if not isinstance(parent, dict) or parent.get("method") != "pk":
            return [f"❌ Column '{col_name}': fk 'parent' must be a pk column spec, e.g. {{'method': 'pk', 'kwargs': {{'start': 1}}}}"]
        foreign = sorted(set(parent) - {"method", "kwargs", "args", "transformers"})
        errors = [f"❌ Column '{col_name}': fk 'parent' takes only 'method' and 'kwargs', not {foreign}"] if foreign else []
        errors += cls._pk_errors(f"{col_name}.parent", parent)
        if isinstance(size, bool) or (isinstance(size, int) and size < 1):
            errors.append(f"❌ Column '{col_name}': fk 'parent_size' must be an integer >= 1")
        domain = parent.get("kwargs", {}).get("domain") if isinstance(parent.get("kwargs"), dict) else None
        if isinstance(size, int) and isinstance(domain, int) and size > domain:
            errors.append(f"❌ Column '{col_name}': fk parent_size {size} exceeds the parent's domain {domain}")
        if isinstance(skew, bool) or not isinstance(skew, (int, float)) or not 0 <= skew < float("inf"):
            errors.append(f"❌ Column '{col_name}': fk 'skew' must be a finite number >= 0 (0 is uniform)")
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
    # HIGH-LEVEL VALIDATION METHODS (for DataGenerator)
    # ========================================================================
    
    @classmethod
    def validate(cls, spec: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Validates a complete DataGenerator specification.
        
        Combines validation from CommonValidator (common methods) and 
        AdvancedValidator (advanced methods); a `constraints` key is refused.
        
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
        
        constraints_errors = cls.validate_constraints(spec)
        if constraints_errors:
            return constraints_errors
        
        for col_name, col_config in spec.items():
            errors.extend(cls._validate_column_complete(col_name, col_config))
        
        return errors
    
    @classmethod
    def _validate_column_complete(cls, col_name: str, col_config: Any) -> List[str]:
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
                    f"   Available methods: {', '.join(sorted(list(CommonValidator.METHOD_SPECS.keys()) + list(cls.METHOD_SPECS.keys())))}"
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
        
        key_errors = {"pk": cls._pk_errors, "fk": cls._fk_errors}.get(method)
        if key_errors:
            errors.extend(key_errors(col_name, col_config))

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
        
        # Try CommonValidator first
        common_errors = CommonValidator.validate_column(col_name, col_config)
        if common_errors:
            errors.extend(common_errors)
        
        # Try AdvancedValidator if method wasn't found in common
        advanced_errors = cls.validate_column(col_name, col_config)
        if advanced_errors:
            errors.extend(advanced_errors)
        
        # If neither validator handled it, it's an unknown method
        if (not common_errors and not advanced_errors and 
            method not in CommonValidator.METHOD_SPECS and 
            method not in cls.METHOD_SPECS):
            available_methods = ", ".join(f"'{m}'" for m in sorted(list(CommonValidator.METHOD_SPECS.keys()) + list(cls.METHOD_SPECS.keys())))
            errors.append(
                f"❌ Column '{col_name}': method '{method}' does not exist\n"
                f"   Available methods: {available_methods}"
            )
        
        # Validate transformers (optional feature)
        if "transformers" in col_config:
            transformers_errors = cls._validate_transformers(col_name, col_config["transformers"])
            errors.extend(transformers_errors)
        
        return errors
    
    @classmethod
    def validate_constraints(cls, spec: Dict[str, Any]) -> List[str]:
        """Refuses a `constraints` key: relations are stateless `pk`/`fk` columns."""
        if "constraints" not in spec:
            return []
        return [
            "❌ 'constraints' is not supported; declare keys as columns:\n"
            + cls._format_example(cls.METHOD_SPECS["pk"]["example"]) + "\n"
            + cls._format_example(cls.METHOD_SPECS["fk"]["example"])
        ]
    
    @classmethod
    def _validate_transformers(cls, col_name: str, transformers: Any) -> List[str]:
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
    
    @classmethod
    def validate_and_raise(cls, spec: Dict[str, Dict[str, Any]]) -> None:
        """
        Validates spec and raises educational exception if there are errors.
        
        Use this for DataGenerator specs that require validation.
        
        Args:
            spec: Specification dictionary
        
        Raises:
            SpecValidationError: If spec contains errors, with detailed messages
        """
        errors = cls.validate(spec)
        if errors:
            separator = "\n" + "="*80 + "\n"
            error_message = (
                f"\n{'='*80}\n"
                f"DATAGENERATOR SPEC VALIDATION ERROR\n"
                f"{'='*80}\n\n"
                f"Found {len(errors)} error(s) in specification:\n\n" +
                separator.join(errors) +
                f"\n\n{'='*80}\n"
                f"📚 Documentation: https://github.com/marcoaureliomenezes/rand_engine\n"
                f"{'='*80}\n"
            )
            raise SpecValidationError(error_message)

    @classmethod
    def validate_with_warnings(cls, spec: Dict[str, Dict[str, Any]]) -> bool:
        """
        Validates spec and prints formatted errors if any.
        
        Returns:
            True if spec is valid, False otherwise
        """
        errors = cls.validate(spec)
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
