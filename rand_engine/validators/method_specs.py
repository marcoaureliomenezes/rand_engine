"""Canonical RandSpec method metadata and typed semantic validators."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import re
import sys
from types import MappingProxyType
from typing import Any, Callable, Mapping

import pyarrow as pa

from rand_engine.core._np_core import DATE_DIRECTIVES, float_lattice_bounds, poisson_lam_supported


TypeRule = type | tuple[type, ...]
SemanticIssue = tuple[str, str]
SemanticValidator = Callable[[Mapping[str, Any]], tuple[SemanticIssue, ...]]
ArrowTypes = Callable[[Mapping[str, Any]], tuple[pa.DataType, ...]]

NUMPY = "numpy"
SPARK = "spark"
ORDINARY = "ordinary"
CORRELATED = "correlated"
KEY = "key"

INTEGER_TYPES = (
    "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"
)


@dataclass(frozen=True)
class MethodSpec:
    required: Mapping[str, TypeRule]
    optional: Mapping[str, TypeRule]
    defaults: Mapping[str, Any]
    engines: frozenset[str]
    kind: str
    semantic: SemanticValidator
    arrow_types: ArrowTypes
    example: Mapping[str, Any]
    requires_cols: bool = False
    expected_cols: int | None = None

    def as_table(self) -> dict[str, Any]:
        """Expose the parameter/example shape consumed by current callers."""
        return {
            "params": {
                "required": dict(self.required),
                "optional": dict(self.optional),
            },
            "example": dict(self.example),
        }


def _no_semantics(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    return ()


def _fixed_arrow_types(*types: pa.DataType) -> ArrowTypes:
    return lambda _kwargs: types


def _array_type(values: list[Any]) -> pa.DataType:
    return pa.array(values, from_pandas=True).type


def _integer_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    int_types = {
        "int8": pa.int8(),
        "int16": pa.int16(),
        "int32": pa.int32(),
        "int64": pa.int64(),
        "uint8": pa.uint8(),
        "uint16": pa.uint16(),
        "uint32": pa.uint32(),
        "uint64": pa.uint64(),
    }
    return (int_types[kwargs.get("int_type", "int32")],)


def _constant_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    value = kwargs["value"]
    return (pa.null() if value is None else pa.scalar(value).type,)


def _distinct_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    return (_array_type(kwargs["distincts"]),)


def _weighted_distinct_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    return (_array_type(list(kwargs["distincts"])),)


def _mapped_arrow_types(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    distincts = kwargs["distincts"]
    values = [value for pool in distincts.values() for value in pool]
    return _array_type(list(distincts)), _array_type(values)


def _weighted_mapped_arrow_types(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    distincts = kwargs["distincts"]
    values = [item[0] for pool in distincts.values() for item in pool]
    return _array_type(list(distincts)), _array_type(values)


def _multi_mapped_arrow_types(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    distincts = kwargs["distincts"]
    pools = list(distincts.values())
    level_types = tuple(
        _array_type([value for levels in pools for value in levels[index]])
        for index in range(len(pools[0]))
    )
    return (_array_type(list(distincts)), *level_types)


def _pk_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    return (pa.string() if kwargs.get("format") is not None else pa.int64(),)


def _fk_arrow_type(kwargs: Mapping[str, Any]) -> tuple[pa.DataType, ...]:
    return _pk_arrow_type(kwargs["parent"].get("kwargs", {}))


def _positive_decimals(kwargs: Mapping[str, Any]) -> list[SemanticIssue]:
    decimals = kwargs.get("decimals")
    if decimals is not None and decimals < 0:
        return [("decimals", "must be a non-negative integer")]
    return []


def _integers(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    issues: list[SemanticIssue] = []
    if kwargs.get("int_type") not in (None, *INTEGER_TYPES):
        issues.append(("int_type", f"must be one of {list(INTEGER_TYPES)}"))
    if kwargs["min"] > kwargs["max"]:
        issues.append(("min/max", "minimum must be less than or equal to maximum"))
    return tuple(issues)


def _normal(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    std = kwargs.get("std", 1.0)
    if std < 0:
        return (("std", "must be greater than or equal to 0"),)
    return ()


def _floats(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    try:
        float_lattice_bounds(
            kwargs["min"], kwargs["max"], kwargs.get("decimals", 2)
        )
    except ValueError as error:
        return (("min/max", str(error)),)
    return ()


def _is_finite_float_domain(value: int | float) -> bool:
    return -sys.float_info.max <= value <= sys.float_info.max


def is_declared_scalar(value: Any) -> bool:
    scalar_types = (bool, int, float, str, bytes, date, datetime, Decimal)
    return not callable(value) and (value is None or isinstance(value, scalar_types))


def _probability(name: str, value: Any) -> SemanticIssue | None:
    if not 0 <= value <= 1:
        return (name, "must be between 0 and 1")
    return None


def _booleans(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    issue = _probability("true_prob", kwargs.get("true_prob", 0.5))
    return (issue,) if issue else ()


def _distincts(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    if not kwargs.get("distincts"):
        return (("distincts", "must be non-empty"),)
    return ()


def _distincts_prop(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    values = kwargs.get("distincts", {})
    issues: list[SemanticIssue] = []
    if not values:
        issues.append(("distincts", "must be non-empty"))
    for weight in values.values():
        if isinstance(weight, bool) or not isinstance(weight, int):
            issues.append(("distincts", "every weight must be an integer"))
    return tuple(issues)


def _dates(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    date_format = kwargs.get("date_format")
    if date_format is None:
        return ()
    unsupported = sorted(set(re.findall(r"%.?", date_format)) - set(DATE_DIRECTIVES))
    if unsupported:
        return (("date_format", f"contains unsupported directives; supported: {' '.join(DATE_DIRECTIVES)}"),)
    return ()


def _exponential(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    issues = _positive_decimals(kwargs)
    scale = kwargs.get("scale", 1.0)
    if not _is_finite_float_domain(scale) or scale <= 0:
        issues.append(("scale", "must be finite and greater than 0"))
    return tuple(issues)


def _lognormal(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    issues = _positive_decimals(kwargs)
    mean = kwargs.get("mean", 0.0)
    std = kwargs.get("std", 1.0)
    if not _is_finite_float_domain(mean):
        issues.append(("mean", "must be finite"))
    if not _is_finite_float_domain(std) or std < 0:
        issues.append(("std", "must be finite and greater than or equal to 0"))
    return tuple(issues)


def _poisson(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    lam = kwargs.get("lam", 1.0)
    if not _is_finite_float_domain(lam) or lam < 0:
        return (("lam", "must be finite and greater than or equal to 0"),)
    if not poisson_lam_supported(lam):
        return (("lam", "is outside NumPy's supported int64 result domain"),)
    return ()


def _zipf(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    a = kwargs.get("a", 2.0)
    if not _is_finite_float_domain(a) or a <= 1:
        return (("a", "must be finite and greater than 1"),)
    return ()


def _constant(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    value = kwargs.get("value")
    if not is_declared_scalar(value):
        return (("value", "must be an immutable scalar"),)
    return ()


def _mapped_values(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    pools = kwargs.get("distincts", {})
    issues = [
        ("distincts", "every pool must be non-empty")
        for values in pools.values()
        if not values
    ]
    return tuple(issues)


def _multi_mapped_values(kwargs: Mapping[str, Any]) -> tuple[SemanticIssue, ...]:
    pools = kwargs.get("distincts", {})
    if not pools:
        return (("distincts", "domain must be non-empty"),)
    issues = [
        ("distincts", "every level must be non-empty")
        for levels in pools.values()
        if isinstance(levels, list) and any(not level for level in levels)
    ]
    return tuple(issues)


def _spec(
    *,
    required: Mapping[str, TypeRule] | None = None,
    optional: Mapping[str, TypeRule] | None = None,
    defaults: Mapping[str, Any] | None = None,
    engines: tuple[str, ...] = (NUMPY, SPARK),
    kind: str = ORDINARY,
    semantic: SemanticValidator = _no_semantics,
    arrow_types: ArrowTypes,
    example: Mapping[str, Any],
    requires_cols: bool = False,
    expected_cols: int | None = None,
) -> MethodSpec:
    return MethodSpec(
        required=MappingProxyType(dict(required or {})),
        optional=MappingProxyType(dict(optional or {})),
        defaults=MappingProxyType(dict(defaults or {})),
        engines=frozenset(engines),
        kind=kind,
        semantic=semantic,
        arrow_types=arrow_types,
        example=MappingProxyType(dict(example)),
        requires_cols=requires_cols,
        expected_cols=expected_cols,
    )


METHOD_CATALOG: Mapping[str, MethodSpec] = MappingProxyType(
    {
        "integers": _spec(
            required={"min": int, "max": int},
            optional={"int_type": str},
            defaults={"int_type": "int64"},
            semantic=_integers,
            arrow_types=_integer_arrow_type,
            example={
                "method": "integers",
                "kwargs": {"min": 18, "max": 65, "int_type": "int32"},
            },
        ),
        "int_zfilled": _spec(
            required={"length": int},
            arrow_types=_fixed_arrow_types(pa.string()),
            example={"method": "int_zfilled", "kwargs": {"length": 8}},
        ),
        "floats": _spec(
            required={"min": (int, float), "max": (int, float)},
            optional={"decimals": int},
            defaults={"decimals": 2},
            semantic=_floats,
            arrow_types=_fixed_arrow_types(pa.float64()),
            example={
                "method": "floats",
                "kwargs": {"min": 0, "max": 1000, "decimals": 2},
            },
        ),
        "floats_normal": _spec(
            required={"mean": (int, float), "std": (int, float)},
            optional={"decimals": int},
            defaults={"decimals": 2},
            semantic=_normal,
            arrow_types=_fixed_arrow_types(pa.float64()),
            example={
                "method": "floats_normal",
                "kwargs": {"mean": 170, "std": 10, "decimals": 2},
            },
        ),
        "booleans": _spec(
            optional={"true_prob": (int, float)},
            defaults={"true_prob": 0.5},
            semantic=_booleans,
            arrow_types=_fixed_arrow_types(pa.bool_()),
            example={"method": "booleans", "kwargs": {"true_prob": 0.7}},
        ),
        "distincts": _spec(
            required={"distincts": list},
            semantic=_distincts,
            arrow_types=_distinct_arrow_type,
            example={
                "method": "distincts",
                "kwargs": {"distincts": ["free", "premium"]},
            },
        ),
        "distincts_prop": _spec(
            required={"distincts": dict},
            semantic=_distincts_prop,
            arrow_types=_weighted_distinct_arrow_type,
            example={
                "method": "distincts_prop",
                "kwargs": {"distincts": {"mobile": 70, "desktop": 30}},
            },
        ),
        "unix_timestamps": _spec(
            required={"start": str, "end": str},
            optional={"date_format": str},
            defaults={"date_format": "%Y-%m-%d"},
            arrow_types=_fixed_arrow_types(pa.int64()),
            example={
                "method": "unix_timestamps",
                "kwargs": {
                    "start": "1970-01-01",
                    "end": "2023-01-01",
                    "date_format": "%Y-%m-%d",
                },
            },
        ),
        "dates": _spec(
            required={"start": str, "end": str},
            optional={"date_format": str},
            defaults={"date_format": "%Y-%m-%d"},
            semantic=_dates,
            arrow_types=_fixed_arrow_types(pa.string()),
            example={
                "method": "dates",
                "kwargs": {
                    "start": "1970-01-01",
                    "end": "2023-01-01",
                    "date_format": "%Y-%m-%d",
                },
            },
        ),
        "uuid4": _spec(
            arrow_types=_fixed_arrow_types(pa.string()),
            example={"method": "uuid4", "kwargs": {}},
        ),
        "exponential": _spec(
            optional={"scale": (int, float), "decimals": int},
            defaults={"scale": 1.0, "decimals": 2},
            engines=(NUMPY,),
            semantic=_exponential,
            arrow_types=_fixed_arrow_types(pa.float64()),
            example={"method": "exponential", "kwargs": {}},
        ),
        "lognormal": _spec(
            optional={
                "mean": (int, float),
                "std": (int, float),
                "decimals": int,
            },
            defaults={"mean": 0.0, "std": 1.0, "decimals": 2},
            engines=(NUMPY,),
            semantic=_lognormal,
            arrow_types=_fixed_arrow_types(pa.float64()),
            example={"method": "lognormal", "kwargs": {}},
        ),
        "poisson": _spec(
            optional={"lam": (int, float)},
            defaults={"lam": 1.0},
            engines=(NUMPY,),
            semantic=_poisson,
            arrow_types=_fixed_arrow_types(pa.int64()),
            example={"method": "poisson", "kwargs": {}},
        ),
        "zipf": _spec(
            optional={"a": (int, float)},
            defaults={"a": 2.0},
            engines=(NUMPY,),
            semantic=_zipf,
            arrow_types=_fixed_arrow_types(pa.int64()),
            example={"method": "zipf", "kwargs": {}},
        ),
        "constant": _spec(
            required={"value": object},
            engines=(NUMPY,),
            semantic=_constant,
            arrow_types=_constant_arrow_type,
            example={"method": "constant", "kwargs": {"value": None}},
        ),
        "distincts_map": _spec(
            required={"distincts": dict},
            engines=(NUMPY,),
            kind=CORRELATED,
            semantic=_mapped_values,
            arrow_types=_mapped_arrow_types,
            example={
                "method": "distincts_map",
                "cols": ["category", "value"],
                "kwargs": {"distincts": {"a": ["b"]}},
            },
            requires_cols=True,
            expected_cols=2,
        ),
        "distincts_map_prop": _spec(
            required={"distincts": dict},
            engines=(NUMPY,),
            kind=CORRELATED,
            arrow_types=_weighted_mapped_arrow_types,
            example={
                "method": "distincts_map_prop",
                "cols": ["category", "value"],
                "kwargs": {"distincts": {"a": [["b", 1]]}},
            },
            requires_cols=True,
            expected_cols=2,
        ),
        "distincts_multi_map": _spec(
            required={"distincts": dict},
            engines=(NUMPY,),
            kind=CORRELATED,
            semantic=_multi_mapped_values,
            arrow_types=_multi_mapped_arrow_types,
            example={
                "method": "distincts_multi_map",
                "cols": ["category", "value"],
                "kwargs": {"distincts": {"a": [["b"]]}},
            },
            requires_cols=True,
        ),
        "complex_distincts": _spec(
            required={"pattern": str, "replacement": str, "templates": list},
            engines=(NUMPY,),
            kind=CORRELATED,
            arrow_types=_fixed_arrow_types(pa.string()),
            example={
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "<x>",
                    "replacement": "x",
                    "templates": [],
                },
            },
        ),
        "pk": _spec(
            optional={
                "style": str,
                "start": int,
                "step": int,
                "domain": int,
                "key": int,
                "format": str,
            },
            engines=(NUMPY,),
            kind=KEY,
            arrow_types=_pk_arrow_type,
            example={
                "method": "pk",
                "kwargs": {"style": "sequence", "start": 1, "step": 1},
            },
        ),
        "fk": _spec(
            required={"parent": dict, "parent_size": int},
            optional={"skew": (int, float)},
            engines=(NUMPY,),
            kind=KEY,
            arrow_types=_fk_arrow_type,
            example={
                "method": "fk",
                "kwargs": {
                    "parent": {"method": "pk", "kwargs": {}},
                    "parent_size": 10,
                },
            },
        ),
    }
)

COMMON_METHOD_SPECS: Mapping[str, dict[str, Any]] = MappingProxyType(
    {
        name: spec.as_table()
        for name, spec in METHOD_CATALOG.items()
        if spec.kind == ORDINARY and SPARK in spec.engines
    }
)


def matches_type(value: Any, rule: TypeRule) -> bool:
    rules = rule if isinstance(rule, tuple) else (rule,)
    if isinstance(value, bool) and bool not in rules and any(item in (int, float) for item in rules):
        return False
    return isinstance(value, rules)


def type_name(rule: TypeRule) -> str:
    rules = rule if isinstance(rule, tuple) else (rule,)
    return " or ".join(item.__name__ for item in rules)
