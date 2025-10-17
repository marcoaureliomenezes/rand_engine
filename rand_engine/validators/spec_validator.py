"""
Validador de especificações (specs) para o Rand Engine.

Este módulo fornece validação antecipada de specs antes da geração de dados,
permitindo detectar erros de configuração e fornecer feedback útil ao usuário.
"""

from typing import Dict, List, Any, Optional
from rand_engine.validators.exceptions import SpecValidationError


class SpecValidator:
    """
    Validador de especificações de dados para o Rand Engine.
    
    Esta classe verifica se uma spec está corretamente configurada antes
    da geração de dados, prevenindo erros em runtime e fornecendo
    mensagens descritivas sobre problemas encontrados.
    
    Suporta dois formatos para o campo 'method':
    - Callable direto: Core.gen_ints (formato antigo)
    - String identifier: "int" (formato novo, recomendado)
    
    Examples:
        >>> # Formato antigo (ainda suportado)
        >>> spec = {"age": {"method": Core.gen_ints, "kwargs": {"min": 0, "max": 100}}}
        >>> errors = SpecValidator.validate(spec)
        
        >>> # Formato novo (recomendado)
        >>> spec = {"age": {"method": "int", "kwargs": {"min": 0, "max": 100}}}
        >>> errors = SpecValidator.validate(spec)
        
        >>> # Levantar exceção se houver erros
        >>> SpecValidator.validate_and_raise(spec)
    """
    
    REQUIRED_KEYS = ["method"]
    OPTIONAL_KEYS = ["kwargs", "args", "transformers", "splitable", "cols", "sep", "pk"]
    MUTUALLY_EXCLUSIVE = [("kwargs", "args")]
    
    # Métodos válidos (identificadores string)
    VALID_METHOD_IDENTIFIERS = {
        "integers", "int_zfilled", "floats", "floats_normal",
        "distincts", "complex_distincts", "unix_timestamps", "unique_ids", "booleans"
    }
    
    @staticmethod
    def validate(spec: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Valida uma especificação e retorna lista de erros encontrados.
        
        Args:
            spec: Dicionário de especificação no formato:
                  {column_name: {method: ..., kwargs: ..., ...}}
        
        Returns:
            Lista de strings descrevendo os erros encontrados.
            Lista vazia se a spec estiver válida.
        
        Examples:
            >>> spec = {"age": {"method": "invalid"}}
            >>> errors = SpecValidator.validate(spec)
            >>> print(errors[0])
            Column 'age': 'method' must be callable, got <class 'str'>
        """
        errors = []
        
        # Validar que spec é um dicionário
        if not isinstance(spec, dict):
            errors.append(f"Spec must be a dict, got {type(spec).__name__}")
            return errors
        
        # Validar que spec não está vazio
        if len(spec) == 0:
            errors.append("Spec cannot be empty")
            return errors
        
        # Validar cada coluna
        for col_name, col_config in spec.items():
            errors.extend(SpecValidator._validate_column(col_name, col_config))
        
        return errors
    
    @staticmethod
    def _validate_column(col_name: str, col_config: Any) -> List[str]:
        """
        Valida configuração de uma coluna individual.
        
        Args:
            col_name: Nome da coluna
            col_config: Configuração da coluna
        
        Returns:
            Lista de erros encontrados para esta coluna
        """
        errors = []
        
        # Validar que col_config é um dicionário
        if not isinstance(col_config, dict):
            errors.append(
                f"Column '{col_name}': config must be a dict, got {type(col_config).__name__}"
            )
            return errors
        
        # Validar chaves obrigatórias
        for required_key in SpecValidator.REQUIRED_KEYS:
            if required_key not in col_config:
                errors.append(
                    f"Column '{col_name}': missing required key '{required_key}'"
                )
        
        # Se não tem 'method', não validar o resto
        if "method" not in col_config:
            return errors
        
        # Validar que method é callable OU string válida
        method_value = col_config["method"]
        
        if isinstance(method_value, str):
            # Formato novo: validar string identifier
            if method_value not in SpecValidator.VALID_METHOD_IDENTIFIERS:
                valid_methods = ", ".join(f"'{m}'" for m in sorted(SpecValidator.VALID_METHOD_IDENTIFIERS))
                errors.append(
                    f"Column '{col_name}': invalid method identifier '{method_value}'. "
                    f"Valid identifiers are: {valid_methods}"
                )
        elif not callable(method_value):
            # Não é string nem callable
            errors.append(
                f"Column '{col_name}': 'method' must be a valid string identifier or callable, "
                f"got {type(method_value).__name__}"
            )
        
        # Validar kwargs vs args (mutuamente exclusivos)
        has_kwargs = "kwargs" in col_config
        has_args = "args" in col_config
        
        if has_kwargs and has_args:
            errors.append(
                f"Column '{col_name}': cannot have both 'kwargs' and 'args', "
                f"use one or the other"
            )
        
        # Validar tipo de kwargs
        if has_kwargs:
            if not isinstance(col_config["kwargs"], dict):
                errors.append(
                    f"Column '{col_name}': 'kwargs' must be a dict, "
                    f"got {type(col_config['kwargs']).__name__}"
                )
        
        # Validar tipo de args
        if has_args:
            if not isinstance(col_config["args"], (list, tuple)):
                errors.append(
                    f"Column '{col_name}': 'args' must be a list or tuple, "
                    f"got {type(col_config['args']).__name__}"
                )
        
        # Validar transformers
        if "transformers" in col_config:
            if not isinstance(col_config["transformers"], list):
                errors.append(
                    f"Column '{col_name}': 'transformers' must be a list, "
                    f"got {type(col_config['transformers']).__name__}"
                )
            else:
                for i, transformer in enumerate(col_config["transformers"]):
                    if not callable(transformer):
                        errors.append(
                            f"Column '{col_name}': transformer at index {i} is not callable, "
                            f"got {type(transformer).__name__}"
                        )
        
        # Validar splitable pattern
        if col_config.get("splitable"):
            if "cols" not in col_config:
                errors.append(
                    f"Column '{col_name}': splitable=True requires 'cols' key"
                )
            elif not isinstance(col_config["cols"], list):
                errors.append(
                    f"Column '{col_name}': 'cols' must be a list, "
                    f"got {type(col_config['cols']).__name__}"
                )
            elif len(col_config["cols"]) == 0:
                errors.append(
                    f"Column '{col_name}': 'cols' cannot be empty when splitable=True"
                )
            
            # Validar sep se fornecido
            if "sep" in col_config:
                if not isinstance(col_config["sep"], str):
                    errors.append(
                        f"Column '{col_name}': 'sep' must be a string, "
                        f"got {type(col_config['sep']).__name__}"
                    )
        
        # Avisar sobre chaves desconhecidas (não gera erro, apenas warning)
        known_keys = set(SpecValidator.REQUIRED_KEYS + SpecValidator.OPTIONAL_KEYS)
        unknown_keys = set(col_config.keys()) - known_keys
        if unknown_keys:
            # Não adiciona como erro, apenas para awareness
            pass
        
        return errors
    
    @staticmethod
    def validate_and_raise(spec: Dict[str, Dict[str, Any]]) -> None:
        """
        Valida spec e levanta exceção se houver erros.
        
        Args:
            spec: Dicionário de especificação
        
        Raises:
            SpecValidationError: Se a spec contiver erros
        
        Examples:
            >>> spec = {"age": {"method": "invalid"}}
            >>> SpecValidator.validate_and_raise(spec)
            Traceback (most recent call last):
                ...
            SpecValidationError: Column 'age': 'method' must be callable...
        """
        errors = SpecValidator.validate(spec)
        if errors:
            error_message = "Spec validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise SpecValidationError(error_message)
    
    @staticmethod
    def validate_with_warnings(spec: Dict[str, Dict[str, Any]]) -> bool:
        """
        Valida spec e imprime erros se houver.
        
        Args:
            spec: Dicionário de especificação
        
        Returns:
            True se spec é válida, False caso contrário
        
        Examples:
            >>> spec = {"age": {"method": Core.gen_ints, "kwargs": {"min": 0, "max": 100}}}
            >>> if SpecValidator.validate_with_warnings(spec):
            ...     print("Spec is valid!")
            ✅ Spec is valid
            Spec is valid!
        """
        errors = SpecValidator.validate(spec)
        if errors:
            print("❌ Spec validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        print("✅ Spec is valid")
        return True
