from core import *

import numpy as np

def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)


def fake_data2(size, **kwargs):
    null_rate = normalize_prop(kwargs["null_rate"]) if kwargs["null_rate"] is not None \
                else 0
    null_size = int(size * null_rate)
    data_size = size - null_size
    methods_dict = {"fake_discrete": fake_discrete, "fake_int": fake_int, "fake_float": fake_float,
                    "fake_float_normal": fake_float_normal, "fake_alphanum": fake_alphanum,
                    "fake_date": fake_date, "fake_name": fake_name, "fake_unique_name": fake_unique_name}

    null_part = fake_discrete(size=null_size, distinct=kwargs.get("null_args")) \
        if kwargs.get("null_args") is not None else []

    data_part = methods_dict[kwargs["method"]](size=data_size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]

    res = np.concatenate((null_part, data_part))
    np.random.shuffle(res)
    return res

def create_table(size=5, **kwargs):
    vect = []
    for i in range(len(kwargs["data"])):
        result = [str(item) for item in fake_data2(size=size, **kwargs["data"][i])]
        vect.append(result)
    res_data = list(zip(*vect))
    return res_data, kwargs["names"]


import unittest

class TestTableMethods(unittest.TestCase):

    metadata1 = dict(
        names=["fake_int", "fake_float", "fake_float_normal"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_int", min_size=5, max_size=8),
            dict(null_rate=0.1, null_args=[None], method="fake_float", min_size=5, max_size=10),
            dict(null_rate=0.1, null_args=[None], method="fake_float_normal", mean=10000, end=3000)
        ]
    )

    metadata2 = dict(
        names=["fake_alphanum", "fake_name", "fake_unique_name"],
        data=[
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum", format="aa22cc"),
            dict(null_rate=0.2, null_args=[None], method="fake_name",
                 names=[["marco", "paulo", "jose"], ["reis", "santos", "lopes"]]),
            dict(null_rate=0.2, null_args=[None], method="fake_unique_name",
                 names=[["marco", "paulo", "jose"], ["reis", "santos", "lopes"]])
        ]
    )

    metadata3 = dict(
        names=["fake_date", "fake_discrete"],
        data=[
            dict(null_rate=0.1, null_args=[None], method="fake_date",
                 start="06-12-2019", end="11-28-2019"),
            dict(null_rate=0.2, null_args=[None], method="fake_discrete",
                 distinct=["valor_1", "valor_2", "valor_3"])
        ]
    )

    def test_fake_data(self):
        vect = [self.metadata1, self.metadata2, self.metadata3]
        for i in vect:
            for j in i["data"]:
                print(fake_data2(size=10, **j))
        self.assertEqual('foo'.upper(), 'FOO')

    # def test_create_table(self):
    #     print(create_table(size=100, **self.metadata3))
    #     self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()