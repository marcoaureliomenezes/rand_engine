from speeding.core import fake_discrete, fake_num, fake_date
from speeding.core import fake_alphanum, fake_name, fake_name_unique
from speeding.core import fake_float, fake_float_normal

import numpy as np

def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)

def fake_data(size, **kwargs):
    null_rate = normalize_prop(kwargs["null_rate"]) if kwargs["null_rate"] is not None \
                else 0
    null_size = int(size * null_rate)
    data_size = size - null_size

    null_part = fake_discrete(size=null_size, distinct=kwargs.get("null_args")) \
        if kwargs.get("null_args") is not None else []

    if kwargs.get("method") == "fake_discrete":
        data_part = fake_discrete(size=data_size, distinct=kwargs["distinct"])

    elif kwargs.get("method") == "fake_num":
        data_part = fake_num(size=data_size, \
                             min_size=kwargs["min_size"], max_size=kwargs["max_size"] ) 
     
    elif kwargs.get("method") == "fake_date":
        data_part = fake_date(size=data_size, start=kwargs["start"], end=kwargs["end"])

    elif kwargs.get("method") == "fake_alphanum":
        data_part = fake_alphanum(size=data_size, format="a333bb" ) 
     
    elif kwargs.get("method") == "fake_float":
        data_part = fake_float(size=data_size, min=kwargs["min"],
                                max=kwargs["max"], algsize=kwargs["algsize"])

    elif kwargs.get("method") == "fake_float_normal":
        data_part = fake_float_normal(size=data_size, mean=kwargs["mean"], std=kwargs["std"])

    elif kwargs.get("method") == "fake_name":
        data_part = fake_name(*kwargs["names"], size=data_size)

    elif kwargs.get("method") == "fake_unique_name":
        data_part = fake_name_unique(*kwargs["names"], size=data_size)
    else:
        data_part = [None for i in range(size)]

    res = np.concatenate((null_part, data_part))
    np.random.shuffle(res)
    return res

def create_table(size=6, **kwargs):
    vect = []
    for i in range(len(kwargs["data"])):
        result = [str(item) for item in fake_data(size=size, **kwargs["data"][i])]
        vect.append(result)
    res_data = list(zip(*vect))
    return res_data, kwargs["names"]


import unittest

class TestTableMethods(unittest.TestCase):

    metadata1 = dict(
        names = ["discrete", "identif", "date"],
        data = [
            dict(null_rate=0.2, null_args=[None], method="fake_discrete",
                distinct=["valor_1", "valor_2", "valor_3"]),

            dict(null_rate=0.1, null_args=[None], method="fake_num", 
                    min_size=5, max_size=10),

            dict(null_rate=0.1, null_args=[None], method="fake_date", 
                start="06-12-2019", end="11-28-2019")
        ]
    )

    metadata2 = dict(
        names = ["alphanum", "float", "float_normal"],
        data = [
            dict(null_rate=0.2, null_args=[None], method="fake_alphanum",
                format="aabb22cc"),

            dict(null_rate=0.1, null_args=[None], method="fake_float", 
                    min=1000, max=200000, algsize=15),

            dict(null_rate=0.1, null_args=[None], method="fake_float_normal", 
                mean=20000, std=4000)
        ]
    )

    metadata3 = dict(
        names = ["name", "unique_name"],
        data = [
            dict(null_rate=0.2, null_args=[None], method="fake_name",
                names=[["marco","paulo","jose","ricardo"],["santander"]])
        ]
    )

    def test_fake_data(self):
        # for i in self.metadata3["data"]:
            # print(fake_data(size=10, **i))
        self.assertEqual('foo'.upper(), 'FOO')

    def test_create_table(self):
        print(create_table(size=100, **self.metadata3))
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()