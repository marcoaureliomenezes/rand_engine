import time, sys, re, itertools, random
from functools import reduce
import numpy as np
from numpy.random import randint
from perform import performance 



@performance
def fake_name(size=5, **kwargs):
    if kwargs["names"] and len(kwargs["names"]) > 0:
        result = [[ arg[j] for j in randint(0, len(arg), size)] for arg in kwargs["names"]]
        return [reduce(lambda a, b: f"{a} {b}",fullname) for fullname in list(zip(*result))]
    return ["" for i in range(size)]

@performance
def fake_unique_name(size=5, **kwargs):
    """ fake_name creates an array of names with the size passed as parameter 

    Parameters:
    size (int): size of the output name array
    kwargs["names"] list(list(strings)): list of string lists representing composed name

    Returns:
    list(string):Returns a list of random names

    """
    if kwargs.get("names"):
        res = [reduce(lambda a, b: f"{a} {b}", i) for i in itertools.product(*kwargs["names"])]
        res = np.append(res, [None for i in range(size - len(res))]) if len(res) < size else \
                    res[0:size]
        np.random.shuffle(res)
        return res
    return ["" for i in range(size)]

import unittest

class TestCoreMethods(unittest.TestCase):

    name_dict = dict(
        nome1 = ["marco","joão","marcos","flávio","luiz","marcio",
                 "pedro","josé", "felipe","filipe"],
        nome2 = ["aurélio","augusto","paulo","calebe","vinicius",
                 "otávio","daniel","gustavo","gabriel","ricardo"],
        nome3 = ["guimarães","machado","reis","sarmento","correia",
                "gonçalves","pereira","costa","galvão","schmidt"],
        nome4 = ["fernandes","lima", "correia", "ribeiro","mesquita",
                 "cardoso","peixoto","nunes","santos","alves"],
        nome5 = ["menezes","gutierres","catapreta","martins","marinho",
                 "jesus","marques","gusmão","betonni", "andrade"] , 
        nome6 = ["junior","filho","neto","primo","delgrado","II", 
                 "netto","júnior", "lock", "mineiro"]

    )

    def test_fake_name(self):
        print(fake_name(size=70, names=[*self.name_dict.values()]))
        fake_name(size=1000000, names=[*self.name_dict.values()])
        self.assertFalse('Foo'.isupper())


    def test_fake_unique_name(self):
        print(fake_unique_name(size=70, names=[*self.name_dict.values()]))
        fake_unique_name(size = 1000000, names=[*self.name_dict.values()])
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()