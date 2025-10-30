"""
Testes para o novo validador educativo (SpecValidator v2).
"""

import pytest
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.exceptions import SpecValidationError


def test_valid_spec_integers():
    """Testa spec válida com método integers."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 18, "max": 65}
        }
    }
    errors = SpecValidator.validate(spec)
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
        "created_at": {"method": "unix_timestamps", "kwargs": {"start": "01-01-2024", "end": "31-12-2024", "format": "%d-%m-%Y"}},
    }
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_invalid_spec_not_dict():
    """Testa erro quando spec não é dicionário."""
    spec = ["lista", "invalida"]
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "must be a dictionary" in errors[0]


def test_invalid_spec_empty():
    """Testa erro quando spec está vazia."""
    spec = {}
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "cannot be empty" in errors[0]


def test_invalid_column_config_not_dict():
    """Tests error when column configuration is not a dictionary."""
    spec = {
        "idade": "string_invalida"
    }
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "cannot have both" in errors[0] and "simultaneously" in errors[0]


def test_invalid_missing_kwargs_and_args():
    """Tests error when neither kwargs nor args are present."""
    spec = {
        "idade": {
            "method": "integers"
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "requires" in errors[0] and ("kwargs" in errors[0] or "args" in errors[0])


def test_invalid_kwargs_not_dict():
    """Testa erro quando kwargs não é dicionário."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": [0, 100]  # Lista ao invés de dict
        }
    }
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "must be callable" in errors[0]


def test_invalid_pk_not_dict():
    """Testa erro quando pk não é dicionário."""
    spec = {
        "id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8},
            "pk": "users"  # String ao invés de dict
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "'pk' must be dictionary" in errors[0]


def test_invalid_pk_missing_required_fields():
    """Tests error when pk doesn't have required fields."""
    spec = {
        "id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8},
            "pk": {"name": "users"}  # Missing 'datatype'
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "requires" in errors[0] and "datatype" in errors[0]


def test_validate_and_raise_valid():
    """Testa que validate_and_raise não levanta exceção para spec válida."""
    spec = {
        "idade": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 100}
        }
    }
    # Não deve levantar exceção
    SpecValidator.validate_and_raise(spec)


def test_validate_and_raise_invalid():
    """Tests that validate_and_raise raises exception for invalid spec."""
    spec = {
        "idade": {
            "method": "metodo_inexistente",
            "kwargs": {"min": 0, "max": 100}
        }
    }
    with pytest.raises(SpecValidationError) as exc_info:
        SpecValidator.validate_and_raise(spec)
    
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
    errors = SpecValidator.validate(spec)
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
                    {"method": "distincts", "parms": {"distincts": ["192", "10"]}},
                    {"method": "integers", "parms": {"min": 0, "max": 255}},
                    {"method": "integers", "parms": {"min": 0, "max": 255}},
                    {"method": "integers", "parms": {"min": 1, "max": 254}}
                ]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


# ============================================================================
# CONSTRAINTS VALIDATION TESTS
# ============================================================================

def test_valid_constraints_pk_simple():
    """Testa constraint PK válida simples."""
    spec = {
        "category_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 4}
        },
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK",
                "fields": ["category_id VARCHAR(4)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_valid_constraints_pk_composite():
    """Testa constraint PK composta (múltiplos campos)."""
    spec = {
        "client_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8}
        },
        "tp_pes": {
            "method": "distincts",
            "kwargs": {"distincts": ["PF", "PJ"]}
        },
        "constraints": {
            "clients_pk": {
                "name": "clients_pk",
                "tipo": "PK",
                "fields": ["client_id VARCHAR(8)", "tp_pes VARCHAR(2)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_valid_constraints_fk_with_watermark():
    """Testa constraint FK válida com watermark."""
    spec = {
        "product_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8}
        },
        "constraints": {
            "category_fk": {
                "name": "category_pk",
                "tipo": "FK",
                "fields": ["category_id"],
                "watermark": 60
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_valid_constraints_fk_without_watermark():
    """Testa constraint FK sem watermark (warning esperado)."""
    spec = {
        "product_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8}
        },
        "constraints": {
            "category_fk": {
                "name": "category_pk",
                "tipo": "FK",
                "fields": ["category_id"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    # Should have 1 warning about missing watermark
    assert len(errors) == 1
    assert "watermark" in errors[0].lower()
    assert "⚠️" in errors[0]


def test_valid_constraints_fk_composite():
    """Testa constraint FK composta."""
    spec = {
        "transaction_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8}
        },
        "constraints": {
            "clients_fk": {
                "name": "clients_pk",
                "tipo": "FK",
                "fields": ["client_id", "tp_pes"],
                "watermark": 60
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_invalid_constraints_not_dict():
    """Testa erro quando constraints não é dicionário."""
    spec = {
        "id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": "string_invalida"
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("must be dictionary" in err for err in errors)


def test_invalid_constraints_empty():
    """Testa warning quando constraints está vazio."""
    spec = {
        "id": {"method": "int_zfilled", "kwargs": {"length": 8}},
        "constraints": {}
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 1
    assert "empty" in errors[0].lower()


def test_invalid_constraint_missing_name():
    """Testa erro quando constraint não tem campo 'name'."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "tipo": "PK",
                "fields": ["category_id VARCHAR(4)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("missing required field 'name'" in err for err in errors)


def test_invalid_constraint_missing_tipo():
    """Testa erro quando constraint não tem campo 'tipo'."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "fields": ["category_id VARCHAR(4)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("missing required field 'tipo'" in err for err in errors)


def test_invalid_constraint_missing_fields():
    """Testa erro quando constraint não tem campo 'fields'."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK"
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("missing required field 'fields'" in err for err in errors)


def test_invalid_constraint_tipo_invalid():
    """Testa erro quando tipo não é PK nem FK."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "UNIQUE",  # Invalid
                "fields": ["category_id VARCHAR(4)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("must be 'PK' or 'FK'" in err for err in errors)


def test_invalid_constraint_fields_not_list():
    """Testa erro quando fields não é lista."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK",
                "fields": "category_id VARCHAR(4)"  # Should be list
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("'fields' must be list" in err for err in errors)


def test_invalid_constraint_fields_empty():
    """Testa erro quando fields está vazia."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK",
                "fields": []
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("cannot be empty" in err for err in errors)


def test_invalid_constraint_watermark_negative():
    """Testa erro quando watermark é negativo."""
    spec = {
        "product_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_fk": {
                "name": "category_pk",
                "tipo": "FK",
                "fields": ["category_id"],
                "watermark": -60  # Invalid
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("must be positive" in err for err in errors)


def test_invalid_constraint_watermark_on_pk():
    """Testa warning quando PK tem watermark (desnecessário)."""
    spec = {
        "category_id": {"method": "int_zfilled", "kwargs": {}},
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK",
                "fields": ["category_id VARCHAR(4)"],
                "watermark": 60  # Warning: only for FK
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) >= 1
    assert any("only used for FK" in err for err in errors)


def test_valid_constraints_multiple():
    """Testa múltiplas constraints no mesmo spec."""
    spec = {
        "category_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 4}
        },
        "product_id": {
            "method": "int_zfilled",
            "kwargs": {"length": 8}
        },
        "constraints": {
            "category_pk": {
                "name": "category_pk",
                "tipo": "PK",
                "fields": ["category_id VARCHAR(4)"]
            },
            "product_pk": {
                "name": "product_pk",
                "tipo": "PK",
                "fields": ["product_id VARCHAR(8)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


def test_constraints_not_interfere_with_columns():
    """Testa que constraints não interferem na validação de colunas."""
    spec = {
        "age": {
            "method": "integers",
            "kwargs": {"min": 0, "max": 100}
        },
        "constraints": {
            "users_pk": {
                "name": "users_pk",
                "tipo": "PK",
                "fields": ["user_id VARCHAR(12)"]
            }
        }
    }
    errors = SpecValidator.validate(spec)
    assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
