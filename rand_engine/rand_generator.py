from typing import List, Optional, Callable
import pandas as pd


class RandGenerator:


  def __init__(self, random_spec):
    self.random_spec = random_spec


  def generate_first_level(self, size: int):
    dict_data = {}
    for k, v in self.random_spec.items():
      try:
        if "args" in v: dict_data[k] = v["method"](size , *v["args"]) 
        else: dict_data[k] = v["method"](size , **v.get("kwargs", {}))
      except Exception as e:
        raise Exception(f"Error generating data for column '{k}': {e}")
    df_pandas = pd.DataFrame(dict_data)
    return df_pandas


  def apply_embedded_transformers(self, df):

    cols_with_transformers = {key: value["transformers"] for key, value in self.random_spec.items() if value.get("transformers")}
    for col, transformers in cols_with_transformers.items():
      for transformer in transformers:
        df[col] = df[col].apply(transformer)
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