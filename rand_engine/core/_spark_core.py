from datetime import datetime as dt
import pandas as pd


class SparkCore:

  @staticmethod
  def gen_uuid4(spark, F, df, col_name):
    return df.withColumn(col_name, F.expr("uuid()"))
  
  @staticmethod
  def gen_booleans(spark, F, df, col_name, true_prob=0.5):
    # Support both 'true_prob' and 'prob_true' for backwards compatibility
    return df.withColumn(col_name, F.rand() < true_prob)
  

  @staticmethod
  def gen_ints(spark, F, df, col_name, min=0, max=10, int_type="long"):
    """
    Generate random integers.
    
    Args:
        int_type: Integer type specification
                 - Accepts Spark types: "int", "bigint", "long", "integer"
                 - Accepts NPCore types: "int8", "int16", "int32", "int64", "uint8", "uint16", "uint32", "uint64"
                   (automatically mapped to Spark equivalents)
    """
    # Map NPCore int_type values to Spark equivalents
    np_to_spark_mapping = {
        "int8": "int",
        "int16": "int", 
        "int32": "int",
        "int64": "bigint",
        "uint8": "int",
        "uint16": "int",
        "uint32": "bigint",
        "uint64": "bigint"
    }
    
    # Convert NPCore types to Spark types if needed
    spark_type = np_to_spark_mapping.get(int_type, int_type)
    
    allowed_integers = ["int", "bigint", "long", "integer"]
    assert spark_type in allowed_integers, f"int_type must be one of {allowed_integers} or NPCore types {list(np_to_spark_mapping.keys())}"
    return df.withColumn(col_name, (F.rand() * (max - min) + min).cast(spark_type))

  @staticmethod
  def gen_ints_zfilled(spark, F, df, col_name, length=10):
    max_value = 10 ** length - 1
    df = SparkCore.gen_ints(spark, F, df, col_name, min=0, max=max_value)
    return df.withColumn(col_name, F.lpad(F.col(col_name).cast("string"), length, "0"))

  @staticmethod
  def gen_floats(spark, F, df, col_name, min=0.0, max=10.0, decimals=2):
    return df.withColumn(col_name, F.round(F.rand() * (max - min) + min, decimals))

  @staticmethod
  def gen_floats_normal(spark, F, df, col_name, mean=0.0, std=1.0, decimals=2):
    return df.withColumn(col_name, F.round(F.randn() * std + mean, decimals))

  @staticmethod
  def gen_distincts(spark, F, df, col_name, distincts=[]):
    values = distincts if distincts else []
    aux_col = f"aux_col{col_name}"
    df_pd = pd.DataFrame(values, columns=[col_name])
    df_pd[aux_col] = range(len(values))
    df_spark = spark.createDataFrame(df_pd)
    df_columns = df.columns
    df_result = df.withColumn(aux_col, (F.rand() * (len(values) - 0) + 0).cast("int"))
    return (
      df_result.alias("a").join(F.broadcast(df_spark).alias("b"), on=aux_col, how="left")
      .select(*df_columns, f"b.{col_name}"))
    

  @staticmethod
  def gen_distincts_prop(spark, F, df, col_name, distincts={}):
    distincts_prop = [ key for key, value in distincts.items() for i in range(value) ]
    return SparkCore.gen_distincts(spark, F, df, col_name, distincts=distincts_prop)


  @staticmethod
  def gen_unix_timestamps(
    spark, F, df, col_name, 
    start="1970-01-01", end="2023-01-01", date_format="%Y-%m-%d"):
    """
    Generate Unix timestamps.
    
    Args:
        date_format: Date format string for parsing start/end dates
    
    Note: Unified API parameter name matches NPCore.gen_unix_timestamps().
    """
    dt_start, dt_end = dt.strptime(start, date_format), dt.strptime(end, date_format)
    if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
    timestamp_start, timestamp_end = int(dt_start.timestamp()), int(dt_end.timestamp())
    df = SparkCore.gen_ints(spark, F, df, col_name, min=timestamp_start, max=timestamp_end)
    return df


  @staticmethod
  def gen_dates(spark, F, df, col_name, start="1970-01-01", end="2023-01-01", date_format="%Y-%m-%d"):

    # Support legacy parameter names for backwards compatibility

    map_formats = {"%Y": "yyyy", "%m": "MM", "%d": "dd","%H": "HH", "%M": "mm", "%S": "ss", "%f": "SSSSSS"}
    spark_format = date_format
    for k, v in map_formats.items():
      spark_format = spark_format.replace(k, v)
    df = SparkCore.gen_unix_timestamps(spark, F, df, col_name, start=start, end=end, date_format=date_format)
    return df.withColumn(col_name,
      F.date_format(F.from_unixtime(F.col(col_name), spark_format).cast("timestamp"), spark_format))


  @staticmethod
  def gen_distincts_map(spark, F, df, col_name, **kwargs):
    """
    Dummy implementation for API compatibility with DataGenerator.
    Returns NULL values. Full implementation pending.
    """
    return df.withColumn(col_name, F.lit(None).cast("string"))


  @staticmethod
  def gen_distincts_multi_map(spark, F, df, col_name, **kwargs):
    """
    Dummy implementation for API compatibility with DataGenerator.
    Returns NULL values. Full implementation pending.
    """
    return df.withColumn(col_name, F.lit(None).cast("string"))


  @staticmethod
  def gen_distincts_map_prop(spark, F, df, col_name, **kwargs):
    """
    Dummy implementation for API compatibility with DataGenerator.
    Returns NULL values. Full implementation pending.
    """
    return df.withColumn(col_name, F.lit(None).cast("string"))


  @staticmethod
  def gen_complex_distincts(spark, F, df, col_name, **kwargs):
    """
    Dummy implementation for API compatibility with DataGenerator.
    Returns NULL values. Full implementation pending.
    """
    return df.withColumn(col_name, F.lit(None).cast("string"))