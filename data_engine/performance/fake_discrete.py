from numpy.random import randint
from functools import reduce
from perform import performance
import numpy as np
from utils import *

# @performance
def fake_discrete(size=5, **kwargs):
    if type(kwargs.get("distinct")) is not list:
        return ["" for i in range(size)]

    if len(kwargs.get("distinct")) > 0 and type(kwargs.get("distinct")[0]) is list:
        result = random_multi_word(size, values=kwargs["distinct"])

    elif type(kwargs.get("distinct") is str):
        result = random_single_word(size, values=kwargs["distinct"])
    result = replace_duplicate(result, None) if kwargs.get("rm_dupl") else result
    result = change_case(result, method=str.capitalize) if kwargs.get("case") == "cap" else result
    result = change_case(result, method=str.lower) if kwargs.get("case") == "lower" else result
    return change_case(result, method=str.upper) if kwargs.get("case") == "upper" else result

    
# @performance
def fake_alphanum(size=5, **kwargs):
    if not kwargs.get("format"):
        return ["" for i in range(size)]
    result = reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
    np.array([np.array([chr(i) for i in randint(97,123, size)]
                if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
                for i in kwargs["format"]], dtype=object))
    result = change_case(result, method=str.capitalize) if kwargs.get("let_case") == "cap" else result
    result = change_case(result, method=str.lower) if kwargs.get("let_case") == "lower" else result
    return change_case(result, method=str.upper) if kwargs.get("let_case") == "upper" else result


import unittest

class TestCoreMethods(unittest.TestCase):

    nome1 = ["marco","joão","marcos","flávio","luiz","marcio",
                "pedro","josé", "felipe","filipe"]
    nome2 = ["aurélio","augusto","paulo","calebe","vinicius",
                "otávio","daniel","gustavo","gabriel","ricardo"]
    nome3 = ["guimarães","machado","reis","sarmento","correia",
            "gonçalves","pereira","costa","galvão","schmidt"]
    nome4 = ["fernandes","lima", "correia", "ribeiro","mesquita",
                "cardoso","peixoto","nunes","santos","alves"]
    total = [nome1, nome2, nome3, nome4, ]
    def test_fake_discrete(self):
        print(fake_discrete(size=5, distinct=["felipe", "marcelo"]))
        print(fake_discrete(size=5, distinct=["felipe", "marcelo"], rm_dupl=True))
        print(fake_discrete(size=5, distinct=[["marco", "luiz"], ["paulo","marco"]]))
        print(fake_discrete(size=5, distinct=[["marco", "luiz"], ["paulo","marco"]], rm_dupl=True))
        # fake_discrete(size=1000000, distinct=["valor-1","valor-2"])
        # fake_discrete(size=1000000, distinct=["valor-1","valor-2"], rm_dupl=True)
        # fake_discrete(size=1000000, distinct=[["valor-1","valor-2"],["valor-3","valor-4"]])
        # fake_discrete(size=1000000, distinct=[["valor-1","valor-2"],["valor-3","valor-4"]], rm_dupl=True)
        # fake_discrete(size=1000000, distinct=self.total)
        # fake_discrete(size=1000000, distinct=self.total, rm_dupl=True)
        self.assertFalse('Foo'.isupper())

    def test_fake_alphanum(self):
        print("\ntest alphanumeric method 2: ")
        print(fake_alphanum(size=5, format="aa22bb"))
        print(fake_alphanum(size=5, format="bb22aa", let_case="lower"))
        print(fake_alphanum(size=5, format="abc123", let_case="upper"))
        print(fake_alphanum(size=5, format="abc123", let_case="cap"))
        # fake_alphanum_2(size=1000000)
        # a = fake_alphanum_2(size=1000000, format="abc123")
        # print("5 primeiros valores: ", a[0:5])
        self.assertFalse('Foo'.isupper())
if __name__ == '__main__':
    unittest.main()