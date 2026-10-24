from datetime import datetime as dt, timedelta
import pandas as pd
from rand_engine.core._np_core import DATE_DIRECTIVES, DATE_SPLIT, float_lattice_bounds, width_beyond_double


class SparkCore:

  _INTEGER_DOMAINS = {
    "int8": (-128, 127, "int"),
    "int16": (-32768, 32767, "int"),
    "int32": (-2147483648, 2147483647, "int"),
    "int64": (-9223372036854775808, 9223372036854775807, "bigint"),
    "uint8": (0, 255, "int"),
    "uint16": (0, 65535, "int"),
    "uint32": (0, 4294967295, "bigint"),
    "int": (-2147483648, 2147483647, "int"),
    "integer": (-2147483648, 2147483647, "integer"),
    "bigint": (-9223372036854775808, 9223372036854775807, "bigint"),
    "long": (-9223372036854775808, 9223372036854775807, "long"),
  }

  @staticmethod
  def gen_uuid4(spark, F, df, col_name):
    return df.withColumn(col_name, F.expr("uuid()"))
  
  @staticmethod
  def gen_booleans(spark, F, df, col_name, true_prob=0.5):
    return df.withColumn(col_name, F.rand() < true_prob)
  

  @staticmethod
  def gen_ints(spark, F, df, col_name, min=0, max=10, int_type="long"):
    if int_type not in SparkCore._INTEGER_DOMAINS:
      raise ValueError(f"unsupported Spark integer type: {int_type!r}")
    type_min, type_max, spark_type = SparkCore._INTEGER_DOMAINS[int_type]
    if min > max: raise ValueError(f"min ({min}) must be <= max ({max})")
    if min < type_min or max > type_max: raise ValueError(f"bounds must fit the logical {int_type} domain")
    if width_beyond_double(max - min + 1): raise ValueError(f"width ({max - min + 1}) must be <= 2**53")
    return df.withColumn(col_name, (F.lit(min) + F.floor(F.rand() * (max - min + 1))).cast(spark_type))

  @staticmethod
  def gen_ints_zfilled(spark, F, df, col_name, length=10):
    max_value = 10 ** length - 1
    df = SparkCore.gen_ints(spark, F, df, col_name, min=0, max=max_value)
    return df.withColumn(col_name, F.lpad(F.col(col_name).cast("string"), length, "0"))

  @staticmethod
  def gen_floats(spark, F, df, col_name, min=0.0, max=10.0, decimals=2):
    if min > max: raise ValueError(f"min ({min}) must be <= max ({max})")
    low, high, fine = float_lattice_bounds(min, max, decimals)
    if fine: return df.withColumn(col_name, (F.rand() * (float(max) - float(min)) + float(min)).cast("double"))
    scale = F.lit(float(10 ** abs(decimals)))
    value = F.lit(low) + F.floor(F.rand() * (high - low + 1))
    return df.withColumn(col_name, (value / scale if decimals >= 0 else value * scale).cast("double"))

  @staticmethod
  def gen_floats_normal(spark, F, df, col_name, mean=0.0, std=1.0, decimals=2):
    return df.withColumn(col_name, F.round(F.randn() * float(std) + float(mean), decimals))

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
    timestamp_start, timestamp_end = ((d - dt(1970, 1, 1)) // timedelta(seconds=1) for d in (dt_start, dt_end))
    df = SparkCore.gen_ints(spark, F, df, col_name, min=timestamp_start, max=timestamp_end - 1)
    return df


  @staticmethod
  def gen_dates(spark, F, df, col_name, start="1970-01-01", end="2023-01-01", date_format="%Y-%m-%d"):

    df = SparkCore.gen_unix_timestamps(spark, F, df, col_name, start=start, end=end, date_format=date_format)
    # NTZ cast to string is TZ-free: "yyyy-MM-dd HH:mm:ss" (whole seconds, years 1970..9999), padded for %f
    utc_wall_clock = F.expr("TIMESTAMP_NTZ'1970-01-01 00:00:00'") + F.col(col_name) * F.expr("INTERVAL 1 SECOND")
    iso = F.concat(utc_wall_clock.cast("string"), F.lit(".000000"))
    span = dict(zip(DATE_DIRECTIVES, [(1, 4), (6, 2), (9, 2), (12, 2), (15, 2), (18, 2), (21, 6)]))
    tokens = [t for t in DATE_SPLIT.split(date_format) if t]
    return df.withColumn(col_name, F.concat(*[F.substring(iso, *span[t]) if t in span else F.lit(t) for t in tokens]))


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
