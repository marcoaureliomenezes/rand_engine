from rand_engine.core._spark_core import SparkCore



class SparkGenerator:

  def __init__(self, spark, F, metadata):
    self.spark = spark
    self.F = F
    self.metadata = metadata
    _size = 0

  def map_methods(self):
    return {
      "integers": SparkCore.gen_ints,
      "zint": SparkCore.gen_ints_zfill,
      "floats": SparkCore.gen_floats,
      "floats_normal": SparkCore.gen_floats_normal,
      "distincts": SparkCore.gen_distincts,
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