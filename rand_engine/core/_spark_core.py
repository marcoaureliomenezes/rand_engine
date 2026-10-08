from datetime import datetime as dt, timezone
import pandas as pd
from rand_engine.core._np_core import DATE_DIRECTIVES, DATE_SPLIT, float_lattice_bounds


class SparkCore:

  _CHUNK_BASE = 10 ** 9

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
  def _fold_decimal_limb(F, high, low, width, precision):
    base = F.lit(str(2 ** 32)).cast("decimal(10,0)")
    modulus = F.lit(str(width)).cast("decimal(20,0)")
    combined = high * base + low
    if precision == 32:
      combined = combined.cast("decimal(32,0)")
    return F.pmod(combined, modulus).cast(f"decimal({precision},0)")

  @staticmethod
  def _integer_chunks(value, length):
    chunks = []
    while value:
      value, chunk = divmod(value, SparkCore._CHUNK_BASE)
      chunks.append(chunk)
    chunks = list(reversed(chunks or [0]))
    return [0] * (length - len(chunks)) + chunks

  @staticmethod
  def _chunk_literal(F, value, length):
    return F.array(*[
      F.lit(chunk).cast("long")
      for chunk in SparkCore._integer_chunks(value, length)
    ])

  @staticmethod
  def _add_chunk_arrays(F, left, right):
    base = F.lit(SparkCore._CHUNK_BASE).cast("long")
    indices = F.reverse(F.sequence(F.lit(1), F.size(left)))
    initial = F.struct(
      F.array().cast("array<long>").alias("digits"),
      F.lit(0).cast("long").alias("carry"),
    )

    def add_digit(state, index):
      total = F.element_at(left, index) + F.element_at(right, index) + state["carry"]
      return F.struct(
        F.concat(F.array(F.pmod(total, base).cast("long")), state["digits"]).alias("digits"),
        F.floor(total / base).cast("long").alias("carry"),
      )

    return F.aggregate(indices, initial, add_digit)["digits"]

  @staticmethod
  def _subtract_chunk_arrays(F, left, right):
    base = F.lit(SparkCore._CHUNK_BASE).cast("long")
    indices = F.reverse(F.sequence(F.lit(1), F.size(left)))
    initial = F.struct(
      F.array().cast("array<long>").alias("digits"),
      F.lit(0).cast("long").alias("borrow"),
    )

    def subtract_digit(state, index):
      difference = F.element_at(left, index) - F.element_at(right, index) - state["borrow"]
      return F.struct(
        F.concat(F.array(F.pmod(difference, base).cast("long")), state["digits"]).alias("digits"),
        F.when(difference < 0, F.lit(1)).otherwise(F.lit(0)).cast("long").alias("borrow"),
      )

    return F.aggregate(indices, initial, subtract_digit)["digits"]

  @staticmethod
  def _double_add_bit(F, digits, bit):
    base = F.lit(SparkCore._CHUNK_BASE).cast("long")
    indices = F.reverse(F.sequence(F.lit(1), F.size(digits)))
    initial = F.struct(
      F.array().cast("array<long>").alias("digits"),
      bit.cast("long").alias("carry"),
    )

    def double_digit(state, index):
      total = F.element_at(digits, index) * F.lit(2) + state["carry"]
      return F.struct(
        F.concat(F.array(F.pmod(total, base).cast("long")), state["digits"]).alias("digits"),
        F.floor(total / base).cast("long").alias("carry"),
      )

    return F.aggregate(indices, initial, double_digit)["digits"]

  @staticmethod
  def _fold_bits_mod(F, bits, width):
    zero = F.transform(width, lambda _chunk: F.lit(0).cast("long"))

    def fold_bit(remainder, bit):
      candidate = SparkCore._double_add_bit(F, remainder, bit)
      return F.when(
        candidate >= width,
        SparkCore._subtract_chunk_arrays(F, candidate, width),
      ).otherwise(candidate)

    return F.aggregate(bits, zero, fold_bit)

  @staticmethod
  def _offset_chunks(F, residue, lower, length):
    lower_chunks = SparkCore._chunk_literal(F, abs(lower), length)
    if lower >= 0:
      return F.struct(
        SparkCore._add_chunk_arrays(F, lower_chunks, residue).alias("magnitude"),
        F.lit(False).alias("negative"),
      )

    crosses_zero = residue >= lower_chunks
    return F.struct(
      F.when(
        crosses_zero,
        SparkCore._subtract_chunk_arrays(F, residue, lower_chunks),
      ).otherwise(
        SparkCore._subtract_chunk_arrays(F, lower_chunks, residue)
      ).alias("magnitude"),
      (~crosses_zero).alias("negative"),
    )

  @staticmethod
  def _float_lattice_expression(F, lower, upper, decimals):
    width = upper - lower + 1
    length = max(
      len(SparkCore._integer_chunks(width, 0)),
      len(SparkCore._integer_chunks(abs(lower), 0)),
      len(SparkCore._integer_chunks(abs(upper), 0)),
    ) + 1
    width_chunks = SparkCore._chunk_literal(F, width, length)

    if width == 1:
      residue = SparkCore._chunk_literal(F, 0, length)
    else:
      limb_count = (width.bit_length() + 31) // 32 + 2
      limbs = [F.floor(F.rand() * F.lit(2 ** 32)).cast("long") for _ in range(limb_count)]
      bits = F.array(*[
        F.getbit(limb, F.lit(position)).cast("long")
        for limb in limbs
        for position in range(31, -1, -1)
      ])
      residue = SparkCore._fold_bits_mod(F, bits, width_chunks)

    offset = SparkCore._offset_chunks(F, residue, lower, length)
    magnitude = offset["magnitude"]
    negative = offset["negative"]

    padded = F.transform(
      magnitude,
      lambda chunk: F.lpad(chunk.cast("string"), 9, "0"),
    )
    unsigned = F.regexp_replace(F.array_join(padded, ""), r"^0+(?!$)", "")
    signed = F.when(
      negative & (unsigned != "0"),
      F.concat(F.lit("-"), unsigned),
    ).otherwise(unsigned)
    return F.concat(signed, F.lit(f"e{-decimals}")).cast("double")

  @staticmethod
  def gen_uuid4(spark, F, df, col_name):
    return df.withColumn(col_name, F.expr("uuid()"))
  
  @staticmethod
  def gen_booleans(spark, F, df, col_name, true_prob=0.5):
    return df.withColumn(col_name, F.rand() < true_prob)
  

  @staticmethod
  def gen_ints(spark, F, df, col_name, min=0, max=10, int_type="long"):
    """Generate exact inclusive integers in the requested logical domain."""
    if int_type not in SparkCore._INTEGER_DOMAINS:
      raise ValueError(f"unsupported Spark integer type: {int_type!r}")
    if type(min) is not int or type(max) is not int:
      raise ValueError("integer bounds must be integers")
    if min > max:
      raise ValueError(f"min ({min}) must be <= max ({max})")

    type_min, type_max, spark_type = SparkCore._INTEGER_DOMAINS[int_type]
    if min < type_min or max > type_max:
      raise ValueError(f"bounds must fit the logical {int_type} domain")

    if min == max:
      value = F.lit(str(min)).cast(spark_type)
      return df.withColumn(col_name, value)

    width = max - min + 1
    limbs = [
      F.floor(F.rand() * F.lit(2 ** 32)).cast("decimal(10,0)")
      for _ in range(3)
    ]
    high_mod = SparkCore._fold_decimal_limb(
      F, limbs[0], limbs[1], width, precision=20
    )
    word_mod = SparkCore._fold_decimal_limb(
      F, high_mod, limbs[2], width, precision=32
    )
    value = F.lit(str(min)).cast("decimal(20,0)") + word_mod
    return df.withColumn(col_name, value.cast(spark_type))

  @staticmethod
  def gen_ints_zfilled(spark, F, df, col_name, length=10):
    max_value = 10 ** length - 1
    df = SparkCore.gen_ints(spark, F, df, col_name, min=0, max=max_value)
    return df.withColumn(col_name, F.lpad(F.col(col_name).cast("string"), length, "0"))

  @staticmethod
  def gen_floats(spark, F, df, col_name, min=0.0, max=10.0, decimals=2):
    if min > max:
      raise ValueError(f"min ({min}) must be <= max ({max})")
    lower, upper, _scale = float_lattice_bounds(min, max, decimals)
    value = SparkCore._float_lattice_expression(F, lower, upper, decimals)
    return df.withColumn(col_name, value)

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
    timestamp_start, timestamp_end = (int(d.replace(tzinfo=timezone.utc).timestamp()) for d in (dt_start, dt_end))
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
