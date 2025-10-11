"""
Exceções customizadas para o Rand Engine.

Este módulo define exceções específicas para melhorar a experiência
de debugging e fornecer mensagens de erro mais descritivas.
"""


class RandEngineError(Exception):
    """Classe base para todas as exceções do Rand Engine."""
    pass


class SpecValidationError(RandEngineError):
    """
    Exceção levantada quando uma especificação (spec) é inválida.
    
    Esta exceção é levantada durante a validação da spec antes da
    geração de dados, permitindo detectar erros de configuração
    antes do runtime.
    
    Examples:
        >>> spec = {"age": {"method": "invalid"}}
        >>> DataGenerator(spec)
        SpecValidationError: Column 'age': 'method' must be callable, got <class 'str'>
    """
    pass


class ColumnGenerationError(RandEngineError):
    """
    Exceção levantada quando há erro ao gerar dados para uma coluna.
    
    Esta exceção encapsula erros que ocorrem durante a execução
    do método de geração, fornecendo contexto sobre qual coluna falhou.
    
    Examples:
        >>> spec = {"age": {"method": Core.gen_ints, "kwargs": {"min": "invalid"}}}
        >>> DataGenerator(spec).generate_pandas_df(100)
        ColumnGenerationError: Error generating column 'age': ...
    """
    pass


class TransformerError(RandEngineError):
    """
    Exceção levantada quando há erro ao aplicar transformer.
    
    Examples:
        >>> spec = {"age": {"method": Core.gen_ints, "kwargs": {...}, "transformers": [invalid_func]}}
        TransformerError: Error applying transformer to column 'age': ...
    """
    pass


class FileWriterError(RandEngineError):
    """
    Exceção levantada quando há erro ao escrever dados em arquivo.
    
    Examples:
        >>> engine.write(1000).format("invalid_format").load("path")
        FileWriterError: Unsupported format 'invalid_format'
    """
    pass
