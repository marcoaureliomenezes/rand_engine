import random, math, itertools, unittest
from numpy.random import rand, randint
import numpy as np
from functools import reduce
from .core import random_single_word, random_multi_word, replace_duplicate, change_case


def fake_discrete(size=5, **kwargs):
    if type(kwargs.get("distinct")) is not list:
        return ["" for i in range(size)]
    if len(kwargs.get("distinct")) > 0 and type(kwargs.get("distinct")[0]) is list:
        result = random_multi_word(size, values=kwargs["distinct"])
    elif type(kwargs.get("distinct") is str):
        result = random_single_word(size, values=kwargs["distinct"])
    result = replace_duplicate(result, None) if kwargs.get("rm_dupl") else result
    result = change_case(result, method=str.capitalize) if kwargs.get("let_case") == "cap" else result
    result = change_case(result, method=str.lower) if kwargs.get("let_case") == "lower" else result
    return change_case(result, method=str.upper) if kwargs.get("let_case") == "upper" else result


def fake_concat(*args, **kwargs):
    sep = kwargs["sep"] if type(kwargs.get("sep")) is str else ""
    res =  list(zip(*args))
    res2 = [reduce(lambda a, b: f"{a}{sep}{b}", i) for i in res]
    return res2

def fake_alphanum(size=5, **kwargs):
    if not kwargs.get("format"):
        return ["" for i in range(size)]
    result = reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
    np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in kwargs["format"]], dtype=object))
    result = fake_concat(fake_discrete(size=size, **kwargs), result, **kwargs) if kwargs.get("distinct") else result
    result = replace_duplicate(result, None) if kwargs.get("rm_dupl") else result
    result = change_case(result, method=str.capitalize) if kwargs.get("let_case") == "cap" else result
    result = change_case(result, method=str.lower) if kwargs.get("let_case") == "lower" else result
    return change_case(result, method=str.upper) if kwargs.get("let_case") == "upper" else result

# def fake_name_alphanum(size, **kwargs):
#     elem1 = fake_discrete(size=size, **kwargs)
#     elem2 = fake_alphanum(size=size, **kwargs)
#     sep = kwargs["sep"] if type(kwargs.get("sep")) is str else "-"
#     res = [ f"{i}{sep}{j}" for i, j in zip(elem1, elem2)]
#     print(res)

######################################################################################################

class TestCoreMethods(unittest.TestCase):

    def test_fake_discrete0(self):
        print("\n\nTEST FAKE_DISCRETE METHOD\n")
        fake_discrete0 = fake_discrete()
        print("fake_discrete sem parâmetros\n\t", fake_discrete0)
        self.assertFalse('Foo'.isupper())
   
    def test_fake_discrete1(self):
        print("\n\nTEST FAKE_DISCRETE METHOD\n")
        fake_discrete1 = fake_discrete(size=10)
        print("fake_discrete com parametro size=10\n\t", fake_discrete1)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete2(self):
        fake_discrete2 = fake_discrete(size=10, distinct=["pedro","lucas","marcus"])
        print("\nfake_discrete com parametros size=10, list of names\n\t", fake_discrete2)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete3(self):
        fake_discrete3 = fake_discrete(size=10, distinct=[["pedro","lucas","marcus"], ["pereira","rocha"]], rm_dupl=True)
        print("\nfake_discrete com parametros size=10, 2 listas de nomes e rm_dupl=True\n\t", fake_discrete3)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete4(self):
        fake_discrete4 = fake_discrete(size=10, distinct=[["pedro","lucas","marcus"], ["pereira","rocha"]], let_case="cap")
        print("\nfake_discrete com parametros size=10, 2 listas de nomes e case=capitalize\n\t", fake_discrete4)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete5(self):
        fake_discrete5 = fake_discrete(size=10, distinct=[["pedro","lucas","marcus"], ["pereira","rocha"]], let_case="lower")
        print("\nfake_discrete com parametros size=10, 2 listas de nomes e case=lower\n\t", fake_discrete5)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete6(self):
        fake_discrete6 = fake_discrete(size=10, distinct=[["pedro","lucas","marcus"], ["pereira","rocha"]], let_case="upper")
        print("\nfake_discrete com parametros size=10, 2 listas de nomes e case upper\n\t", fake_discrete6)
        self.assertFalse('Foo'.isupper())

    def test_fake_discrete7(self):
        fake_discrete7 = fake_discrete(size=10, distinct=[
            ["marco","pedro","lucas","jesus","cibele","fabio","rafael","henrique", "caina","rubens"],
            ["rocha","pereira","lima","reis","duarte","barbosa","souza","lopes","perez","rodrigues"]
        ])
        print("\nfake_discrete com 2 listas de 10 nomes cada (100 nomes de combinação\n\t", fake_discrete7)
        print("\n------------------------------------------------------------------------------------\n")
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum0(self):
        print("\n\nTEST FAKE_ALPHANUM METHOD")
        fake_alphanum0 = fake_alphanum()
        print("\nfake_alphanum sem parâmetros (size=5 por default)\n\t", fake_alphanum0)
        self.assertFalse('Foo'.isupper())
    
    def test_fake_alphanum1(self):
        fake_alphanum1 = fake_alphanum(size=10)
        print("\nfake_alphanum com parametro size=10\n\t", fake_alphanum1)
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum2(self):
        fake_alphanum2 = fake_alphanum(size=10, format="aa22bb")
        print("\nfake_alphanum com format='aa22bb'\n\t", fake_alphanum2)
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum3(self):
        fake_alphanum3 = fake_alphanum(size=10, format="aa22bb", let_case="lower")
        print("\nfake_alphanum com format='aa22bb' e case=lower\n\t", fake_alphanum3)
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum4(self):
        fake_alphanum4 = fake_alphanum(size=10, format="aa22bb", let_case="upper")
        print("\nfake_alphanum com format='aa22bb' e case=upper\n\t", fake_alphanum4)
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum5(self):
        fake_alphanum5 = fake_alphanum(size=10, format="aa22bb", let_case="cap")
        print("\nfake_alphanum com format='aa22bb' e case=capitalize\n\t", fake_alphanum5)
        print("\n------------------------------------------------------------------------------------\n")
        self.assertFalse('Foo'.isupper())

    def test_fake__name_alphanum(self):
        fake_name_alphanum1 = fake_concat(fake_discrete(size=10, distinct=["vale", "petr", "appl","msft","spcx"]), fake_alphanum(size=10, format="a22bb", let_case="upper", sep="*"))
        print("\nfake_name_alphanum\n\t", fake_name_alphanum1)
if __name__ == '__main__':
    unittest.main()