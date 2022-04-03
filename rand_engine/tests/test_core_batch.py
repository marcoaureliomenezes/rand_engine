from core_batch import *
from templates import *
from utils import loop_complexity
import unittest


class TestCoreMethods(unittest.TestCase):

    def test_gen_ints(self):
        expected_size, expected_min, expected_max = (100, 0, 5)
        real_result = gen_ints(size=expected_size, min=expected_min, max=expected_max)
        assert len(real_result) == expected_size
        assert min(real_result) == expected_min
        assert max(real_result) == expected_max


    def test_gen_ints10(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_ints10(size=expected_size, min=expected_min, max=expected_max)
        assert len(real_result) == expected_size
        # assert min(real_result) == expected_min
        assert max(real_result) < 10**expected_max + 1


    def test_fake_ints(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = fake_ints(size=expected_size, min=expected_min, max=expected_max)
        assert len(real_result) == expected_size
        # assert min(real_result) == expected_min
        assert max(real_result) < 10**expected_max + 1


    def test_gen_floats(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_floats(size=expected_size, min=expected_min, max=expected_max)
        print(real_result)


    def test_gen_floats10(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_floats10(size=expected_size, min=expected_min, max=expected_max)
        print(real_result)


    def test_gen_floats_normal(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_floats_normal(size=expected_size, min=expected_min, max=expected_max)
        print(real_result)


    def test_fake_floats(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = fake_ints(size=expected_size, min=expected_min, max=expected_max)


    def test_random_float(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_floats(size=expected_size, min=expected_min, max=expected_max)
        print(real_result)


    def test_gen_distincts(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        real_result = gen_distincts(distinct=['value1', 'value2'])


    def test_fake_discrete(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        # real_result = fake_discrete(size=expected_size, min=expected_min, max=expected_max)


    def test_fake_discrete_format(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        # real_result = fake_discrete_format()


    def test_gen_dates(self):
        expected_size, expected_min, expected_max = (100, 5, 6)
        #real_result = gen_dates(size=expected_size, min=expected_min, max=expected_max)


    def test_create_table(self):
        metadata_1 = dict(
            names=["email", "cpf", "cnpj", "saldo", "data_nascimento"],
            data = [
                template_batch('email'),
                template_batch('cpf'),
                template_batch('cnpj'),
                dict(method='fake_float', min=0, max=100),
                dict(method='fake_date', start="01-01-2010", end="31-12-2020", formato="%d-%m-%Y")
            ])

        table = create_table(10, **metadata_1)
        print(table)

        loop_complexity(create_table, size=10**6, **metadata_1)

if __name__ == '__main__':
    unittest.main()