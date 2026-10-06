from functools import partial
from typing import Dict, List, Optional, Callable
import numpy as np
import pandas as pd
from rand_engine.validators.exceptions import ColumnGenerationError, TransformerError
from rand_engine.core._keys import Keys
from rand_engine.core._py_core import METHODS
from rand_engine.core._spark_core import SparkCore


class RandGenerator:


  def __init__(self, random_spec: Callable[[], Dict], validate: bool = True):
    # Avalia a spec usando lazy evaluation
    self.random_spec = random_spec


  def map_methods(self, rng: Optional[np.random.Generator] = None, offset: int = 0, key_seed: int = 0, column: str = ""):
    return {
      **{name: partial(method, rng=rng) for name, method in METHODS.items()},
      "pk": partial(Keys.gen_pk, offset=offset),
      "fk": partial(Keys.gen_fk, offset=offset, key_seed=key_seed, column=column),
    }
 
  def generate_first_level(self, size: int, rng: np.random.Generator, key_seed: int = 0, offset: int = 0):
    dict_data = {}
    for k, v in self.random_spec.items():
      columns = v.get("cols", [k])
      generator_method = self.map_methods(rng, offset, key_seed, k)[v["method"]]
      try:
        values = generator_method(size , **v.get("kwargs", {}))
        for i, col in enumerate(columns):
          dict_data[col] = values if len(columns) == 1 else [val[i] for val in values]
      except Exception as e:
        raise ColumnGenerationError(
          f"Error generating column '{k}': {type(e).__name__}: {str(e)}"
        ) from e
    df_pandas = pd.DataFrame(dict_data)
    return df_pandas


  def apply_embedded_transformers(self, df):
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
 