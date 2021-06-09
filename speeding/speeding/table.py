from speeding.core import fake_discrete, fake_num, fake_date
import numpy as np

def normalize_prop(num):
    return 0  if num < 0 else ( 1 if num > 1 else num)

def fake_data(size, **kwargs):
    null_rate = normalize_prop(kwargs["null_rate"])
    null_size = int(size * null_rate)

    null_part = fake_discrete(size=null_size, distinct=kwargs.get("null_args")) \
        if kwargs.get("null_args") is not None else []

    if kwargs.get("categorical") is not None:
        data_part = fake_discrete(size=(size - null_size), distinct=kwargs["distinct"])

    elif kwargs.get("identif") is not None:
        data_part = fake_num(size=(size - null_size), \
                             min_size=kwargs["min_size"], max_size=kwargs["max_size"] ) 
     
    elif kwargs.get("interval") is not None:
        data_part = fake_date(size=(size - null_size), start=kwargs["start"], end=kwargs["end"])

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

    metadata = dict(
        names = ["coluna_A", "coluna_B", "coluna_C"],
        data = [
            dict(null_rate=0.2, null_args=[None], categorical=True,
                distinct=["valor_1", "valor_2", "valor_3"]),

            dict(null_rate=0.1, null_args=[None], identif=True, 
                    min_size=5, max_size=10),

            dict(null_rate=0.1, null_args=[None], interval=True, 
                start="06-12-2019", end="11-28-2019")
        ]
    )

    def test_fake_data(self):
        print(fake_data(size=5, null_rate=0.2, null_args=[None], categorical=True,
                distinct=["valor_1", "valor_2", "valor_3"]))
        fake_data(size=5, null_rate=1, null_args=[None], categorical=True, distinct=["valor_1"])
        fake_data(size=5, null_rate=0, null_args=[None], categorical=True, distinct=["valor_1"])
        self.assertEqual('foo'.upper(), 'FOO')

    def test_create_table(self):
        print(create_table(min_size=5, **self.metadata))
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()