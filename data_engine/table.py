from fakemethods import *
import pandas as pd

def fake_data(size, **kwargs):
    methods_dict = {"fake_discrete": fake_discrete,"fake_int": fake_int, 
                    "fake_float": fake_float,
                    "fake_alphanum": fake_alphanum,"fake_date": fake_date,
                    "fake_partition": fake_partition }
    return methods_dict[kwargs["method"]](size=size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]

def create_table(size=5, **kwargs):
    names, data = (kwargs["names"], kwargs["data"])
    return pd.DataFrame({names[i]: fake_data(size, **data[i]) for i in range(len(data))})
    
import unittest
from names import names, last_names
class TestTableMethods(unittest.TestCase):

    metadata1 = dict(
        names=["fake_int1", "fake_int2",  "fake_int3", "fake_int4"],
        data=[
            dict(method="fake_int"),
            dict(method="fake_int", min=10, max=20),
            dict(method="fake_int", min=4, max=7, algnum=True),
            dict(method="fake_int", min=4, max=7, algnum=True, algsize=10),
        ]
    )

    metadata2 = dict(
        names=["fake_float1","fake_float2","fake_float3", "fake_normal1", "fake_normal2", "fake_float4","fake_float5"],
        data=[
            dict(method="fake_float"),
            dict(method="fake_float", min=10, max=20),
            dict(method="fake_float", min=10, max=20, round=2),
            dict(method="fake_float", mean=100., std=20., type="normal", round=2),
            dict(method="fake_float", mean=100., std=20., type="normal", round=2, outlier=True),
            dict(method="fake_float", min=10, max=20, round=2, outlier=True),
            dict(method="fake_float", min=5, max=7, round=2, algnum=True),
        ]
    )

    metadata3 = dict(
        names=["fake_discrete1", "fake_discrete2", "fake_discrete3",
        "fake_discrete4", "fake_discrete5", "fake_discrete6"],
        data=[
            dict(method="fake_discrete", distinct=["bitcoin","etherium", "ripple"] ),
            dict(method="fake_discrete", distinct=names),
            dict(method="fake_discrete", distinct=[names, last_names], let_case="upper"),
            dict(method="fake_discrete", distinct=[names, last_names], let_case="lower"),
            dict(method="fake_discrete",distinct=[names, last_names], let_case="capitalize"),
            dict(method="fake_discrete", distinct=[names, last_names], rm_dupl=True),
        ]
    )
    metadata4 = dict(
        names=["fake_alphanum1","fake_alphanum2","fake_alphanum3","fake_alphanum4","fake_alphanum5","fake_alphanum6","fake_alphanum_7"],
        data=[
            dict(method="fake_alphanum"),
            dict(method="fake_alphanum", format="aa22bb"),
            dict(method="fake_alphanum",format="aa22bb", let_case="upper"),
            dict(method="fake_alphanum", format="aa22bb", let_case="lower"),
            dict(method="fake_alphanum", format="aa22bb", let_case="cap"),
            dict(method="fake_alphanum", format="aa22bb", rm_dupl=True),
            dict(method="fake_alphanum", format="aa22bb", 
            distinct=["contacorrente", "poupanca", "acoes"], sep="-"),
        ]
    )

    metadata5 = dict(
        names=["fake_date1","fake_date2","fake_date3","fake_date4","fake_date5"],
        data=[
            dict(method="fake_date"),
            dict(method="fake_date", start="02-06-2020", end="06-06-2020"),
            dict(method="fake_date",start="2-6-2020", end="6-6-2020"),
            dict(method="fake_date",start="2-6-2020", end="6-6-2020", format="%d/%m/%Y"),
            dict(method="fake_date",start="2-6-2020", end="6-6-2020", format=["%d/%m/%Y", "%d-%m-%Y", "%d %m %y"]),
    
        ]
    )
    metadata6 = dict(
        names=["fake_partition1","fake_partition2"],
        data=[
            dict(method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=5),
            dict(method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=10),
        ]
    )

    def test_table_pandas_int(self):
        table_pandas = create_table(size=10000, **self.metadata1)
        print(table_pandas)

    def test_table_pandas_float(self):
        table_pandas = create_table(size=10000, **self.metadata2)
        print(table_pandas)

    def test_table_pandas_discrete(self):
        table_pandas = create_table(size=10000, **self.metadata3)
        print(table_pandas)
    # def test_table(self):
    #     from pyspark.sql import SparkSession
    #     spark = SparkSession.builder.appName("SparkSQL").getOrCreate()
    #     spark.sparkContext.setLogLevel('ERROR')
    #     spark = SparkSession.builder.appName("SparkSQL").getOrCreate()
    #     spark.sparkContext.setLogLevel('ERROR')
    #     tabela_para_spark = create_table(size=100, **self.all_metadata)
    #     df = spark.createDataFrame(tabela_para_spark[0], tabela_para_spark[1])


if __name__ == '__main__':
    unittest.main()


# Chamada que cria os dados realmente, usando o dicionario metadata descrito acima.
#Retorna uma tupla, onde o primeiro valor tabela_para_spark[1] são os nomes das colunas e
# tabela_para_spark[0] são os dados
 