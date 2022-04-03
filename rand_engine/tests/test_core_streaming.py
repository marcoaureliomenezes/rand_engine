from core_streaming import *
from templates import *
from utils import loop_complexity
import unittest


class TestCoreMethods(unittest.TestCase):


    def test_gen_int(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_int(min=expected_min, max=expected_max)
        assert min(real_result) == expected_min
        assert max(real_result) == expected_max

    def test_gen_int10(self):
        expected_min, expected_max = (7, 10)
        real_result = gen_int10(min=expected_min, max=expected_max)
        print(real_result)

    def test_gen_value(self):
        expected_length = 5
        #real_result = gen_int(min=expected_min, max=expected_max)

    def test_gen_str_num(self):
        expected_length = 5
        real_result = gen_str_num(expected_length)

    def test_gen_float(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_float(min=expected_min, max=expected_max)

    def test_gen_money(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_money(min=expected_min, max=expected_max)


    def test_gen_distinct(self):
        expected_values = ['value1', 'value2']
        real_result = gen_distinct(distinct=expected_values)
        assert real_result in expected_values

    def test_gen_discrete(self):
        expected_min, expected_max = (0, 5)
        # real_result = gen_int(min=expected_min, max=expected_max)

    def test_date(self):
        start_date, formato = ('05-07-1991', '%d-%m-%Y')
        real_result = gen_date(start=start_date, formato=formato)
        print(real_result)

    def test_gen_date_oper(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_int(min=expected_min, max=expected_max)

    def test_gen_diff_day(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_int(min=expected_min, max=expected_max)

    def test_date(self):
        expected_min, expected_max = (0, 5)
        real_result = gen_int(min=expected_min, max=expected_max)



if __name__ == '__main__':
    unittest.main()