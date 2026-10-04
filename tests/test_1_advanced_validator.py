"""
Tests for AdvancedValidator - validates DataGenerator specs.
Covers common methods (integers, floats, etc.) + advanced methods (distincts_map, pk, fk, etc.)
"""

import pytest
from rand_engine.main.data_generator import DataGenerator
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


def test_invalid_both_kwargs_and_args():
    """Tests error when having both kwargs and args simultaneously."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 100},
            "args": [0, 100]
        }
    }
    errors = AdvancedValidator.validate(spec)
    assert len(errors) == 1
    assert "cannot have both" in errors[0] and "simultaneously" in errors[0]


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
