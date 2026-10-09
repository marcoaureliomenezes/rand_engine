from functools import partial
from numbers import Number
from typing import Dict, List, Optional, Callable
import numpy as np
import pandas as pd
from pandas.api.types import (
  infer_dtype,
  is_bool_dtype,
  is_datetime64_any_dtype,
  is_float_dtype,
  is_integer_dtype,
  is_object_dtype,
  is_string_dtype,
)
from rand_engine.validators.exceptions import ColumnGenerationError, RandEngineError, TransformerError
from rand_engine.core._keys import Keys
from rand_engine.core._py_core import METHODS


class RandGenerator:


  def __init__(self, random_spec: Dict):
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
  

  def apply_global_transformers(self, df, transformers: List[Callable]):
    for transformer in transformers:
      df = transformer(df)
    return df


  @staticmethod
  def _object_values_are_compatible(series: pd.Series, values: list) -> bool:
    candidates = [value for value in values if not pd.isna(value)]
    source_kind = infer_dtype(series, skipna=True)
    if source_kind == "empty" or not candidates:
      return True
    candidate_kind = infer_dtype(candidates, skipna=True)
    return source_kind in {"mixed", "mixed-integer"} or source_kind == candidate_kind


  @staticmethod
  def _scalar_preserves_dtype(value, dtype) -> bool:
    if is_integer_dtype(dtype):
      if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        return False
      bounds = np.iinfo(dtype.numpy_dtype if hasattr(dtype, "numpy_dtype") else dtype)
      return bounds.min <= int(value) <= bounds.max
    if is_bool_dtype(dtype):
      return isinstance(value, (bool, np.bool_))
    if is_float_dtype(dtype):
      if isinstance(value, (bool, np.bool_)):
        return False
      numpy_dtype = dtype.numpy_dtype if hasattr(dtype, "numpy_dtype") else dtype
      try:
        converted = np.asarray([value], dtype=numpy_dtype)[0]
      except (TypeError, ValueError, OverflowError):
        return False
      if not isinstance(value, Number) and not pd.isna(value):
        return False
      return (pd.isna(value) and pd.isna(converted)) or converted == value
    if is_datetime64_any_dtype(dtype):
      if isinstance(value, str):
        return False
      try:
        converted = pd.array([value], dtype=dtype)[0]
      except (TypeError, ValueError, OverflowError):
        return False
      return (pd.isna(value) and pd.isna(converted)) or pd.Timestamp(value) == converted
    if is_string_dtype(dtype):
      return pd.isna(value) or isinstance(value, str)
    try:
      converted = pd.array([value], dtype=dtype)[0]
    except (TypeError, ValueError, OverflowError):
      return False
    return (pd.isna(value) and pd.isna(converted)) or converted == value


  @classmethod
  def _anomaly_values_are_compatible(cls, series: pd.Series, values: list) -> bool:
    if is_object_dtype(series.dtype):
      return cls._object_values_are_compatible(series, values)
    return all(cls._scalar_preserves_dtype(value, series.dtype) for value in values)


  def _modifier_targets(self) -> list[tuple[str, dict]]:
    targets = []
    for spec_key, config in self.random_spec.items():
      anomaly_rate = config.get("anomaly_rate", 0)
      null_rate = config.get("null_rate", 0)
      if not anomaly_rate and not null_rate:
        continue
      aliases = config.get("cols")
      targets.append((aliases[0] if aliases else spec_key, config))
    return targets


  def _validate_modifiers(self, df: pd.DataFrame, targets: list[tuple[str, dict]]):
    for column, config in targets:
      anomaly_rate = config.get("anomaly_rate", 0)
      if column not in df:
        raise RandEngineError(f"modifier column '{column}' is missing after transformers")
      if anomaly_rate and not self._anomaly_values_are_compatible(df[column], config["anomaly_values"]):
        raise RandEngineError(f"column '{column}' anomaly values cannot preserve dtype {df[column].dtype}")


  @staticmethod
  def _coerce_anomaly_values(series: pd.Series, values: np.ndarray):
    if is_object_dtype(series.dtype):
      return np.asarray(values, dtype=object)
    return pd.array(values, dtype=series.dtype)


  @staticmethod
  def _assign_nulls(series: pd.Series, mask: np.ndarray) -> pd.Series:
    if is_object_dtype(series.dtype) or is_string_dtype(series.dtype):
      return series.astype(object).mask(mask, None)
    if is_integer_dtype(series.dtype):
      nullable = str(series.dtype).replace("uint", "UInt").replace("int", "Int")
      return series.astype(nullable).mask(mask, pd.NA)
    if is_bool_dtype(series.dtype):
      return series.astype("boolean").mask(mask, pd.NA)
    if is_datetime64_any_dtype(series.dtype):
      return series.mask(mask, pd.NaT)
    if is_float_dtype(series.dtype):
      return series.mask(mask, np.nan)
    return series.mask(mask, None)


  def apply_modifiers(self, df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    targets = self._modifier_targets()
    self._validate_modifiers(df, targets)
    for column, config in targets:
      anomaly_rate = config.get("anomaly_rate", 0)
      null_rate = config.get("null_rate", 0)
      series = df[column]
      if anomaly_rate:
        anomaly_mask = rng.random(len(series)) < anomaly_rate
        pool = np.asarray(config["anomaly_values"], dtype=object)
        selected = rng.choice(pool, size=int(anomaly_mask.sum()))
        series = series.copy()
        series.iloc[np.flatnonzero(anomaly_mask)] = self._coerce_anomaly_values(series, selected)
      if null_rate:
        null_mask = rng.random(len(series)) < null_rate
        series = self._assign_nulls(series, null_mask)
      df[column] = series
    return df
