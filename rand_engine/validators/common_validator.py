"""Catalog-driven validation shared by DataGenerator and SparkGenerator."""

import json
from typing import Any
import warnings

from rand_engine.validators.exceptions import SpecValidationError
from rand_engine.validators.method_specs import (
    COMMON_METHOD_SPECS,
    CORRELATED,
    METHOD_CATALOG,
    MethodSpec,
    ORDINARY,
    SPARK,
    is_declared_scalar,
    matches_type,
    type_name,
)


class CommonValidator:
    """Validate ordinary RandSpec methods and adapt them for Spark."""

    METHOD_SPECS = COMMON_METHOD_SPECS

    @classmethod
    def validate_column(cls, col_name: str, col_config: dict[str, Any]) -> list[str]:
        if not isinstance(col_config, dict):
            return [
                f"❌ Column '{col_name}': Configuration must be a dictionary\n"
                f"   Got: {type(col_config).__name__}"
            ]
        if "method" not in col_config:
            return [f"❌ Column '{col_name}': Missing 'method' field"]

        method = col_config["method"]
        method_spec = METHOD_CATALOG.get(method) if isinstance(method, str) else None
        if method_spec is None or method_spec.kind != ORDINARY:
            return []

        errors = cls._validate_method_parameters(col_name, col_config, method_spec)
        errors.extend(cls._modifier_errors(col_name, col_config))
        return errors

    @classmethod
    def _validate_method_parameters(
        cls,
        col_name: str,
        col_config: dict[str, Any],
        method_spec: MethodSpec,
    ) -> list[str]:
        """Validate one method's named parameters through catalog metadata."""
        method = col_config["method"]
        kwargs = col_config.get("kwargs", {})
        if not isinstance(kwargs, dict):
            return [
                f"❌ Column '{col_name}': 'kwargs' must be dictionary\n"
                f"   Got: {type(kwargs).__name__}"
            ]

        errors: list[str] = []
        invalid_parameters: set[str] = set()
        for parameter, rule in method_spec.required.items():
            if parameter not in kwargs:
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' requires parameter '{parameter}'\n"
                    f"   Expected type: {type_name(rule)}\n"
                    f"   Correct example:\n{cls._format_example(method_spec.example)}"
                )
                invalid_parameters.add(parameter)
            elif not matches_type(kwargs[parameter], rule):
                errors.append(cls._type_error(col_name, parameter, rule, kwargs[parameter]))
                invalid_parameters.add(parameter)

        for parameter, value in kwargs.items():
            rule = method_spec.optional.get(parameter)
            if rule is not None and not matches_type(value, rule):
                errors.append(cls._type_error(col_name, parameter, rule, value))
                invalid_parameters.add(parameter)

        valid_parameters = set(method_spec.required) | set(method_spec.optional)
        unknown_parameters = sorted(set(kwargs) - valid_parameters)
        if unknown_parameters:
            valid = ", ".join(f"'{name}'" for name in sorted(valid_parameters))
            if method_spec.kind == ORDINARY:
                unknown = "', '".join(unknown_parameters)
                errors.append(
                    f"⚠️  Column '{col_name}': unknown parameters: '{unknown}'\n"
                    f"   Valid parameters for '{method}': {valid}"
                )
            else:
                errors.extend(
                    f"⚠️  Column '{col_name}': Unknown parameter '{parameter}' for method '{method}'\n"
                    f"   Valid parameters: {valid}"
                    for parameter in unknown_parameters
                )

        if not invalid_parameters and not unknown_parameters:
            for parameter, message in method_spec.semantic(kwargs):
                errors.append(
                    f"❌ Column '{col_name}': method '{method}' parameter '{parameter}' {message}"
                )

        return errors

    @staticmethod
    def _type_error(col_name: str, parameter: str, rule: Any, value: Any) -> str:
        return (
            f"⚠️  Column '{col_name}': parameter '{parameter}' must be {type_name(rule)}\n"
            f"   Got: {type(value).__name__}"
        )

    @staticmethod
    def _modifier_errors(col_name: str, col_config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for modifier in ("anomaly_rate", "null_rate"):
            if modifier not in col_config:
                continue
            rate = col_config[modifier]
            if isinstance(rate, bool) or not isinstance(rate, (int, float)):
                errors.append(f"❌ Column '{col_name}': '{modifier}' must be a real number between 0 and 1")
            elif not 0 <= rate <= 1:
                errors.append(f"❌ Column '{col_name}': '{modifier}' must be between 0 and 1")

        anomaly_rate = col_config.get("anomaly_rate")
        if isinstance(anomaly_rate, (int, float)) and not isinstance(anomaly_rate, bool) and anomaly_rate > 0:
            values = col_config.get("anomaly_values")
            if not isinstance(values, list) or not values:
                errors.append(f"❌ Column '{col_name}': positive 'anomaly_rate' requires non-empty 'anomaly_values'")
            elif any(not is_declared_scalar(value) for value in values):
                errors.append(f"❌ Column '{col_name}': 'anomaly_values' must contain only scalar values")
        return errors

    @staticmethod
    def _format_example(example: Any) -> str:
        return "   " + json.dumps(dict(example), indent=6).replace("\n", "\n   ")

    @classmethod
    def validate_spark_spec(cls, spec: dict[str, dict[str, Any]]) -> list[str]:
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

        errors: list[str] = []
        for col_name, col_config in spec.items():
            errors.extend(cls._validate_spark_column(col_name, col_config))
        return errors

    @classmethod
    def _validate_spark_column(cls, col_name: str, col_config: Any) -> list[str]:
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
            return [
                f"❌ Column '{col_name}': 'method' must be string, got {type(method).__name__}\n"
                f"   Available methods: {', '.join(sorted(METHOD_CATALOG))}"
            ]
        if "args" in col_config:
            return [
                f"❌ Column '{col_name}': SparkGenerator does not support 'args'\n"
                "   Use 'kwargs' (recommended)"
            ]

        method_spec = METHOD_CATALOG.get(method)
        if method_spec is None:
            available = ", ".join(f"'{name}'" for name in sorted(cls.METHOD_SPECS))
            return [
                f"❌ Column '{col_name}': method '{method}' does not exist\n"
                f"   Available methods: {available}"
            ]

        modifiers = [name for name in ("anomaly_rate", "null_rate") if name in col_config]
        if modifiers:
            names = "', '".join(modifiers)
            return [
                f"❌ Column '{col_name}': modifier '{names}' is NumPy engine only\n"
                "   Use DataGenerator for specs with modifiers"
            ]

        if method_spec.kind == CORRELATED:
            warnings.warn(
                f"⚠️  Column '{col_name}': method '{method}' is a dummy in SparkGenerator (returns NULL)\n"
                "   This method is only fully implemented in DataGenerator\n"
                f"   Available SparkGenerator methods: {', '.join(sorted(cls.METHOD_SPECS))}"
            )
            return []
        if SPARK not in method_spec.engines:
            return [
                f"❌ Column '{col_name}': method '{method}' is NumPy engine only in 0.7.0\n"
                "   Use DataGenerator for this method"
            ]

        kwargs = col_config.get("kwargs", {})
        if method == "integers" and isinstance(kwargs, dict) and kwargs.get("int_type") == "uint64":
            return [f"❌ Column '{col_name}': 'uint64' is not representable by the Spark signed integer carrier"]
        return cls.validate_column(col_name, col_config)

    @classmethod
    def validate_spark_and_raise(cls, spec: dict[str, dict[str, Any]]) -> None:
        errors = cls.validate_spark_spec(spec)
        if errors:
            cls._raise(errors, "SPARKGENERATOR")

    @classmethod
    def validate_spark_with_warnings(cls, spec: dict[str, dict[str, Any]]) -> bool:
        errors = cls.validate_spark_spec(spec)
        if not errors:
            print("\n✅ Spark spec validated successfully!\n")
            return True
        print(f"\n{'=' * 80}\n❌ SPARK VALIDATION FAILED - {len(errors)} error(s) found\n{'=' * 80}\n")
        for index, error in enumerate(errors, 1):
            print(f"{index}. {error}\n")
        print(f"{'=' * 80}\n")
        return False

    @staticmethod
    def _raise(errors: list[str], engine: str) -> None:
        separator = "\n" + "=" * 80 + "\n"
        message = (
            f"\n{'=' * 80}\n{engine} SPEC VALIDATION ERROR\n{'=' * 80}\n\n"
            f"Found {len(errors)} error(s) in specification:\n\n"
            + separator.join(errors)
            + f"\n\n{'=' * 80}\n"
            "📚 Documentation: https://github.com/marcoaureliomenezes/rand_engine\n"
            f"{'=' * 80}\n"
        )
        raise SpecValidationError(message)
