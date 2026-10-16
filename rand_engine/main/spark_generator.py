"""Spark generation facade: one RandSpec, one SparkSession, one DataFrame."""
from rand_engine.core._spark_core import SparkCore
from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.exceptions import RandEngineError



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

  def __init__(self, spark, F, metadata):
    # Validação obrigatória - sempre executada
    CommonValidator.validate_spark_and_raise(metadata)
    
    self.spark = spark
    self.F = F
    self.metadata = metadata
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
    for k, v in self.metadata.items():
      generator_method = mapped_methods[v["method"]]
      dataframe = generator_method(self.spark, F=self.F, df=dataframe, col_name=k, **v.get("kwargs", {}))
    # Remove the technical 'id' column from spark.range() only if not in spec
    if "id" not in self.metadata:
      return dataframe.drop("id")
    return dataframe