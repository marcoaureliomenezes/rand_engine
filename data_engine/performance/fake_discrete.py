from numpy.random import randint
from functools import reduce
from perform import performance

from utils import replace_duplicate

@performance
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


import unittest

class TestCoreMethods(unittest.TestCase):


    def test_fake_discrete(self):
        print(fake_discrete(size=5, distinct=["val-1", "val-2"], rm_dupl=True))
        print(fake_discrete(size=5, distinct=[["val-1", "val-2"], ["val-3","val-4"]], rm_dupl=True))
        # fake_discrete(size=1000000)
        # fake_discrete(size=1000000, distinct=["valor-1","valor-2"], rm_dupl=True)
        # fake_discrete(size=1000000, distinct=[["felipe", "marcelo"], ["ferreira","peixoto"]], rm_dupl=True)
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()