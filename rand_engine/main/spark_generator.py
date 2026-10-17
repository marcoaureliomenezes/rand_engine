"""Spark generation facade: one RandSpec, one SparkSession, one DataFrame."""
import numpy as np
import pandas as pd
import pyarrow as pa

from rand_engine.core._keys import Keys
from rand_engine.core._spark_core import SparkCore
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.exceptions import RandEngineError
from rand_engine.validators.method_specs import METHOD_CATALOG



class SparkGenerator:
  """
  Generate a PySpark DataFrame from a RandSpec.

  Parameters
  ----------
  spark : pyspark.sql.SparkSession
      Session that builds the DataFrame.
  F : module
      The ``pyspark.sql.functions`` module.
  metadata : dict
      RandSpec mapping each column to ``{"method": ..., "kwargs": ...}``. Validated at construction.

  Raises
  ------
  SpecValidationError
      If ``metadata`` is invalid.

  Examples
  --------
  >>> from pyspark.sql import SparkSession, functions as F  # doctest: +SKIP
  >>> from rand_engine import SparkGenerator  # doctest: +SKIP
  >>> spark = SparkSession.builder.getOrCreate()  # doctest: +SKIP
  >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
  >>> SparkGenerator(spark, F, spec).size(100).get_df().count()  # doctest: +SKIP
  100
  """

  def __init__(self, spark, F, metadata, seed=None):
    # Validação obrigatória - sempre executada
    errors = CommonValidator.validate_spark_spec(metadata)
    key_metadata = {}
    if isinstance(metadata, dict):
      key_metadata = {
        column: config for column, config in metadata.items()
        if isinstance(config, dict) and config.get("method") in ("pk", "fk")
      }
    key_errors = AdvancedValidator.validate(key_metadata) if key_metadata else []
    errors.extend(error for error in key_errors if error not in errors)
    if errors:
      CommonValidator._raise(errors, "SPARKGENERATOR")
    
    self.spark = spark
    self.F = F
    self.metadata = metadata
    self._key_metadata = key_metadata
    if key_metadata:
      seed_sequence = np.random.SeedSequence(seed)
      self._key_seed = int(seed_sequence.generate_state(1)[0])
    self._size = None

  def map_methods(self):
    """
    Return the RandSpec method names mapped to their Spark generator functions.

    Returns
    -------
    dict
        Method name to ``SparkCore`` generator function.

    Examples
    --------
    >>> from pyspark.sql import SparkSession, functions as F  # doctest: +SKIP
    >>> from rand_engine import SparkGenerator  # doctest: +SKIP
    >>> spark = SparkSession.builder.getOrCreate()  # doctest: +SKIP
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}  # doctest: +SKIP
    >>> "integers" in SparkGenerator(spark, F, spec).map_methods()  # doctest: +SKIP
    True
    """
    return {
      "integers": SparkCore.gen_ints,
      "int_zfilled": SparkCore.gen_ints_zfilled,
      "floats": SparkCore.gen_floats,
      "floats_normal": SparkCore.gen_floats_normal,
      "distincts": SparkCore.gen_distincts,
      "distincts_prop": SparkCore.gen_distincts_prop,
      "unix_timestamps": SparkCore.gen_unix_timestamps,
      "uuid4": SparkCore.gen_uuid4,
      "booleans": SparkCore.gen_booleans,
      "dates": SparkCore.gen_dates,
      "distincts_map": SparkCore.gen_distincts_map,
      "distincts_multi_map": SparkCore.gen_distincts_multi_map,
      "distincts_map_prop": SparkCore.gen_distincts_map_prop,
      "complex_distincts": SparkCore.gen_complex_distincts,
    }
 
  def size(self, size):
    """
    Set the number of rows of the DataFrame and return this generator.

    Parameters
    ----------
    size : int
        Rows built by ``get_df``.

    Returns
    -------
    SparkGenerator
        This generator, for chaining.

    Examples
    --------
    >>> from pyspark.sql import SparkSession, functions as F  # doctest: +SKIP
    >>> from rand_engine import SparkGenerator  # doctest: +SKIP
    >>> spark = SparkSession.builder.getOrCreate()  # doctest: +SKIP
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}  # doctest: +SKIP
    >>> gen = SparkGenerator(spark, F, spec).size(100)  # doctest: +SKIP
    """
    self._size = size
    return self


  def get_df(self):
    """
    Build the Spark DataFrame of ``size`` rows generated from the metadata.

    Returns
    -------
    pyspark.sql.DataFrame
        One column per metadata key; the technical ``id`` column is dropped unless the metadata declares ``id``.

    Raises
    ------
    RandEngineError
        If ``size`` was not set.

    Examples
    --------
    >>> from pyspark.sql import SparkSession, functions as F  # doctest: +SKIP
    >>> from rand_engine import SparkGenerator  # doctest: +SKIP
    >>> spark = SparkSession.builder.getOrCreate()  # doctest: +SKIP
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> SparkGenerator(spark, F, spec).size(100).get_df().count()  # doctest: +SKIP
    100
    """
    if self._size is None:
      raise RandEngineError("size not set: call .size(n) before get_df()")
    mapped_methods = self.map_methods()
    dataframe = self.spark.range(self._size)
    source_index = next(
      f"__rand_engine_source_index_{index}"
      for index in range(len(self.metadata) + 1)
      if f"__rand_engine_source_index_{index}" not in self.metadata
    )
    if self._key_metadata:
      dataframe = dataframe.withColumn(source_index, self.F.col("id"))
    for k, v in self.metadata.items():
      if v["method"] in ("pk", "fk"):
        continue
      generator_method = mapped_methods[v["method"]]
      dataframe = generator_method(self.spark, F=self.F, df=dataframe, col_name=k, **v.get("kwargs", {}))
    if self._key_metadata:
      if "id" in self._key_metadata:
        dataframe = dataframe.drop("id")
      dataframe = self._add_key_columns(dataframe, source_index)
      return dataframe.select(*(
        self.F.col(f"`{column.replace('`', '``')}`").alias(column)
        for column in self.metadata
      ))
    # Remove the technical 'id' column from spark.range() only if not in spec
    if "id" not in self.metadata:
      return dataframe.drop("id")
    return dataframe


  def _add_key_columns(self, dataframe, source_index):
    """Build stateless key columns from the source indexes carried by Spark."""
    from pyspark.sql.types import LongType, StringType, StructField, StructType

    key_metadata = self._key_metadata
    key_seed = self._key_seed
    for column, config in key_metadata.items():
      if config["method"] != "fk" or self._size == 0:
        continue
      kwargs = config.get("kwargs", {})
      born_before = kwargs.get("born_before")
      if born_before is None:
        continue
      eligible = Keys._eligible_parent_counts(
        np.asarray([0], dtype=np.int64), kwargs["parent_size"], born_before
      )
      if not eligible[0]:
        raise RandEngineError(f"fk column '{column}' has a child with no eligible parent")

    def key_field(column, config):
      kwargs = config.get("kwargs", {})
      arrow_type = METHOD_CATALOG[config["method"]].arrow_types(kwargs)[0]
      return StructField(column, StringType() if pa.types.is_string(arrow_type) else LongType(), False)

    schema = StructType([
      StructField(source_index, LongType(), False),
      *(key_field(column, config) for column, config in key_metadata.items()),
    ])

    def generate_keys(batches):
      for batch in batches:
        indexes = batch[source_index].to_numpy(dtype=np.int64)
        values = {source_index: indexes}
        for column, config in key_metadata.items():
          kwargs = config.get("kwargs", {})
          if config["method"] == "pk":
            values[column] = Keys._pk_at(
              indexes, int(indexes.min()) if indexes.size else 0,
              int(indexes.max()) if indexes.size else -1, **kwargs
            )
          else:
            values[column] = Keys._fk_at(
              indexes, kwargs["parent"], kwargs["parent_size"], kwargs.get("skew", 0),
              key_seed, column, kwargs.get("born_before")
            )
        yield pd.DataFrame(values)

    keys = dataframe.select(source_index).mapInPandas(generate_keys, schema)
    return dataframe.join(keys, source_index)
