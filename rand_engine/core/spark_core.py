from datetime import datetime as dt
import pandas as pd


class SparkCore:

    @staticmethod
    def gen_ints(spark, F, df, col_name, min=0, max=10):
      return df.withColumn(col_name, (F.rand() * (max - min) + min).cast("int"))
  
    @staticmethod
    def gen_floats(spark, F, df, col_name, min=0.0, max=10.0, decimals=2):
      return df.withColumn(col_name, F.round(F.rand() * (max - min) + min, decimals))
    
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

  