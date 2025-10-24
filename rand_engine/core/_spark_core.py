from datetime import datetime as dt
import pandas as pd


class SparkCore:

    @staticmethod
    def gen_uuid4(spark, F, df, col_name):
      return df.withColumn(col_name, F.expr("uuid()"))
    
    @staticmethod
    def gen_ints(spark, F, df, col_name, min=0, max=10):
      return df.withColumn(col_name, (F.rand() * (max - min) + min).cast("long"))
  
    @staticmethod
    def gen_ints_zfill(spark, F, df, col_name, length=10):
      max_value = 10 ** length - 1
      df = SparkCore.gen_ints(spark, F, df, col_name, min=0, max=max_value)
      return df.withColumn(col_name, F.lpad(F.col(col_name).cast("string"), length, "0"))

    @staticmethod
    def gen_floats(spark, F, df, col_name, min=0.0, max=10.0, decimals=2):
      return df.withColumn(col_name, F.round(F.rand() * (max - min) + min, decimals))
    
    @staticmethod
    def gen_floats_normal(spark, F, df, col_name, mean=0.0, stddev=1.0, decimals=2):
      return df.withColumn(col_name, F.round(F.randn() * stddev + mean, decimals))
    
    @staticmethod
    def gen_distincts(spark, F, df, col_name, distincts=[]):
      aux_col = f"aux_col{col_name}"
      df_pd = pd.DataFrame(distincts, columns=[col_name])
      df_pd[aux_col] = range(len(distincts))
      df_spark = spark.createDataFrame(df_pd)
      df_columns = df.columns
      df_result = df.withColumn(aux_col, (F.rand() * (len(distincts) - 0) + 0).cast("int"))
      return (
        df_result.alias("a").join(F.broadcast(df_spark).alias("b"), on=aux_col, how="left")
        .select(*df_columns, f"b.{col_name}"))

    @staticmethod
    def gen_booleans(spark, F, df, col_name, true_prob=0.5):
      return df.withColumn(col_name, F.rand() < true_prob)


    @staticmethod
    def gen_dates(spark, F, df, col_name, start="1970-01-01", end="2023-01-01", formato="%Y-%m-%d"):
      map_formats = {
        "%Y": "yyyy", "%m": "MM", "%d": "dd","%H": "HH", "%M": "mm", "%S": "ss", "%f": "SSSSSS"
      }
      spark_format = formato
      for k, v in map_formats.items():
        spark_format = spark_format.replace(k, v)
      dt_start, dt_end = dt.strptime(start, formato), dt.strptime(end, formato)
      if dt_start < dt(1970, 1, 1): dt_start = dt(1970, 1, 1)
      timestamp_start, timestamp_end = int(dt_start.timestamp()), int(dt_end.timestamp())
      df = SparkCore.gen_ints(spark, F, df, col_name, min=timestamp_start, max=timestamp_end)
      return df.withColumn(col_name, 
                          F.date_format(F.from_unixtime(F.col(col_name), spark_format).cast("timestamp"), spark_format))