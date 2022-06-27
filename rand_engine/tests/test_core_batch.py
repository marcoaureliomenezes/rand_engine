from sqlalchemy import distinct
from core_batch import *
from templates import *
from utils import distinct_proportion
import unittest



class TestCoreMethods(unittest.TestCase):

    # def test_gen_ints(self):
    #     expected_size, expected_min, expected_max = (100, 0, 5)
    #     real_result = gen_ints(size=expected_size, min=expected_min, max=expected_max)
    #     assert len(real_result) == expected_size
    #     assert min(real_result) == expected_min
    #     assert max(real_result) == expected_max


    # def test_gen_ints10(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = gen_ints10(size=expected_size, min=expected_min, max=expected_max)
    #     assert len(real_result) == expected_size
    #     # assert min(real_result) == expected_min
    #     assert max(real_result) < 10**expected_max + 1


    # def test_fake_ints(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = fake_ints(size=expected_size, min=expected_min, max=expected_max)
    #     assert len(real_result) == expected_size
    #     # assert min(real_result) == expected_min
    #     assert max(real_result) < 10**expected_max + 1


    # def test_gen_floats(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = gen_floats(size=expected_size, min=expected_min, max=expected_max)
    #     print(real_result)


    # def test_gen_floats10(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = gen_floats10(size=expected_size, min=expected_min, max=expected_max)
    #     print(real_result)


    # def test_gen_floats_normal(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = gen_floats_normal(size=expected_size, mean=expected_min, std=expected_max)
    #     print(real_result)


    # def test_fake_floats(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = fake_ints(size=expected_size, min=expected_min, max=expected_max)


    # def test_random_float(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     real_result = gen_floats(size=expected_size, min=expected_min, max=expected_max)
    #     print(real_result)


    # def test_gen_distincts(self):
    #     expected_size, distinct = (100, ['value1', 'value2'])
    #     real_result = gen_distincts(size = expected_size, distinct=distinct)


    # def test_fake_discrete(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     # real_result = fake_discrete(size=expected_size, min=expected_min, max=expected_max)


    # def test_fake_discrete_format(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     # real_result = fake_discrete_format()


    # def test_gen_dates(self):
    #     expected_size, expected_min, expected_max = (100, 5, 6)
    #     #real_result = gen_dates(size=expected_size, min=expected_min, max=expected_max)


    def test_create_table(self):
        metadata = dict(
            nome = dict(method="fake_discrete", formato="x x", key="x", 
                params=[
                    {'how': "fake_discrete", 'distinct': ["marco", "jose", "ruth"]},
                    {'how': "fake_discrete", 'distinct': ["pereira", "cardoso", "souza"]}
            ]),
            cpf= dict(formato="x.x.x-x", sep="x", 
                params=[
                    {"how": "gen_str_num", 'params': {"length": 3}},
                    {"how": "gen_str_num", 'params': {"length": 3}},
                    {"how": "gen_str_num", 'params': {"length": 3}},
                    {"how": "gen_str_num", 'params': {"length": 2}}
            ]),
            possui_conta_corrente =  dict(method="fake_discrete", distinct=distinct_proportion(prop_false=0, prop_true=1)),
            possui_poupanca =  dict(method="fake_discrete", distinct=distinct_proportion(prop_false=3, prop_true=2)),
            idade = dict(method='fake_ints', min=0, max=100),
            saldo = dict(method='fake_floats', min=0, max=100),
            data_entrada = dict(method='fake_dates', start="01-01-2010",end="31-12-2020", formato="%d-%m-%Y")
        )

        table_data = create_table(10**6, metadata=metadata)

if __name__ == '__main__':
    unittest.main()