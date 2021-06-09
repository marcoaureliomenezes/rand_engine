from numpy.random import randint
from dateutil import parser
from datetime import datetime

def fake_discrete(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [str(kwargs["distinct"][i]) for i in aux]

def fake_num(size=5, **kwargs):
    tam = randint(kwargs["min_size"],kwargs["max_size"]) \
            if kwargs.get("min_size") is not None and kwargs.get("max_size") is not None else None
    print(tam)
    return [ str(randint(0,10 ** tam)).zfill(tam) for i in range(size) ]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else 2
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]

import unittest

class TestStringMethods(unittest.TestCase):

    def test_fake_categorical(self):
        print(fake_discrete(distinct=["ccorrent", "cpoupanca"]))
        self.assertEqual('foo'.upper(), 'FOO')

    def test_fake_num(self):
        print(fake_num(min_size=5, max_size=10))
        self.assertFalse('Foo'.isupper())

    def test_fake_date(self):
        print(fake_date(start="20-02-2020", end="27-05-2020"))
        self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()

