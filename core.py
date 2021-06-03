from numpy.random import randint
from dateutil import parser
from datetime import datetime


def fake_categorical(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [kwargs["distinct"][i] for i in aux]

def fake_null(size, *args): 
    args = [None] if len(args) == 0 else args
    return fake_categorical(size, distinct = args)

def fake_num(size=5, min_size=5, max_size=10):
    tam = randint(min_size,max_size)
    return [ str(randint(0,10 ** tam)).zfill(tam) for i in range(size) ]

#format # dia mes ano
def random_date(size, start, end):
    interval = parser.parse(start).timestamp(), parser.parse(end).timestamp()
    int_array = randint(interval[0], interval[1], size)
    return [ datetime.fromtimestamp(i).strftime("%m/%d/%Y") for i in int_array ]

# Escrever testes aqui
# Criar arquivo teste de performance


import unittest

class TestStringMethods(unittest.TestCase):

    def test_fake_categorical(self):
        print(fake_categorical(distinct=["ccorrent", "cpoupanca"]))
        self.assertEqual('foo'.upper(), 'FOO')

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()

