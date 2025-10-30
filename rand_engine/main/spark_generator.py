from rand_engine.core._spark_core import SparkCore
from rand_engine.validators.spark_spec_validator import SparkSpecValidator



class SparkGenerator:

  def __init__(self, spark, F, metadata, validate: bool = True):
    """
    Initialize SparkGenerator with PySpark session, functions, and metadata.
    
    Args:
        spark: SparkSession instance
        F: pyspark.sql.functions module
        metadata: Dictionary mapping column names to generation specs
        validate: If True, validates metadata on initialization (default: True)
    
    Raises:
        SpecValidationError: If validate=True and metadata is invalid
    """
    if validate:
      SparkSpecValidator.validate_and_raise(metadata)
    
    self.spark = spark
    self.F = F
    self.metadata = metadata
    _size = 0

  def map_methods(self):
    return {
      "integers": SparkCore.gen_ints,
      "zint": SparkCore.gen_ints_zfilled,
      "floats": SparkCore.gen_floats,
      "floats_normal": SparkCore.gen_floats_normal,
      "distincts": SparkCore.gen_distincts,
      "distincts_prop": SparkCore.gen_distincts_prop,
      "booleans": SparkCore.gen_booleans,
      "dates": SparkCore.gen_dates,
      "uuid4": SparkCore.gen_uuid4
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
    return dataframe