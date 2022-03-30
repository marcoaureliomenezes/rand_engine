from performance import loop_complexity
from fakemethods import *
import pandas as pd, sys

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
    

def queue_1_second_volume_data(size=10000, rate=1, **kwargs):
    time, length = loop_complexity(create_table, size=size, **kwargs)
    one_second_data = (length * rate) / (time)
    list_of_1_second_dfs = []
    # This must be one thread in while 1
    for i in range(11):
        list_of_1_second_dfs.append(create_table(size=int(one_second_data), **kwargs))
        print(f"pass {i}")
        if len(list_of_1_second_dfs) >= 10:
            list_of_1_second_dfs.pop(0)
    print("END!")
    result = pd.concat(list_of_1_second_dfs, axis=0)
    print(f"Size in Mb: {sys.getsizeof(result) / 1024 ** 2}")
    return (length * rate) / (time)
#############################################################################################

import unittest
from names import names, last_names
class TestTableMethods(unittest.TestCase):

    size=1000000

    def test_fake_int_table(self):
        metadata = dict(
            names=["fake_int1", "fake_int2",  "fake_int3", "fake_int4"],
            data=[
                dict(method="fake_int"),
                dict(method="fake_int", min=10, max=20),
                dict(method="fake_int", min=4, max=7, algnum=True),
                dict(method="fake_int", min=4, max=7, algnum=True, algsize=10),
            ]
        )
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

    def test_fake_float_table(self):
        metadata = dict(
            names=["fake_float1","fake_float2","fake_float3", "fake_normal1", "fake_normal2", 
            "fake_float4","fake_float5"],
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
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

    def test_fake_discrete_table(self):
        metadata = dict(
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
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

    def test_fake_discrete_table(self):
        metadata = dict(
            names=["fake_alphanum1","fake_alphanum2","fake_alphanum3","fake_alphanum4","fake_alphanum5","fake_alphanum6","fake_alphanum_7"],
            data=[
                dict(method="fake_alphanum"),
                dict(method="fake_alphanum", format="aa22bb"),
                dict(method="fake_alphanum", format="11. 111. 111/0001-11"),
                dict(method="fake_alphanum", format="mmmm_mmmm@ggg.com"),
                dict(method="fake_alphanum", format="111.555.444-67", 
                distinct=["contacorrente", "poupanca", "acoes"], sep="-"),
            ]
        )
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

    def test_fake_date_table(self):
        metadata = dict(
            names=["fake_date1","fake_date2","fake_date3","fake_date4","fake_date5"],
            data=[
                dict(method="fake_date"),
                dict(method="fake_date", start="02-06-2020", end="06-06-2020"),
                dict(method="fake_date",start="2-6-2020", end="6-6-2020"),
            ]
        )
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

    def test_fake_date_table(self):
        metadata = dict(
            names=["fake_partition1","fake_partition2"],
            data=[
                dict(method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=5),
                dict(method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=10),
            ]
        )
        table_pandas = create_table(size=self.size, **metadata)
        print(table_pandas)

 


if __name__ == '__main__':
    print("Hello")

    metadata = dict(
        names=["fake_int1", "fake_int2",  "fake_int3", "fake_int4"],
        data=[
            dict(method="fake_int"),
            dict(method="fake_int", min=10, max=20),
            dict(method="fake_int", min=4, max=7, algnum=True),
            dict(method="fake_int", min=4, max=7, algnum=True, algsize=10),
        ]
    )
    queue_1_second_volume_data(size=1000000, rate=1, **metadata)

# TODO:

#   Criar testes para table no modelo de fake methods
#   Mudar testes de performance para fora do pacote
#   
#   criar maneira de passar tipos e outras configurações para dados pelo pandas
#   varios metodos para emagrecer utils e handlers (num and something).

#   Criar metodo que calcula numero de linhas criadas por segundo de determinada configuração
#   de tabela para alimentar spark em tempo
#   começar a cuspir esses dados por segundo

#   Começar a criar modulo que lê amostra de tamanho de uma tabela e traduz dados em metadados


 