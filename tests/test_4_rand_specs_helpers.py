import builtins
import copy
import random

import numpy as np
import pyarrow as pa
import pytest
from faker.generator import random as faker_random

from rand_engine import DataGenerator, RandSpecs
from rand_engine.validators.exceptions import RandEngineError, SpecValidationError


def _helper(name):
  helper = getattr(RandSpecs, name, None)
  assert callable(helper), f"RandSpecs.{name} must be a callable helper"
  return helper


def _numpy_state_equal(left, right):
  return (
      left[0] == right[0]
      and np.array_equal(left[1], right[1])
      and left[2:] == right[2:]
  )


SUPPORTED_SCHEMA = pa.schema([
    pa.field("flag", pa.bool_(), nullable=True, metadata={b"label": b"ignored"}),
    pa.field("i8", pa.int8()),
    pa.field("i16", pa.int16()),
    pa.field("i32", pa.int32()),
    pa.field("i64", pa.int64()),
    pa.field("u8", pa.uint8()),
    pa.field("u16", pa.uint16()),
    pa.field("u32", pa.uint32()),
    pa.field("u64", pa.uint64()),
    pa.field("f32", pa.float32()),
    pa.field("f64", pa.float64()),
    pa.field("text", pa.string()),
    pa.field("large_text", pa.large_string()),
    pa.field("day32", pa.date32()),
    pa.field("day64", pa.date64()),
    pa.field("moment", pa.timestamp("us")),
    pa.field("nothing", pa.null()),
])


EXPECTED_SCHEMA_SPEC = {
    "flag": {"method": "booleans", "kwargs": {"true_prob": 0.5}},
    "i8": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "int8"}},
    "i16": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "int16"}},
    "i32": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "int32"}},
    "i64": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "int64"}},
    "u8": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "uint8"}},
    "u16": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "uint16"}},
    "u32": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "uint32"}},
    "u64": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "uint64"}},
    "f32": {"method": "floats", "kwargs": {"min": 0, "max": 1, "decimals": 2}},
    "f64": {"method": "floats", "kwargs": {"min": 0, "max": 1, "decimals": 2}},
    "text": {"method": "uuid4", "kwargs": {}},
    "large_text": {"method": "uuid4", "kwargs": {}},
    "day32": {
        "method": "dates",
        "kwargs": {"start": "2000-01-01", "end": "2030-12-31", "date_format": "%Y-%m-%d"},
    },
    "day64": {
        "method": "dates",
        "kwargs": {"start": "2000-01-01", "end": "2030-12-31", "date_format": "%Y-%m-%d"},
    },
    "moment": {
        "method": "dates",
        "kwargs": {
            "start": "2000-01-01",
            "end": "2030-12-31",
            "date_format": "%Y-%m-%d %H:%M:%S",
        },
    },
    "nothing": {"method": "constant", "kwargs": {"value": None}},
}


def test_from_schema_maps_every_supported_arrow_type_and_generates_declared_outputs():
  from_schema = _helper("from_schema")

  spec = from_schema(SUPPORTED_SCHEMA)

  assert type(spec) is dict
  assert spec == EXPECTED_SCHEMA_SPEC
  frame = DataGenerator(spec, seed=31).size(4).get_df()
  assert frame.dtypes.astype(str).to_dict() == {
      "flag": "bool",
      "i8": "int8",
      "i16": "int16",
      "i32": "int32",
      "i64": "int64",
      "u8": "uint8",
      "u16": "uint16",
      "u32": "uint32",
      "u64": "uint64",
      "f32": "float64",
      "f64": "float64",
      "text": "object",
      "large_text": "object",
      "day32": "object",
      "day64": "object",
      "moment": "object",
      "nothing": "object",
  }
  assert frame["nothing"].tolist() == [None] * 4


def test_from_schema_merges_kwargs_but_whole_method_overrides_replace_defaults():
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("count", pa.int16()), pa.field("amount", pa.decimal128(12, 2))])
  overrides = {
      "count": {"kwargs": {"min": 7}, "null_rate": 0.25},
      "amount": {"method": "constant", "kwargs": {"value": "12.34"}},
  }

  spec = from_schema(schema, overrides=overrides)

  assert spec == {
      "count": {
          "method": "integers",
          "kwargs": {"min": 7, "max": 100, "int_type": "int16"},
          "null_rate": 0.25,
      },
      "amount": {"method": "constant", "kwargs": {"value": "12.34"}},
  }


def test_from_schema_copies_schema_and_nested_override_inputs():
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("value", pa.int32(), metadata={b"source": b"caller"})])
  overrides = {"value": {"kwargs": {"min": 9}, "transformers": [str]}}
  schema_before = schema.serialize().to_pybytes()
  overrides_before = copy.deepcopy(overrides)

  result = from_schema(schema, overrides=overrides)
  result["value"]["kwargs"]["min"] = 77
  result["value"]["transformers"].append(int)

  assert schema.serialize().to_pybytes() == schema_before
  assert overrides == overrides_before


@pytest.mark.parametrize("invalid", [{"x": pa.int8()}, pa.table({"x": [1]})])
def test_from_schema_refuses_non_schema_inputs(invalid):
  from_schema = _helper("from_schema")

  with pytest.raises(SpecValidationError, match="pyarrow.Schema"):
    from_schema(invalid)


def test_from_schema_refuses_unknown_or_incomplete_overrides():
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("count", pa.int16())])

  with pytest.raises(SpecValidationError, match="missing"):
    from_schema(schema, overrides={"missing": {"kwargs": {"min": 1}}})
  with pytest.raises(SpecValidationError, match="count"):
    from_schema(schema, overrides={"count": {"method": "constant"}})


def test_from_schema_refuses_unsupported_and_duplicate_fields_with_a_remedy():
  from_schema = _helper("from_schema")

  with pytest.raises(SpecValidationError, match=r"amount.*decimal.*override"):
    from_schema(pa.schema([pa.field("amount", pa.decimal128(12, 2))]))
  with pytest.raises(SpecValidationError, match=r"duplicate.*code|code.*duplicate"):
    from_schema(pa.schema([pa.field("code", pa.int8()), pa.field("code", pa.int16())]))


@pytest.mark.parametrize(
    "arrow_type, type_name",
    [
        (pa.decimal128(12, 2), "decimal"),
        (pa.binary(), "binary"),
        (pa.binary(4), "fixed_size_binary"),
        (pa.time32("s"), "time32"),
        (pa.duration("ms"), "duration"),
        (pa.month_day_nano_interval(), "month_day_nano_interval"),
        (pa.list_(pa.int8()), "list"),
        (pa.dictionary(pa.int8(), pa.string()), "dictionary"),
        (pa.timestamp("us", tz="UTC"), "timestamp"),
    ],
)
def test_from_schema_requires_complete_overrides_for_every_unsupported_family(arrow_type, type_name):
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("payload", arrow_type)])
  override = {"payload": {"method": "constant", "kwargs": {"value": "literal"}}}

  with pytest.raises(SpecValidationError, match=rf"payload.*{type_name}.*override"):
    from_schema(schema)

  assert from_schema(schema, overrides=override) == override


@pytest.mark.parametrize(
    "arrow_type, type_name",
    [(pa.uuid(), "uuid"), (pa.json_(), "json")],
)
def test_from_schema_refuses_installed_extension_types_unless_completely_overridden(arrow_type, type_name):
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("payload", arrow_type)])
  override = {"payload": {"method": "constant", "kwargs": {"value": "literal"}}}

  with pytest.raises(SpecValidationError, match=rf"payload.*{type_name}.*override"):
    from_schema(schema)

  assert from_schema(schema, overrides=override) == override


def test_from_schema_validates_the_semantics_of_merged_kwargs_overrides():
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("count", pa.int16())])

  with pytest.raises(SpecValidationError, match=r"count.*min.*max"):
    from_schema(schema, overrides={"count": {"kwargs": {"min": 101}}})


def test_from_schema_refuses_a_methodless_override_for_an_unsupported_type():
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("payload", pa.binary())])

  with pytest.raises(SpecValidationError, match=r"payload.*binary.*method|payload.*complete.*override"):
    from_schema(schema, overrides={"payload": {"kwargs": {"value": b"raw"}}})


@pytest.mark.parametrize("overrides", [[], {"value": []}])
def test_from_schema_refuses_malformed_override_shapes(overrides):
  from_schema = _helper("from_schema")
  schema = pa.schema([pa.field("value", pa.int32())])

  with pytest.raises(SpecValidationError, match="override"):
    from_schema(schema, overrides=overrides)


def test_faker_pool_has_a_seeded_literal_pool_and_returns_an_ordinary_spec():
  faker_pool = _helper("faker_pool")
  expected = {
      "method": "distincts",
      "kwargs": {
          "distincts": [
              "Sr. Miguel Rezende",
              "Brayan Nascimento",
              "Luiz Otávio Pacheco",
              "Thiago Cunha",
              "Caio Lopes",
          ]
      },
  }

  first = faker_pool("name", locale="pt_BR", pool_size=5, seed=7)
  second = faker_pool("name", locale="pt_BR", pool_size=5, seed=7)
  changed = faker_pool("name", locale="pt_BR", pool_size=5, seed=8)

  assert first == expected
  assert second == expected
  assert changed["kwargs"]["distincts"] == [
      "Léo Garcia",
      "Gael Santos",
      "Bryan Carvalho",
      "Thiago Costela",
      "Ana Marques",
  ]
  assert changed != first


def test_faker_pool_does_not_change_python_numpy_or_faker_global_rng_state():
  faker_pool = _helper("faker_pool")
  python_before = random.getstate()
  numpy_before = np.random.get_state()
  faker_before = faker_random.getstate()

  faker_pool("name", locale="pt_BR", pool_size=5, seed=7)

  assert random.getstate() == python_before
  assert _numpy_state_equal(np.random.get_state(), numpy_before)
  assert faker_random.getstate() == faker_before


def test_faker_pool_is_materialized_before_generation(monkeypatch):
  faker_pool = _helper("faker_pool")
  spec = {"person": faker_pool("name", locale="pt_BR", pool_size=5, seed=7)}
  expected_pool = set(spec["person"]["kwargs"]["distincts"])
  real_import = builtins.__import__

  def refuse_faker(name, *args, **kwargs):
    if name == "faker" or name.startswith("faker."):
      raise AssertionError("generation must not call Faker")
    return real_import(name, *args, **kwargs)

  monkeypatch.setattr(builtins, "__import__", refuse_faker)
  values = DataGenerator(spec, seed=17).size(30).get_df()["person"]

  assert set(values) <= expected_pool
  assert len(values) == 30


def test_faker_pool_translates_a_missing_optional_dependency_at_the_import_boundary(monkeypatch):
  faker_pool = _helper("faker_pool")
  real_import = builtins.__import__

  def missing_faker(name, *args, **kwargs):
    if name == "faker" or name.startswith("faker."):
      raise ImportError("simulated missing optional dependency")
    return real_import(name, *args, **kwargs)

  monkeypatch.setattr(builtins, "__import__", missing_faker)
  with pytest.raises(RandEngineError, match=r"(?i)faker.*optional|optional.*faker"):
    faker_pool("name", locale="pt_BR", pool_size=5, seed=7)


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"provider": "not_a_provider", "locale": "pt_BR", "pool_size": 5, "seed": 7}, "provider"),
        ({"provider": "name", "locale": "not_A_LOCALE", "pool_size": 5, "seed": 7}, "locale"),
        ({"provider": "name", "locale": "pt_BR", "pool_size": 0, "seed": 7}, "pool_size"),
        ({"provider": "name", "locale": "pt_BR", "pool_size": True, "seed": 7}, "pool_size"),
        ({"provider": "profile", "locale": "pt_BR", "pool_size": 1, "seed": 7}, "scalar"),
    ],
)
def test_faker_pool_refuses_invalid_construction_inputs(kwargs, message):
  faker_pool = _helper("faker_pool")

  with pytest.raises(RandEngineError, match=message):
    faker_pool(**kwargs)


@pytest.mark.parametrize("pool_size", [-1, 1.5, "5"])
def test_faker_pool_refuses_negative_and_non_integer_sizes(pool_size):
  faker_pool = _helper("faker_pool")

  with pytest.raises(RandEngineError, match="pool_size"):
    faker_pool("name", locale="pt_BR", pool_size=pool_size, seed=7)
