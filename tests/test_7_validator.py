"""
Testes para o módulo de validação de specs.
"""

import pytest
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.exceptions import SpecValidationError
from rand_engine.core._np_core import NPCore


class TestSpecValidator:
    """Testes para SpecValidator."""
    
    def test_valid_spec_with_kwargs(self):
        """Testa validação de spec válida com kwargs."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100}
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_with_args(self):
        """Testa validação de spec válida com args."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "args": [0, 100]
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_with_transformers(self):
        """Testa validação de spec válida com transformers."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100},
                "transformers": [lambda x: x * 2]
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_with_splitable(self):
        """Testa validação de spec válida com splitable."""
        spec = {
            "device_os": {
                "method": NPCore.gen_distincts,
                "kwargs": {"distinct": ["mobile;iOS", "desktop;Windows"]},
                "splitable": True,
                "cols": ["device", "os"],
                "sep": ";"
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_valid_spec_with_distincts_prop(self):
        """Testa validação de spec válida com distincts_prop."""
        spec = {
            "plan": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"free": 70, "standard": 30}}
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 0
    
    def test_missing_method(self):
        """Testa erro quando 'method' está ausente."""
        spec = {
            "age": {
                "kwargs": {"min": 0, "max": 100}
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "missing required key 'method'" in errors[0]
        assert "'age'" in errors[0]
    
    def test_method_not_callable(self):
        """Testa erro quando 'method' não é callable nem string válida."""
        spec = {
            "age": {
                "method": "not_callable",
                "kwargs": {"min": 0, "max": 100}
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "invalid method identifier 'not_callable'" in errors[0]
        assert "'age'" in errors[0]
    
    def test_kwargs_and_args_together(self):
        """Testa erro quando kwargs e args são usados juntos."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100},
                "args": [0, 100]
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "cannot have both 'kwargs' and 'args'" in errors[0]
    
    def test_kwargs_not_dict(self):
        """Testa erro quando kwargs não é dict."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": [0, 100]  # Deveria ser dict
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'kwargs' must be a dict" in errors[0]
    
    def test_args_not_list(self):
        """Testa erro quando args não é list/tuple."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "args": {"min": 0, "max": 100}  # Deveria ser list
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'args' must be a list or tuple" in errors[0]
    
    def test_transformers_not_list(self):
        """Testa erro quando transformers não é list."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100},
                "transformers": lambda x: x * 2  # Deveria ser list
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'transformers' must be a list" in errors[0]
    
    def test_transformer_not_callable(self):
        """Testa erro quando transformer não é callable."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100},
                "transformers": ["not_callable"]
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "transformer at index 0 is not callable" in errors[0]
    
    def test_splitable_without_cols(self):
        """Testa erro quando splitable=True mas falta 'cols'."""
        spec = {
            "device_os": {
                "method": NPCore.gen_distincts,
                "kwargs": {"distinct": ["mobile;iOS"]},
                "splitable": True
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "splitable=True requires 'cols'" in errors[0]
    
    def test_splitable_cols_not_list(self):
        """Testa erro quando 'cols' não é list."""
        spec = {
            "device_os": {
                "method": NPCore.gen_distincts,
                "kwargs": {"distinct": ["mobile;iOS"]},
                "splitable": True,
                "cols": "device,os"  # Deveria ser list
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'cols' must be a list" in errors[0]
    
    def test_splitable_cols_empty(self):
        """Testa erro quando 'cols' está vazio."""
        spec = {
            "device_os": {
                "method": NPCore.gen_distincts,
                "kwargs": {"distinct": ["mobile;iOS"]},
                "splitable": True,
                "cols": []
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'cols' cannot be empty" in errors[0]
    
    def test_splitable_sep_not_string(self):
        """Testa erro quando 'sep' não é string."""
        spec = {
            "device_os": {
                "method": NPCore.gen_distincts,
                "kwargs": {"distinct": ["mobile;iOS"]},
                "splitable": True,
                "cols": ["device", "os"],
                "sep": 123  # Deveria ser string
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "'sep' must be a string" in errors[0]
    
    def test_spec_not_dict(self):
        """Testa erro quando spec não é dict."""
        spec = ["not", "a", "dict"]
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "Spec must be a dict" in errors[0]
    
    def test_spec_empty(self):
        """Testa erro quando spec está vazio."""
        spec = {}
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "Spec cannot be empty" in errors[0]
    
    def test_column_config_not_dict(self):
        """Testa erro quando config de coluna não é dict."""
        spec = {
            "age": "not_a_dict"
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) == 1
        assert "config must be a dict" in errors[0]
    
    def test_multiple_errors(self):
        """Testa detecção de múltiplos erros."""
        spec = {
            "age": {
                "method": "not_callable",
                "kwargs": [0, 100],  # Deveria ser dict
                "args": [0, 100]  # kwargs e args juntos
            },
            "name": {
                # Falta method
                "kwargs": {"distinct": ["John"]}
            }
        }
        errors = SpecValidator.validate(spec)
        assert len(errors) >= 4  # Pelo menos 4 erros
    
    def test_validate_and_raise_valid_spec(self):
        """Testa que validate_and_raise não levanta exceção para spec válida."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100}
            }
        }
        # Não deve levantar exceção
        SpecValidator.validate_and_raise(spec)
    
    def test_validate_and_raise_invalid_spec(self):
        """Testa que validate_and_raise levanta exceção para spec inválida."""
        spec = {
            "age": {
                "method": "not_callable"
            }
        }
        with pytest.raises(SpecValidationError) as exc_info:
            SpecValidator.validate_and_raise(spec)
        
        assert "Spec validation failed" in str(exc_info.value)
        assert "invalid method identifier 'not_callable'" in str(exc_info.value)
    
    def test_validate_with_warnings_valid(self, capsys):
        """Testa validate_with_warnings com spec válida."""
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 0, "max": 100}
            }
        }
        result = SpecValidator.validate_with_warnings(spec)
        assert result is True
        
        captured = capsys.readouterr()
        assert "✅ Spec is valid" in captured.out
    
    def test_validate_with_warnings_invalid(self, capsys):
        """Testa validate_with_warnings com spec inválida."""
        spec = {
            "age": {
                "method": "not_callable"
            }
        }
        result = SpecValidator.validate_with_warnings(spec)
        assert result is False
        
        captured = capsys.readouterr()
        assert "❌ Spec validation errors" in captured.out
        assert "invalid method identifier 'not_callable'" in captured.out


class TestDataGeneratorValidation:
    """Testes de integração com DataGenerator."""
    
    def test_data_generator_valid_spec(self):
        """Testa que DataGenerator aceita spec válida."""
        from rand_engine.main.data_generator import DataGenerator
        
        spec = {
            "age": {
                "method": NPCore.gen_ints,
                "kwargs": {"min": 18, "max": 65}
            }
        }
        # Não deve levantar exceção
        engine = DataGenerator(spec, seed=42)
        assert engine is not None
    
    def test_data_generator_invalid_spec(self):
        """Testa que DataGenerator rejeita spec inválida."""
        from rand_engine.main.data_generator import DataGenerator
        
        spec = {
            "age": {
                "method": "not_callable"
            }
        }
        with pytest.raises(SpecValidationError):
            DataGenerator(spec)
    
    def test_data_generator_skip_validation(self):
        """Testa que validação pode ser desabilitada."""
        from rand_engine.main.data_generator import DataGenerator
        
        spec = {
            "age": {
                "method": "not_callable"
            }
        }
        # Não deve levantar exceção quando validate=False
        engine = DataGenerator(spec, validate=False)
        assert engine is not None
