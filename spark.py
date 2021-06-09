from pyspark.sql import SparkSession
from table_gen import table

meta_data = dict(
    names = ["tipo_produto", "cpf", "data_contrato"],
    data = [
        dict(null_rate=0.2, null_args=[None], categorical=True,
            distinct=["ccorrente", "ações", "criptmoeda"]),

        dict(null_rate=0.1, null_args=[None], identif=True, 
                min_size=5, max_size=10),

        dict(null_rate=0.1, null_args=[None], interval=True, 
            start="06-12-2019", end="11-28-2019")
    ]
)



# Create a SparkSession
spark = SparkSession.builder.appName("SparkSQL").getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

result = table.create_table(size=100000, **meta_data)
df = spark.createDataFrame(result[0], result[1])
df.describe().show()