"""Catalog-driven validation for DataGenerator RandSpecs."""

import json
import string
from types import MappingProxyType
from typing import Any

from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.method_specs import (
    CORRELATED,
    KEY,
    METHOD_CATALOG,
    NUMPY,
    ORDINARY,
    MethodSpec,
)


class AdvancedValidator:
    """Validate a complete DataGenerator RandSpec through the method catalog."""

    METHOD_SPECS = MappingProxyType(
        {
            name: {
                **method_spec.as_table(),
                "requires_cols": method_spec.requires_cols,
                "expected_cols": method_spec.expected_cols,
            }
            for name, method_spec in METHOD_CATALOG.items()
            if method_spec.kind != ORDINARY
        }
    )

    @classmethod
    def validate(cls, spec: dict[str, dict[str, Any]]) -> list[str]:
        if not isinstance(spec, dict):
            return [
                f"❌ Spec must be a dictionary, got {type(spec).__name__}\n"
                "   Correct example:\n"
                "   spec = {'age': {'method': 'integers', 'kwargs': {'min': 0, 'max': 100}}}"
            ]
        if not spec:
            return [
                "❌ Spec cannot be empty\n"
                "   Minimal example:\n"
                "   spec = {'id': {'method': 'int_zfilled', 'kwargs': {'length': 8}}}"
            ]

        constraint_errors = cls.validate_constraints(spec)
        if constraint_errors:
            return constraint_errors

        errors: list[str] = []
        for col_name, col_config in spec.items():
            errors.extend(cls._validate_column_complete(col_name, col_config))
        return errors

    @classmethod
    def _validate_column_complete(cls, col_name: str, col_config: Any) -> list[str]:
        if not isinstance(col_config, dict):
            return [
                f"❌ Column '{col_name}': configuration must be a dictionary, got {type(col_config).__name__}\n"
                f"   Fix to:\n   '{col_name}': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}"
            ]
        if "method" not in col_config:
            return [
                f"❌ Column '{col_name}': field 'method' is required\n"
                f"   Fix to:\n   '{col_name}': {{'method': 'integers', 'kwargs': {{'min': 0, 'max': 100}}}}"
            ]

        method = col_config["method"]
        if not isinstance(method, str):
            if callable(method):
                return [
                    f"❌ Column '{col_name}': use string identifier instead of callable\n"
                    "   Old format (not recommended): {'method': NPCore.gen_ints, ...}\n"
                    "   New format (correct): {'method': 'integers', ...}"
                ]
            return [
                f"❌ Column '{col_name}': 'method' must be string, got {type(method).__name__}\n"
                f"   Available methods: {', '.join(sorted(METHOD_CATALOG))}"
            ]
        if "args" in col_config:
            return [
                f"❌ Column '{col_name}': 'args' was removed in 0.7.0; "
                "pass parameters by name in 'kwargs'"
            ]

        method_spec = METHOD_CATALOG.get(method)
        if method_spec is None or NUMPY not in method_spec.engines:
            available = ", ".join(f"'{name}'" for name in sorted(METHOD_CATALOG))
            return [
                f"❌ Column '{col_name}': method '{method}' does not exist\n"
                f"   Available methods: {available}"
            ]

        if method_spec.kind == ORDINARY:
            errors = CommonValidator.validate_column(col_name, col_config)
        else:
            errors = cls._validate_catalog_column(col_name, col_config, method_spec)

        if method_spec.kind in (CORRELATED, KEY):
            errors.extend(cls._excluded_modifier_errors(col_name, method, col_config))
        if method == "pk":
            errors.extend(cls._pk_errors(col_name, col_config))
        elif method == "fk":
            errors.extend(cls._fk_errors(col_name, col_config))
        elif method_spec.kind == CORRELATED:
            errors.extend(cls._correlated_errors(col_name, col_config))

        if "transformers" in col_config and method_spec.kind == ORDINARY:
            errors.extend(cls._validate_transformers(col_name, col_config["transformers"]))
        return errors

    @classmethod
    def validate_column(cls, col_name: str, col_config: dict[str, Any]) -> list[str]:
        """Validate one DataGenerator column through the complete intake."""
        return cls._validate_column_complete(col_name, col_config)

    @classmethod
    def _validate_catalog_column(
        cls,
        col_name: str,
        col_config: dict[str, Any],
        method_spec: MethodSpec,
    ) -> list[str]:
        errors = CommonValidator._validate_method_parameters(
            col_name, col_config, method_spec
        )
        errors.extend(cls._cols_errors(col_name, col_config, method_spec))
        return errors

    @classmethod
    def _cols_errors(
        cls,
        col_name: str,
        col_config: dict[str, Any],
        method_spec: MethodSpec,
    ) -> list[str]:
        if not method_spec.requires_cols:
            return []
        if "cols" not in col_config:
            return [
                f"❌ Column '{col_name}': Method '{col_config['method']}' requires 'cols' field\n"
                f"   Example:\n{cls._format_example(method_spec.example)}"
            ]
        cols = col_config["cols"]
        if not isinstance(cols, list):
            return [
                f"❌ Column '{col_name}': 'cols' must be list\n"
                f"   Got: {type(cols).__name__}"
            ]
        if method_spec.expected_cols is not None and len(cols) != method_spec.expected_cols:
            return [
                f"⚠️  Column '{col_name}': Method '{col_config['method']}' expects "
                f"{method_spec.expected_cols} columns\n   Got: {len(cols)} columns"
            ]
        return []

    @staticmethod
    def _excluded_modifier_errors(
        col_name: str,
        method: str,
        col_config: dict[str, Any],
    ) -> list[str]:
        return [
            f"❌ Column '{col_name}': method '{method}' does not support modifier '{modifier}'"
            for modifier in ("anomaly_rate", "null_rate")
            if modifier in col_config
        ]

    @classmethod
    def _correlated_errors(
        cls,
        col_name: str,
        col_config: dict[str, Any],
    ) -> list[str]:
        kwargs = col_config.get("kwargs")
        if not isinstance(kwargs, dict):
            return []
        method = col_config["method"]
        distincts = kwargs.get("distincts")
        if method == "complex_distincts":
            return cls._complex_errors(col_name, kwargs)
        if not isinstance(distincts, dict):
            return []

        errors: list[str] = []
        for category, values in distincts.items():
            if not isinstance(values, list):
                errors.append(
                    f"⚠️  Column '{col_name}': Each 'distincts' pool must be a list\n"
                    f"   Got: {type(values).__name__}"
                )
                continue
            if method == "distincts_map_prop":
                if not values:
                    errors.append(
                        f"❌ Column '{col_name}': method '{method}' parameter 'distincts' must be non-empty"
                    )
                for item in values:
                    if not isinstance(item, (tuple, list)) or len(item) != 2:
                        errors.append(
                            f"⚠️  Column '{col_name}': Each item must be a (value, weight) pair"
                        )
                    elif isinstance(item[1], bool) or not isinstance(item[1], int):
                        errors.append(
                            f"⚠️  Column '{col_name}': Weight must be an integer\n"
                            f"   Got: {type(item[1]).__name__}"
                        )
            elif method == "distincts_multi_map":
                cols = col_config.get("cols")
                if isinstance(cols, list) and len(cols) != len(values) + 1:
                    errors.append(
                        f"❌ Column '{col_name}': category '{category}' has {len(values)} levels, "
                        f"so 'cols' needs {len(values) + 1} names; got {len(cols)}"
                    )
                for level in values:
                    if not isinstance(level, list):
                        errors.append(
                            f"⚠️  Column '{col_name}': Each element must be a list\n"
                            f"   Got: {type(level).__name__}"
                        )
        return errors

    @classmethod
    def _complex_errors(cls, col_name: str, kwargs: dict[str, Any]) -> list[str]:
        pattern = kwargs.get("pattern")
        replacement = kwargs.get("replacement")
        templates = kwargs.get("templates")
        if not isinstance(pattern, str) or not isinstance(replacement, str) or not isinstance(templates, list):
            return []

        errors: list[str] = []
        if pattern.count(replacement) != len(templates):
            errors.append(
                f"⚠️  Column '{col_name}': Pattern has {pattern.count(replacement)} replacement "
                f"occurrences\n   but {len(templates)} templates provided. They must match."
            )
        for index, template in enumerate(templates):
            name = f"{col_name}.templates[{index}]"
            if not isinstance(template, dict):
                errors.append(
                    f"⚠️  Column '{col_name}': Template {index} must be a dictionary\n"
                    f"   Got: {type(template).__name__}"
                )
                continue
            if "method" not in template:
                errors.append(f"⚠️  Column '{col_name}': Template {index} missing 'method' field")
                continue
            if "kwargs" not in template:
                errors.append(f"⚠️  Column '{col_name}': Template {index} missing 'kwargs' field")
                continue
            template_method = template["method"]
            template_spec = METHOD_CATALOG.get(template_method) if isinstance(template_method, str) else None
            if template_spec is None or template_spec.kind != ORDINARY or NUMPY not in template_spec.engines:
                allowed = sorted(
                    method
                    for method, method_spec in METHOD_CATALOG.items()
                    if method_spec.kind == ORDINARY and NUMPY in method_spec.engines
                )
                errors.append(
                    f"❌ Column '{name}': template method '{template_method}' must be one of "
                    f"{', '.join(allowed)}"
                )
                continue
            errors.extend(CommonValidator.validate_column(name, template))
        return errors

    @classmethod
    def _pk_errors(cls, col_name: str, col_config: dict[str, Any]) -> list[str]:
        kwargs = col_config.get("kwargs", {})
        if "transformers" in col_config:
            return [f"❌ Column '{col_name}': 'pk' takes only 'kwargs', never 'args' or 'transformers'"]
        if not isinstance(kwargs, dict):
            return []

        errors: list[str] = []
        style = kwargs.get("style", "sequence")
        if style not in ("sequence", "permuted"):
            errors.append(
                f"❌ Column '{col_name}': pk 'style' is unknown; use 'sequence' or 'permuted'"
            )
        if style == "permuted":
            domain, start = kwargs.get("domain"), kwargs.get("start", 0)
            if not isinstance(domain, int) or isinstance(domain, bool) or not 1 <= domain <= 2**62:
                errors.append(
                    f"❌ Column '{col_name}': pk 'permuted' needs an integer 'domain' in [1, 2**62] (int64 Feistel)"
                )
            elif isinstance(start, int) and not isinstance(start, bool) and not -2**63 <= start <= start + domain - 1 < 2**63:
                errors.append(f"❌ Column '{col_name}': pk start + domain leaves int64")
        foreign = sorted(set(kwargs) & ({"step"} if style == "permuted" else {"domain", "key"}))
        if foreign:
            errors.append(f"❌ Column '{col_name}': pk style {style!r} does not take {foreign}")
        if kwargs.get("step", 1) == 0:
            errors.append(f"❌ Column '{col_name}': pk 'step' must not be 0 (keys would repeat)")
        if "format" in kwargs and not cls._valid_key_format(kwargs["format"]):
            errors.append(
                f"❌ Column '{col_name}': pk 'format' needs exactly one integer replacement field, e.g. 'C-{{:08d}}'"
            )
        return errors

    @staticmethod
    def _valid_key_format(template: Any) -> bool:
        if not isinstance(template, str):
            return False
        try:
            fields = [
                (field, format_spec, conversion)
                for _, field, format_spec, conversion in string.Formatter().parse(template)
                if field is not None
            ]
            valid = (
                len(fields) == 1
                and fields[0][0] in ("", "0")
                and fields[0][2] is None
                and "{" not in fields[0][1]
                and (
                    fields[0][1][-1:]
                    if fields[0][1][-1:].isalpha() or fields[0][1][-1:] == "%"
                    else ""
                )
                in "bdoxXn"
            )
            if valid:
                template.format(0)
            return valid
        except (ValueError, TypeError):
            return False

    @classmethod
    def _fk_errors(cls, col_name: str, col_config: dict[str, Any]) -> list[str]:
        kwargs = col_config.get("kwargs", {})
        if not isinstance(kwargs, dict):
            return []
        parent = kwargs.get("parent")
        size = kwargs.get("parent_size")
        skew = kwargs.get("skew", 0)
        if not isinstance(parent, dict) or parent.get("method") != "pk":
            return [
                f"❌ Column '{col_name}': fk 'parent' must be a pk column spec, "
                "e.g. {'method': 'pk', 'kwargs': {'start': 1}}"
            ]

        foreign = sorted(set(parent) - {"method", "kwargs", "args", "transformers"})
        errors = (
            [f"❌ Column '{col_name}': fk 'parent' takes only 'method' and 'kwargs', not {foreign}"]
            if foreign
            else []
        )
        errors.extend(cls._pk_errors(f"{col_name}.parent", parent))
        if isinstance(size, bool) or (isinstance(size, int) and size < 1):
            errors.append(f"❌ Column '{col_name}': fk 'parent_size' must be an integer >= 1")
        parent_kwargs = parent.get("kwargs")
        domain = parent_kwargs.get("domain") if isinstance(parent_kwargs, dict) else None
        if isinstance(size, int) and not isinstance(size, bool) and isinstance(domain, int) and size > domain:
            errors.append(
                f"❌ Column '{col_name}': fk parent_size {size} exceeds the parent's domain {domain}"
            )
        if (
            isinstance(skew, bool)
            or not isinstance(skew, (int, float))
            or not 0 <= skew < float("inf")
        ):
            errors.append(f"❌ Column '{col_name}': fk 'skew' must be a finite number >= 0 (0 is uniform)")
        return errors

    @staticmethod
    def _format_example(example: Any) -> str:
        return "   " + json.dumps(dict(example), indent=6).replace("\n", "\n   ")

    @classmethod
    def validate_constraints(cls, spec: dict[str, Any]) -> list[str]:
        if "constraints" not in spec:
            return []
        return [
            "❌ 'constraints' is not supported; declare keys as columns:\n"
            + cls._format_example(METHOD_CATALOG["pk"].example)
            + "\n"
            + cls._format_example(METHOD_CATALOG["fk"].example)
        ]

    @staticmethod
    def _validate_transformers(col_name: str, transformers: Any) -> list[str]:
        if not isinstance(transformers, list):
            return [
                f"❌ Column '{col_name}': 'transformers' must be list, got {type(transformers).__name__}\n"
                "   Correct example:\n"
                "   'transformers': [lambda x: x.upper(), lambda x: x.strip()]"
            ]
        return [
            f"❌ Column '{col_name}': transformer[{index}] must be callable (function/lambda), "
            f"got {type(transformer).__name__}\n   Example: lambda x: x.upper()"
            for index, transformer in enumerate(transformers)
            if not callable(transformer)
        ]

    @classmethod
    def validate_and_raise(cls, spec: dict[str, dict[str, Any]]) -> None:
        errors = cls.validate(spec)
        if errors:
            CommonValidator._raise(errors, "DATAGENERATOR")

    @classmethod
    def validate_with_warnings(cls, spec: dict[str, dict[str, Any]]) -> bool:
        errors = cls.validate(spec)
        if not errors:
            print("\n✅ Spec validated successfully!\n")
            return True
        print(f"\n{'=' * 80}\n❌ VALIDATION FAILED - {len(errors)} error(s) found\n{'=' * 80}\n")
        for index, error in enumerate(errors, 1):
            print(f"{index}. {error}\n")
        print(f"{'=' * 80}\n")
        return False
