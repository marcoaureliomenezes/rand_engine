from rand_engine.core._spark_core import SparkCore
from rand_engine.validators.common_validator import CommonValidator



class SparkGenerator:

  def __init__(self, spark, F, metadata):
    """
    Initialize SparkGenerator with PySpark session, functions, and metadata.
    
    Args:
        spark: SparkSession instance
        F: pyspark.sql.functions module
        metadata: Dictionary mapping column names to generation specs
    
    Raises:
        SpecValidationError: If metadata is invalid (validation is always performed)
    """
    # Validação obrigatória - sempre executada
    CommonValidator.validate_spark_and_raise(metadata)
    
    self.spark = spark
    self.F = F
    self.metadata = metadata
    _size = 0

  def map_methods(self):
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
    self._size = size
    return self


  def get_df(self):
    mapped_methods = self.map_methods()
    dataframe = self.spark.range(self._size)
    for k, v in self.metadata.items():
      generator_method = mapped_methods[v["method"]]
      dataframe = generator_method(self.spark, F=self.F, df=dataframe, col_name=k, **v["kwargs"])
    # Remove the technical 'id' column from spark.range() only if not in spec
    if "id" not in self.metadata:
      return dataframe.drop("id")
    return dataframe