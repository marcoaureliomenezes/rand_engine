
import pyspark.sql.functions as F
from pyspark.sql.functions import randn, rand, randstr
from pyspark.sql import DataFrame, SparkSession
import pandas as pd

class RandSpark:

    def __init__(self, spark, df: DataFrame):
        self.spark = spark
        self._df = df


    def withColumnRandInt(self, col_name="rand_int", min_size=0, max_size=10):
        return RandSpark(
            self._df.withColumn(col_name, (F.rand() * (max_size - min_size) + min_size).cast("int"))
        )
    
    def withColumnRandFloat(self, col_name="rand_float", min_size=0.0, max_size=10.0, decimals=2):
      
        return RandSpark(
            self._df.withColumn(col_name, F.round(F.rand() * (max_size - min_size) + min_size, decimals))
        )
    
    def withColumnRandChoice(self, col_name="rand_choice", distincts=[]):
        df_columns = self._df.columns
        aux_col = f"{col_name}_aux"
        
        df_pd = pd.DataFrame(distincts, columns=[col_name])
        df_pd[aux_col] = range(len(distincts))
        df_spark = self.spark.createDataFrame(df_pd)
        df = RandSpark(self._df.withColumn(aux_col, (F.rand() * (len(distincts) - 0) + 0).cast("int")))
        return (
            df.alias("a").join(F.broadcast(df_spark).alias("b"), on=aux_col, how="left") \
            .select(*df_columns, f"b.{col_name}"))


    def __getattr__(self, name):
        """Delegate unknown methods to the original DataFrame"""
        return getattr(self._df, name)