# Codigo escrito por Marco Menezes

import random, math, itertools, unittest
from numpy.random import rand, randint
from dateutil import parser
from datetime import datetime
import numpy as np
from functools import reduce
from utils import replace_duplicate


def stringify(iterr, **kwargs):
    return str(iterr).zfill(kwargs["algsize"]) if ( kwargs.get("string") and kwargs.get("algsize")) \
                    else str(iterr) if kwargs.get("string") else iterr

def intify(input_array):
    return [int(i) for i in input_array]


def round_array(iterr, **kwargs):
    return round(iterr, kwargs["round"]) if kwargs.get("round") else round(iterr, 2)


def fake_int(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.randint(0, 9) for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = list(randint(kwargs["min"], kwargs["max"] + 1, size))
    else:
        def random_int(size, **kw):
            return [math.floor(
                random.random() * math.pow(10, random.randint(kw.get("min"), (kw.get("max")))))
                for i in range(size)]
        result = random_int(size, **kwargs)
    return stringify(result, **kwargs) if kwargs.get("array_type") == "string" else \
            intify(result) if kwargs.get("array_type") == "int" else result


def fake_float(size=5, **kwargs):
    if kwargs.get("min_size") and kwargs.get("max_size"):
        if kwargs.get("round"):
            return [int(i) / kwargs["round"] for i in
                fake_int(size=size, min_size=kwargs["min_size"] + kwargs["round"],
                    max_size=kwargs["max_size"] + kwargs["round"])]
        return [int(i)/2 for i in fake_int(size=size, min_size=kwargs["min_size"] + 2,
                                                    max_size=kwargs["max_size"] + 2)]
    return [0. for i in range(size)]


def fake_float_normal(size=5, **kwargs):
    def random_float_normal(**kw):
        return np.random.normal(kw["mean"], kw["std"]) if (kw.get("mean") and kw.get("std")) else 0.
    result = [random_float_normal(**kwargs) for i in range(size)]
    result = [round_array(i, **kwargs) for i in result]
    result = [stringify(i, **kwargs) for i in result]
    return result


def fake_alphanum(size=5, **kwargs):
    def random_alphanum(**kw):
        return np.array([np.array([chr(i) for i in randint(97, 123, size)]
            if i.isalpha() else [chr(i) for i in randint(48, 57, size)])
            for i in kw["format"]], dtype=object)
    if kwargs.get("format"):
        return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], random_alphanum(**kwargs))
    return ["" for i in range(size)]


def fake_discrete(size=5, **kwargs):

    def random_single_word(size, **kw):
        return list(map(lambda x: kw["distinct"][x], randint(0, len(kw["distinct"]), size)))

    def random_multi_word(**kw):
        result_array = [[arg[j] for j in randint(0, len(arg), size)] for arg in kw["distinct"]]
        return [reduce(lambda a, b: f"{a} {b}", fullname) for fullname in list(zip(*result_array))]

    if type(kwargs.get("distinct")) is list:
        if len(kwargs.get("distinct")) > 0 and type(kwargs.get("distinct")[0]) is list:
            res = random_multi_word(**kwargs)
        elif type(kwargs.get("distinct") is str):
            res = random_single_word(size, **kwargs)
        return replace_duplicate(res, None) if kwargs.get("rm_dupl") else res
    return ["" for i in range(size)]


def fake_date(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else (100000000, 100010000)
    int_array = randint(interval[0], interval[1], size)
    if type(kwargs.get("format")) is list:
        return [datetime.fromtimestamp(i).strftime(kwargs["format"][randint(0, len(kwargs["format"]))])
                for i in int_array]
    elif type(kwargs.get("format")) is str:
        return [datetime.fromtimestamp(i).strftime(kwargs["format"]) for i in int_array]
    return [datetime.fromtimestamp(i).strftime("%d-%m-%Y") for i in int_array]


class TestCoreMethods(unittest.TestCase):

    def test_fake_int(self):
        built_max = max
        built_min = min
        # SEM ARGUMENTOS
        fake_int1 = fake_int()
        print("Teste sem parâmetros:\t", fake_int1)
        self.assertTrue(built_max(fake_int1) < 10, msg="Valores menores que 10")
        self.assertTrue(built_max(fake_int1) >= 0, msg="Valores maiores ou igual que 0")
        self.assertTrue(len(fake_int1) == 5, msg="Tamanho default igual a 5")
        self.assertTrue(type(fake_int1[1]) == int, msg="elementos da lista são inteiros")

        ######################################################################################################
        # ARGUMENTO SIZE
        size = 10
        fake_int2 = fake_int(size)
        print("Teste com parametros min e max:\t", fake_int2)
        self.assertTrue(len(fake_int2) == size, msg="Tamanho do array de saída igual ao passado por parâmetro")

        #######################################################################################################
        # ARGUMENTO MAX e MIN
        min_num = 5; max_num = 10
        fake_int3 = fake_int(min=min_num, max=max_num)
        print("Teste com parametros min e max:\t", fake_int3)
        self.assertTrue(built_max(fake_int3) <= max_num, msg="Valores menores que parâmetro max")
        self.assertTrue(built_min(fake_int3) >= min_num, msg="Valores maiores ou igual a parâmetro min")
        self.assertTrue(len(fake_int3) == 5, msg="Tamanho default igual a 5")

        #######################################################################################################
        # ARGUMENTO MAX e MIN associado com parametro algnum=True
        min_size = 5; max_size = 7
        fake_int4 = fake_int(min=min_size, max=max_size, algnum=True)
        print("Teste com parametros min, max e algsize:\t", fake_int4)
        tamanho_nums = [int(math.log10(x) + 1) for x in fake_int4]
        self.assertTrue(built_max(tamanho_nums) <= max_size, msg="Valores menores que parâmetro max")

        #######################################################################################################
        # ARGUMENTO MAX e MIN associado com parametro algnum=True e array_type igual a string
        min_size = 5; max_size = 7; arraytype = "String"
        fake_int5 = fake_int(min=min_size, max=max_size, algnum=True, array_type="string")
        print("Teste com parametros min, max e algnum e array_type:\t", fake_int5)
        self.assertTrue(type(fake_int5[0]) == str, msg="elementos do tipo string")
        self.assertTrue(built_max(tamanho_nums) <= max_size, msg="Valores menores que parâmetro max")
 
        #######################################################################################################
        min_size = 5; max_size = 7; algarism_size=12
        fake_int6 = fake_int(min=min_size, max=max_size, algnum=True, array_type="string", algsize=algarism_size)
        self.assertTrue(type(fake_int6[0]) == str, msg="elementos do tipo string")
        self.assertTrue(len(fake_int6[0]) == algarism_size, msg="Algarismos em string com tamanho correto")

        #######################################################################################################
        min_size = 5; max_size = 7; algarism_size=12
        fake_int7 = fake_int(min=min_size, max=max_size, algnum=True, array_type="int")
        print("Teste com parametros min, max e algnum e array_type = int:\t", fake_int7)
        self.assertTrue(type(fake_int6[0]) == str, msg="elementos do tipo int")

    # def test_fake_float(self):
    #     print("\n\nResults for FAKE_FLOAT method with different parameters")
    #     # print(fake_float(size=5))
    #     print(fake_float(size=5, min_size=2, max_size=4))
    #     print(fake_float(size=5, min_size=2, max_size=4, round=2))
    #     print(fake_float(size=5, min_size=2, max_size=4, string=True, algsize=12))
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_fake_float_normal(self):
    #     print("\n\nResults for FAKE_FLOAT_NORMAL with different parameters")
    #     print(fake_float_normal(size=5))
    #     print(fake_float_normal(size=5, mean=10000, std=3000))
    #     print(fake_float_normal(size=5, mean=10000, std=3000, round=2))
    #     print(fake_float_normal(size=10, mean=10000, std=3000, string=True, algsize=12))
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_fake_discrete(self):
    #     print("\n\nResults for FAKE_DISCRETE with different parameters")
    #     print(fake_discrete(size=5, distinct=["valor1","valor2","valor3"]))
    #     print(fake_discrete(size=5, distinct=[1, 2, "NULL"]))
    #     print(fake_discrete(size=5, distinct=["gado", "etherium", "bitcoin"]))
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_fake_alphanum(self):
    #     print("\n\nResults for FAKE_ALPHANUM with different parameters")
    #     print(fake_alphanum(size=5, format="abc123"))
    #     print(fake_alphanum(size=5, format="22123"))
    #     print(fake_alphanum(size=5, format="abcb"))
    #     self.assertFalse('Foo'.isupper())
    #
    # def test_fake_date(self):
    #     print("\n\nResults for FAKE_ALPHANUM with different parameters")
    #     print(fake_date(size=5, start="06-02-2020", end="08-02-2020", format="%d-%m-%Y"))
    #     print(fake_date(size=5, start="06-02/2020", end="08/02-2020",format="%d %m %Y"))
    #     print(fake_date(size=5, start="01/20/2021", end="12-20-2021",format=["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y"]))
    #     self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()
