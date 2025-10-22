from typing import Dict, List, Optional, Callable
import pandas as pd
from rand_engine.integrations._duckdb_handler import DuckDBHandler
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.exceptions import ColumnGenerationError, TransformerError
from rand_engine.core._np_core import NPCore
from rand_engine.core._py_core import PyCore
from rand_engine.core._spark_core import SparkCore


class RandGenerator:


  def __init__(self, random_spec: Callable[[], Dict], validate: bool = True):
    # Avalia a spec usando lazy evaluation
    self.random_spec = random_spec


  def map_methods(self):
    return {
      "integers": NPCore.gen_ints,
      "int_zfilled": NPCore.gen_ints_zfilled,
      "floats": NPCore.gen_floats,
      "floats_normal": NPCore.gen_floats_normal,
      "distincts": NPCore.gen_distincts,
      "distincts_prop": NPCore.gen_distincts_prop,
      "distincts_map": PyCore.gen_distincts_map,
      "distincts_multi_map": PyCore.gen_distincts_multi_map,
      "distincts_map_prop": PyCore.gen_distincts_map_prop,
      "complex_distincts": PyCore.gen_complex_distincts,
      "unix_timestamps": NPCore.gen_unix_timestamps,
      "unique_ids": NPCore.gen_unique_identifiers,
      "booleans": NPCore.gen_bools,
    }
 
  def generate_first_level(self, size: int):
    dict_data = {}
    mapped_methods = self.map_methods()
    for k, v in self.random_spec.items():
      columns = v.get("cols", [k])
      generator_method = mapped_methods[v["method"]]
      try:
        if "args" in v: values = generator_method(size , *v["args"])
        else: values = generator_method(size , **v.get("kwargs", {}))
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
 