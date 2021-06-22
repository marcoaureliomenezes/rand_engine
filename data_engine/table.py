from .fakenamecode import fake_discrete, fake_alphanum
from .fakenum import fake_int, fake_float, fake_float_normal
from .fakedate import fake_date, fake_partition
from .core import nonefy


def fake_data(size, **kwargs):
    methods_dict = {"fake_discrete": fake_discrete,"fake_int": fake_int, 
                    "fake_float": fake_float,"fake_float_normal": fake_float_normal,
                    "fake_alphanum": fake_alphanum,"fake_date": fake_date,
                    "fake_partition": fake_partition }
    result = methods_dict[kwargs["method"]](size=size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]
    result = nonefy(result, chance=kwargs.get("null_rate"), distinct=kwargs.get("null_args"))
    return result


def create_table(size=5, **kwargs):
    vect = []
    for i in range(len(kwargs["data"])):
        result = [str(item) for item in fake_data(size=size, **kwargs["data"][i])]
        vect.append(result)
    res_data = list(zip(*vect))
    return res_data, kwargs["names"]


import unittest

class TestTableMethods(unittest.TestCase):

    metadata1 = dict(
        names=["fake_int1", "fake_int2",  "fake_int3", "fake_int4", "fake_int5", "fake_int6"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_int"),
            dict(null_rate=0.2, null_args=[None], method="fake_int", min=10, max=20),
            dict(null_rate=0.2, null_args=[None], method="fake_int", min=5, max=10, algnum=True),
            dict(null_rate=0.2, null_args=[None], method="fake_int", min=5, max=10, algnum=True, array_type="string"),
            dict(null_rate=0.2, null_args=[None], method="fake_int", min=5, max=10, algnum=True, array_type="string", algsize=12),
            dict(null_rate=0.2, null_args=[None], method="fake_int", min=5, max=10, algnum=True, array_type="int"),
        ]
    )

    metadata2 = dict(
        names=["fake_float1","fake_float2","fake_float3","fake_float4","fake_float5","fake_float6",
                "fake_float_7", "fake_float_8"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_float"),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=10, max=20),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=10, max=20, round=2),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=10, max=20, round=2, outlier=True),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=5, max=10, round=2, algnum=True),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=5, max=10, algnum=True, round=2, array_type="string"),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=5, max=10, round=2, algnum=True, array_type="string", algsize=12),
            dict(null_rate=0.2, null_args=[None], method="fake_float", min=5, max=10, algnum=True, array_type="int"),
        ]
    )

    metadata3 = dict(
        names=["fake_float_normal1","fake_float_normal2","fake_float_normal3","fake_float_normal4",
        "fake_float_normal5","fake_float_normal6","fake_float_normal7","fake_float_normal8" ],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal"),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, round=2),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, round=2, outlier=True),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, round=2, outlier=True),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, outlier=True, round=2, array_type="int"),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, outlier=True, round=2, array_type="str"),
            dict(null_rate=0.2, null_args=[None], method="fake_float_normal", mean=100, std=20, outlier=True, round=0, algsize=12),
        ]
    )

    metadata4 = dict(
        names=["fake_discrete1", "fake_discrete2", "fake_discrete3",
        "fake_discrete4", "fake_discrete5", "fake_discrete6"],
        data=[
            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                 distinct=["marco, pedro", "lucas", "gustavo","andre"]),
            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                 distinct=[["marco, pedro", "lucas", "gustavo","andre]"],
                 ["reis","dias","pereira","ribeiro","de lucca","pires"]]),

            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                 distinct=[["marco, pedro", "lucas", "gustavo","andre", "ana","maria","lucia","licia"],
                 ["reis","dias","pereira","lopes","ribas""ribeiro","de lucca","pires"]], let_case="upper"),

            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                 distinct=[["marco, pedro", "lucas", "gustavo","andre]"],
                 ["reis","dias","pereira","ribeiro","de lucca","pires"]], let_case="lower"),

            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                 distinct=[["marco, pedro", "lucas", "gustavo","andre", "paulo","maria","fernanda"],
                 ["reis","lopes","dias","pereira","ribeiro","de lucca","pires"]], let_case="capitalize"),
            dict(null_rate=0.1, null_args=[None], method="fake_discrete",
                   distinct=[["marco, pedro", "lucas", "gustavo","andre", "lua","lucia","ana","Ian","luan","ribas","rubens"],
                 ["reis","dias","nunes","gianini","menezes","souza","pereira","ribeiro","de lucca","pires"]], rm_dupl=True),
        ]
    )
    metadata5 = dict(
        names=["fake_alphanum1","fake_alphanum2","fake_alphanum3","fake_alphanum4","fake_alphanum5","fake_alphanum6","fake_alphanum_7"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum"),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22bb"),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum",format="aa22bb", let_case="upper"),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22bb", let_case="lower"),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22bb", let_case="cap"),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22bb", rm_dupl=True),
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22bb", 
            distinct=["contacorrente", "poupanca", "acoes"], sep="-"),
        ]
    )

    metadata7 = dict(
        names=["fake_date1","fake_date2","fake_date3","fake_date4","fake_date5"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_date"),
            dict(null_rate=0.2, null_args=[None], method="fake_date", start="02-06-2020", end="06-06-2020"),
            dict(null_rate=0.2, null_args=[None], method="fake_date",start="2-6-2020", end="6-6-2020"),
            dict(null_rate=0.2, null_args=[None], method="fake_date",start="2-6-2020", end="6-6-2020", format="%d/%m/%Y"),
            dict(null_rate=0.2, null_args=[None], method="fake_date",start="2-6-2020", end="6-6-2020", format=["%d/%m/%Y", "%d-%m-%Y", "%d %m %y"]),
    
        ]
    )
    metadata8 = dict(
        names=["fake_partition1","fake_partition2"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=5),
            dict(null_rate=0.2, null_args=[None], method="fake_partition", part_type="date", start="07-05-2020", end="07-05-2021", num_part=10),

    
        ]
    )
    # def test_fake_data(self):
    #     vect = [self.metadata1, self.metadata2]
    #     print("start")
    #     for i in vect:
    #         for j in i["data"]:
    #             print(fake_data(size=10, **j))
    #     self.assertEqual('foo'.upper(), 'FOO')

    def test_create_table(self):
        print(create_table(size=10, **self.metadata8))
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()