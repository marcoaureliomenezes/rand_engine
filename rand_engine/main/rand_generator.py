from typing import List, Optional, Callable
import pandas as pd
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.exceptions import ColumnGenerationError, TransformerError


class RandGenerator:


  def __init__(self, random_spec, validate: bool = True):
    """
    Inicializa o gerador de dados randômicos.
    
    Args:
        random_spec: Dicionário de especificação de dados
        validate: Se True, valida a spec antes de inicializar (padrão: True)
    
    Raises:
        SpecValidationError: Se a spec for inválida e validate=True
    """
    if validate:
      SpecValidator.validate_and_raise(random_spec)
    self.random_spec = random_spec


  def generate_first_level(self, size: int):
    """
    Gera dados para todas as colunas conforme especificação.
    
    Args:
        size: Número de linhas a serem geradas
    
    Returns:
        DataFrame pandas com os dados gerados
    
    Raises:
        ColumnGenerationError: Se houver erro ao gerar dados para alguma coluna
    """
    dict_data = {}
    for k, v in self.random_spec.items():
      try:
        if "args" in v: dict_data[k] = v["method"](size , *v["args"]) 
        else: dict_data[k] = v["method"](size , **v.get("kwargs", {}))
      except Exception as e:
        raise ColumnGenerationError(
          f"Error generating column '{k}': {type(e).__name__}: {str(e)}"
        ) from e
    df_pandas = pd.DataFrame(dict_data)
    return df_pandas


  def apply_embedded_transformers(self, df):
    """
    Aplica transformers embutidos nas specs de cada coluna.
    
    Args:
        df: DataFrame pandas com dados gerados
    
    Returns:
        DataFrame com transformações aplicadas
    
    Raises:
        TransformerError: Se houver erro ao aplicar transformer
    """
    cols_with_transformers = {key: value["transformers"] for key, value in self.random_spec.items() if value.get("transformers")}
    for col, transformers in cols_with_transformers.items():
      for i, transformer in enumerate(transformers):
        try:
          df[col] = df[col].apply(transformer)
        except Exception as e:
          raise TransformerError(
            f"Error applying transformer {i} to column '{col}': {type(e).__name__}: {str(e)}"
          ) from e
    return df
  
  def apply_global_transformers(self, df, transformers: List[Optional[Callable]]):
    if transformers:
      if len(transformers) > 0: 
        for transformer in transformers:
          df = transformer(df)
    return df
 
  def handle_splitable(self, df):
    for key, value in self.random_spec.items():
      if value.get("splitable"):
        sep = value.get("sep", ";")   
        cols = value.get("cols")
        df[cols] = df[key].str.split(sep, expand=True)
        df.drop(columns=[key], inplace=True)
    return df