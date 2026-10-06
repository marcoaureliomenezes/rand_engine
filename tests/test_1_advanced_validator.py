"""
Tests for AdvancedValidator - validates DataGenerator specs.
Covers common methods (integers, floats, etc.) + advanced methods (distincts_map, pk, fk, etc.)
"""

import functools
import inspect

import pytest
from rand_engine.main._rand_generator import RandGenerator
from rand_engine.main.data_generator import DataGenerator
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.exceptions import SpecValidationError


def test_valid_spec_integers():
    """Testa spec válida com método integers."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 18, "max": 65}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 0


def test_valid_spec_with_all_basic_methods():
    """Testa spec válida com todos os métodos básicos."""
    spec = {
        "id": {"method": "int_zfilled", "kwargs": {"length": 12}},
        "idade": {"method": "integers", "kwargs": {"min": 0, "max": 100}},
        "preco": {"method": "floats", "kwargs": {"min": 0, "max": 1000, "decimals": 2}},
        "altura": {"method": "floats_normal", "kwargs": {"mean": 170, "std": 10, "decimals": 2}},
        "ativo": {"method": "booleans", "kwargs": {"true_prob": 0.7}},
        "plano": {"method": "distincts", "kwargs": {"distincts": ["free", "premium"]}},
        "dispositivo": {"method": "distincts_prop", "kwargs": {"distincts": {"mobile": 70, "desktop": 30}}},
        "created_at": {"method": "unix_timestamps", "kwargs": {"start": "01-01-2024", "end": "31-12-2024", "date_format": "%d-%m-%Y"}},
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 0


def test_valid_spec_with_correlated_columns():
    """Testa spec válida com colunas correlacionadas."""
    spec = {
        "device_os": {
            "method": "distincts_map",
            "cols": ["device_type", "os_type"],
            "kwargs": {"distincts": {
                "smartphone": ["android", "ios"],
                "desktop": ["windows", "linux"]
            }}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 0


def test_valid_spec_with_transformers():
    """Testa spec válida com transformers."""
    spec = {
        "nome": {
            "method": "distincts",
            "kwargs": {"distincts": ["joao", "maria", "pedro"]},
            "transformers": [lambda x: x.upper(), lambda x: x.strip()]
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 0


def test_invalid_spec_not_dict():
    """Testa erro quando spec não é dicionário."""
    spec = ["lista", "invalida"]
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "must be a dictionary" in errors[0]


def test_invalid_spec_empty():
    """Testa erro quando spec está vazia."""
    spec = {}
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "cannot be empty" in errors[0]


def test_invalid_column_config_not_dict():
    """Tests error when column configuration is not a dictionary."""
    spec = {
        "idade": "string_invalida"
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "configuration must be a dictionary" in errors[0]
    assert "idade" in errors[0]


def test_invalid_missing_method():
    """Testa erro quando campo method está ausente."""
    spec = {
        "idade": {
            "kwargs": {"min": 0, "max": 100}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "'method' is required" in errors[0]


def test_invalid_method_not_string():
    """Testa erro quando method não é string."""
    spec = {
        "idade": {
            "method": 12345,
            "kwargs": {"min": 0, "max": 100}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) > 0
    assert "'method' must be string" in errors[0]


def test_invalid_method_unknown():
    """Tests error when method does not exist."""
    spec = {
        "idade": {
            "method": "metodo_inexistente",
            "kwargs": {"min": 0, "max": 100}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "does not exist" in errors[0]
    assert "Available methods" in errors[0]


def test_invalid_missing_kwargs_and_args():
    """A spec without kwargs is checked against the method's required parameters."""
    spec = {
        "idade": {
            "method": "integers"
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 2
    assert "requires parameter 'min'" in errors[0]


def test_invalid_kwargs_not_dict():
    """Testa erro quando kwargs não é dicionário."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": [0, 100]  # Lista ao invés de dict
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "'kwargs' must be dictionary" in errors[0]


def test_invalid_missing_required_param():
    """Testa erro quando falta parâmetro obrigatório."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 0}  # Falta 'max'
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "requires parameter 'max'" in errors[0]
    assert "Correct example" in errors[0]


def test_invalid_wrong_param_type():
    """Testa erro quando tipo de parâmetro está errado."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": "zero", "max": "cem"}  # Strings ao invés de int
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 2  # min e max errados
    assert any("must be int" in e for e in errors)


def test_invalid_method_requires_cols():
    """Tests error when method requires cols but it wasn't provided."""
    spec = {
        "device_os": {
            "method": "distincts_map",
            "kwargs": {"distincts": {
                "smartphone": ["android", "ios"]
            }}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "requires" in errors[0] and "cols" in errors[0]


def test_invalid_cols_not_list():
    """Testa erro quando cols não é lista."""
    spec = {
        "device_os": {
            "method": "distincts_map",
            "cols": "device_type",  # String ao invés de lista
            "kwargs": {"distincts": {
                "smartphone": ["android", "ios"]
            }}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "'cols' must be list" in errors[0]


def test_invalid_transformers_not_list():
    """Testa erro quando transformers não é lista."""
    spec = {
        "nome": {
            "method": "distincts",
            "kwargs": {"distincts": ["joao", "maria"]},
            "transformers": lambda x: x.upper()  # Função direta ao invés de lista
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "'transformers' must be list" in errors[0]


def test_invalid_transformer_not_callable():
    """Testa erro quando transformer não é callable."""
    spec = {
        "nome": {
            "method": "distincts",
            "kwargs": {"distincts": ["joao", "maria"]},
            "transformers": ["string_invalida"]
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "must be callable" in errors[0]


def test_invalid_pk_not_dict():
    """Legacy 'pk' field (not in constraints) is no longer validated - passes silently."""
    spec = {
        "id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8},
            "pk": "users"  # Legacy field - no longer validated
        }
    }
    errors = AdvancedValidator.validate(spec)
    # No errors - legacy pk field is ignored in simplified validator
    assert len(errors) == 0


def test_invalid_pk_missing_required_fields():
    """Legacy 'pk' field (not in constraints) is no longer validated - passes silently."""
    spec = {
        "id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8},
            "pk": {"name": "users"}  # Legacy field - no longer validated
        }
    }
    errors = AdvancedValidator.validate(spec)
    # No errors - legacy pk field is ignored in simplified validator
    assert len(errors) == 0


def test_validate_and_raise_valid():
    """Testa que validate_and_raise não levanta exceção para spec válida."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 100}
        }
    }
    # Não deve levantar exceção
    AdvancedValidator.validate_and_raise(spec)


def test_validate_and_raise_invalid():
    """Tests that validate_and_raise raises exception for invalid spec."""
    spec = {
        "idade": {
            "method": "metodo_inexistente",
            "kwargs": {"min": 0, "max": 100}
        }
    }
    with pytest.raises(SpecValidationError) as exc_info:
        AdvancedValidator.validate_and_raise(spec)
    
    assert "SPEC VALIDATION ERROR" in str(exc_info.value)
    assert "does not exist" in str(exc_info.value)


def test_multiple_errors_in_single_column():
    """Testa múltiplos erros em uma única coluna."""
    spec = {
        "dados": {
            "method": "integers",
            "kwargs": {"min": "zero"},  # Tipo errado e falta 'max'
            "transformers": "nao_eh_lista"  # Tipo errado
        }
    }
    errors = AdvancedValidator.validate(spec)
    # Deve ter pelo menos 3 erros: tipo de min, falta max, transformers
    assert len(errors) >= 3


def test_multiple_errors_across_columns():
    """Testa múltiplos erros em diferentes colunas."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 0}  # Falta 'max'
        },
        "nome": {
            "method": "metodo_inexistente",
            "kwargs": {}
        },
        "ativo": {
            # Falta 'method'
            "kwargs": {"true_prob": 0.7}
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) >= 3  # Pelo menos um erro por coluna


def test_warning_for_unknown_params():
    """Testa aviso para unknown parameters."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {
                "min": 0,
                "max": 100,
                "parametro_invalido": "valor"
            }
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "unknown parameters" in errors[0]
    assert "parametro_invalido" in errors[0]


def test_valid_spec_complex_distincts():
    """Testa spec válida com complex_distincts."""
    spec = {
        "ip": {
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
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 0


# ============================================================================
# CONSTRAINTS VALIDATION TESTS
# ============================================================================

@pytest.mark.parametrize("constraints", [
    {"users_pk": {"name": "users_pk", "tipo": "PK", "fields": ["user_id VARCHAR(12)"]}},
    {},
])
def test_constraints_key_is_refused_naming_pk_and_fk(constraints):
    """AC5.1: the checkpoint left in 0.7.0; an old `constraints` spec fails pointing at pk/fk."""
    spec = {"user_id": {"method": "pk"}, "constraints": constraints}
    with pytest.raises(SpecValidationError, match=r"(?s)'constraints'.*\bpk\b.*\bfk\b"):
        DataGenerator(spec)
    assert len(AdvancedValidator.validate(spec)) == 1  # the refusal only, no column error on `constraints`


@pytest.mark.parametrize("config, message", [
    ({"method": "integers", "kwargs": {"min": 1, "max": 5, "dtype": "int"}}, "unknown parameters: 'dtype'"),
    ({"method": "distincts_external", "kwargs": {"name": "t", "fields": ["id"], "watermark": "1 DAY"}}, "does not exist"),
    ({"method": "distincts_map", "cols": ["device", "os"]}, "requires parameter 'distincts'"),
])
def test_spec_the_engine_cannot_run_is_rejected(config, message):
    """validator-engine-schema-drift: no spec validates that DataGenerator then fails to generate."""
    with pytest.raises(SpecValidationError, match=message):
        DataGenerator({"c": config})


def test_validated_spec_without_kwargs_generates():
    """The validator's own uuid4 example (no kwargs) validates and generates."""
    assert len(DataGenerator({"id": {"method": "uuid4"}}).size(3).get_df()) == 3


@pytest.mark.parametrize("column, match", [
    ({"method": "pk", "kwargs": {"style": "random"}}, r"(?s)style.*sequence.*permuted"),
    ({"method": "pk", "kwargs": {"style": "permuted"}}, r"integer .domain."),
    ({"method": "pk", "kwargs": {"style": "permuted", "domain": 0}}, r"integer .domain."),
    ({"method": "pk", "kwargs": {"step": 0}}, r"step"),
    ({"method": "pk", "kwargs": {"start": 1.5}}, r"start"),
    ({"method": "pk", "kwargs": {"step": "2"}}, r"step"),
    ({"method": "pk", "kwargs": {"style": "permuted", "domain": 10, "key": 0.5}}, r"key"),
    ({"method": "pk", "kwargs": {"format": "C-{}-{}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "C-"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "C-{x}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "C-{1}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{:s}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{:.0e}"}}, r"format"),
    ({"method": "pk", "kwargs": {"start": 2**60, "format": "{:.0%}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{:.2d}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{!s:.1}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "C-{:{}}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{:{x}}"}}, r"format"),
    ({"method": "pk", "kwargs": {"format": "{0:{0}}"}}, r"format"),
    ({"method": "pk", "kwargs": {"domain": 5, "key": 3}}, r"(?s)'sequence' does not take.*domain.*key"),
    ({"method": "pk", "kwargs": {"style": "permuted", "domain": 5, "step": 2}}, r"(?s)'permuted' does not take.*step"),
    ({"method": "pk", "kwargs": {"style": "permuted", "domain": 2**62, "start": 2**62 + 1}}, r"int64"),
    ({"method": "pk", "kwargs": {"style": "permuted", "domain": 2**62 + 1}}, r"int64"),
    ({"method": "pk", "args": [1]}, r"args"),
    ({"method": "pk", "kwargs": {}, "transformers": [lambda x: x]}, r"transformers"),
])
def test_pk_spec_is_refused(column, match):
    """AC1.7: every unbuildable or non-unique pk spec fails before generation."""
    with pytest.raises(SpecValidationError, match=match):
        DataGenerator({"id": column})


def test_pk_permuted_with_format_and_key_is_accepted():
    spec = {"id": {"method": "pk", "kwargs": {"style": "permuted", "domain": 100, "key": 3, "format": "C-{0:,}"}},
            "top": {"method": "pk", "kwargs": {"style": "permuted", "domain": 2**62, "start": 2**62 - 1}}}
    assert AdvancedValidator.validate(spec) == []


FK_PARENT = {"method": "pk", "kwargs": {"style": "permuted", "domain": 100}}


@pytest.mark.parametrize("kwargs, match", [
  ({"parent": {"method": "integers", "kwargs": {"min": 0, "max": 9}}, "parent_size": 10}, r"'parent'.*pk column spec"),
  ({"parent": {"kwargs": {}}, "parent_size": 10}, r"'parent'.*pk column spec"),
  ({"parent": {"method": "pk", "kwargs": {}, "transformers": [str]}, "parent_size": 10}, r"pid\.parent.*transformers"),
  ({"parent": {"method": "pk", "kwargs": {"step": 0}}, "parent_size": 10}, r"step"),
  ({"parent": {"method": "pk", "kwargs": {}, "cols": ["a"]}, "parent_size": 10}, r"'parent'.*\['cols'\]"),
  ({"parent": FK_PARENT, "parent_size": 0}, r"parent_size.*>= 1"),
  ({"parent": FK_PARENT, "parent_size": 101}, r"parent_size 101.*domain 100"),
  ({"parent": FK_PARENT, "parent_size": 10, "skew": -0.1}, r"skew.*>= 0"),
  ({"parent": FK_PARENT, "parent_size": 10, "skew": "1"}, r"skew"),
  ({"parent": FK_PARENT, "parent_size": 10, "skew": True}, r"skew.*number"),
  ({"parent": FK_PARENT, "parent_size": 10, "skew": float("nan")}, r"skew.*finite"),
  ({"parent": FK_PARENT, "parent_size": 10, "skew": float("inf")}, r"skew.*finite"),
  ({"parent": FK_PARENT, "parent_size": True}, r"parent_size.*integer"),
  ({"parent": FK_PARENT, "parent_size": 10, "seed": 1}, r"Unknown parameter 'seed'"),
])
def test_fk_spec_is_refused(kwargs, match):
  """AC2.6."""
  with pytest.raises(SpecValidationError, match=match):
    AdvancedValidator.validate_and_raise({"pid": {"method": "fk", "kwargs": kwargs}})


def test_fk_with_domain_sized_parent_and_skew_is_accepted():
  AdvancedValidator.validate_and_raise({"pid": {"method": "fk", "kwargs": {"parent": FK_PARENT, "parent_size": 100, "skew": 1}}})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


@pytest.mark.parametrize("column", [
  {"method": "integers", "args": [1, 9]},
  {"method": "uuid4", "args": [5]},
  {"method": "integers", "kwargs": {"min": 0, "max": 9}, "args": [0, 9]},
])
def test_args_is_refused(column):
  """The Spark side is owned by test_1_common_validator ("does not support 'args'")."""
  errors = AdvancedValidator.validate({"x": column})
  assert len(errors) == 1
  assert "'args'" in errors[0] and "'kwargs'" in errors[0]


@pytest.mark.parametrize("template, match", [
  ({"method": "integers", "kwargs": {"min": 0, "max": 9, "dtype": "int8"}}, r"(?s)c\.templates\[0\].*dtype"),
  ({"method": "integers", "kwargs": {"max": 9}}, r"(?s)c\.templates\[0\].*requires parameter 'min'"),
  ({"method": "distincts_map", "kwargs": {"distincts": {"a": ["b"]}}}, r"(?s)c\.templates\[0\].*distincts_map"),
])
def test_complex_distincts_template_is_checked(template, match):
  spec = {"c": {"method": "complex_distincts", "kwargs": {"pattern": "<x>", "replacement": "x", "templates": [template]}}}
  with pytest.raises(SpecValidationError, match=match):
    DataGenerator(spec)


@pytest.mark.parametrize("template, expected", [
  ({"method": "dates", "kwargs": {"start": "2024-01-01", "end": "2024-01-02"}}, "<2024-01-01>"),
  ({"method": "distincts_prop", "kwargs": {"distincts": {"a": 1}}}, "<a>"),
])
def test_complex_distincts_template_that_validates_generates(template, expected):
  spec = {"c": {"method": "complex_distincts", "kwargs": {"pattern": "<x>", "replacement": "x", "templates": [template]}}}
  assert set(DataGenerator(spec, seed=1).size(20).get_df()["c"]) == {expected}


@pytest.mark.parametrize("cols, got", [(["k", "l"], "got 2"), (["k", "l", "m", "n"], "got 4")])
def test_distincts_multi_map_cols_must_be_levels_plus_one(cols, got):
  spec = {"c": {"method": "distincts_multi_map", "kwargs": {"distincts": {"t": [["a", "b"], ["x", "y"]]}}, "cols": cols}}
  errors = AdvancedValidator.validate(spec)
  assert len(errors) == 1
  assert "'t' has 2 levels, so 'cols' needs 3 names" in errors[0] and got in errors[0]


def _params(fn, injected=("size", "rng", "spark", "F", "df", "col_name", "offset", "key_seed", "column")):
  sig = inspect.signature(fn.func if isinstance(fn, functools.partial) else fn).parameters.values()
  if any(p.kind is p.VAR_KEYWORD for p in sig):
    return None
  names = {p.name for p in sig} - set(injected)
  return names, {p.name for p in sig if p.default is p.empty} - set(injected)


def test_validator_tables_match_engine_maps_and_signatures():
  """One method set: every validator table pinned to both engine maps and to each callable's parameters."""
  common, advanced = CommonValidator.METHOD_SPECS, AdvancedValidator.METHOD_SPECS
  pandas = RandGenerator({}).map_methods()
  spark = SparkGenerator.map_methods(None)
  assert set(common) | set(advanced) == set(pandas)
  assert set(common) | set(advanced) - {"pk", "fk"} == set(spark)
  for name, fn in [*pandas.items(), *spark.items()]:
    table = (common.get(name) or advanced[name])["params"]
    params = _params(fn)
    if params is None:
      continue
    names, required = params
    assert set(table["required"]) | set(table["optional"]) == names, name
    assert required <= set(table["required"]), name
