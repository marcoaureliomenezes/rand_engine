import numpy as np
import pyspark
from .table import create_table
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, first, avg, sum, col

def multiple_columns_append(df, **kwargs):
    for i in kwargs:
        df = df.withColumn(i, lit(kwargs[i])).alias(i)
    return df

def rename_multiple_columns(df, **kwargs):
    for i in kwargs:
        if i in df.columns:
            df = df.withColumnRenamed(i, kwargs[i])
    return df

def sum_or_first_agg(df, groupedBy, sum_args):
    columns = df.columns
    columns.remove(groupedBy)
    sum_or_first_agg = [sum(x).alias(x) if x in sum_args else first(x).alias(x) for x in columns]
    return df.groupBy(groupedBy).agg(*sum_or_first_agg)

metadata = dict(
    names=["id", "idade", "tipo_conta", "tipo_cliente", "saldo", "qtd_acoes"
          ],
    data=[
        # ints
        dict(null_rate=0., null_args=[None], method="fake_int", min_size=0, max_size=10),
        dict(null_rate=0., null_args=[None], method="fake_int", min_size=0, max_size=99),
        dict(null_rate=0., null_args=[None], method="fake_discrete", distinct=["ccorrente","cpoupanca"]),
        dict(null_rate=0., null_args=[None], method="fake_discrete", distinct=["PF","PJ", "ONG"]),
        dict(null_rate=0., null_args=[None], method="fake_float", min_size=10., max_size=3000, outlier=True, round=2),
        dict(null_rate=0., null_args=[None], method="fake_float", min_size=0, max_size=999, array_type="int"),
    ]   
)
spark = SparkSession.builder.appName("SparkSQL").getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

tabela_para_spark = create_table(size=100, **metadata)
df = spark.createDataFrame(tabela_para_spark[0], tabela_para_spark[1])
df.show(20)

df = multiple_columns_append(df, col1="Ola",col2="hallo")
df = sum_or_first_agg(df, "id", ["saldo", "qtd_acoes"])
df = rename_multiple_columns(df, tipo_conta="conta", teste="acoes", qtd_acoes="ações", col1="port",col2="deut")
df.orderBy("id").show()