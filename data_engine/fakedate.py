from numpy.random import randint
import unittest
from core import get_interval, expand_array, reduce_array, format_date_array, \
                spaced_array, handle_format

def fake_date(size=5, **kwargs):
    if not (kwargs.get("start") and kwargs.get("end")):
        return ["" for i in range(size)]
    interval = get_interval(start=kwargs["start"], end=kwargs["end"])
    int_array = randint(interval[0], interval[1], size)
    format = handle_format(kwargs.get("format"))
    return format_date_array(int_array, format)


def fake_partition(size=5, **kwargs):
    if not (kwargs.get("start") and kwargs.get("end")):
        return ["" for i in range(size)]
    interval = get_interval(kwargs["start"], kwargs["end"])
    num_part = kwargs["num_part"] if kwargs.get("num_part") else 2    
    times = spaced_array(interval, num_part)

    result = reduce_array(size, base_array=times) if kwargs.get("num_part") >= size \
        else expand_array(size=size, base_array=times)

    format = kwargs["format"] if kwargs.get("format") else "%d-%m-%Y"
    return format_date_array(result, format)


#################################################################################################


class TestCoreMethods(unittest.TestCase):


    def test_fake_date0(self):
        print("\n\nTEST FAKE_DATE METHOD")
        fake_date0 = fake_date()
        print("\nfake_date sem parâmetros (size=5 por default)\n\t", fake_date0)
        self.assertFalse('Foo'.isupper())
    
    def test_fake_date1(self):
        fake_date1 = fake_date(size=10)
        print("\nfake_alphanum com parâmetro size=10\n\t", fake_date1)
        self.assertFalse('Foo'.isupper())

    def test_fake_date2(self):
        fake_date2 = fake_date(size=5, start="01/20/2021", end="12-20-2021")
        print("\nfake_alphanum com parâmetros size=10, start=01/20/2020, end=12-20-2021\n\t", fake_date2)
        self.assertFalse('Foo'.isupper())

    def test_fake_date3(self):
        fake_date3 = fake_date(size=5, start="01/20/2021", end="12-20-2021", format="%d/%m/%Y")
        print("\nfake_alphanum com parâmetros size=10, start=01/20/2020, end=12-20-2021 e format='day/month/year\n\t", fake_date3)
        self.assertFalse('Foo'.isupper())

    def test_fake_date4(self):
        fake_date4 = fake_date(size=5, start="01/20/2021", end="12-20-2021",format=["%d-%m-%Y", "%d/%m/%Y", "%d@%m@%Y"])
        print("\nfake_alphanum com parâmetros size=10, start=01/20/2020, end=12-20-2021 e format=multiple formats\n\t", fake_date4)
        self.assertFalse('Foo'.isupper())
        print("\n--------------------------------------------------------------------------------------\n")

    def test_fake_partition0(self):
        print("\n\nTEST FAKE_PARTITION METHOD")
        fake_partition0 = fake_partition(size=8, part_type="date", start="07-05-2020", end="07-05-2021", num_part=3)
        print("\nfake_partition com parâmetros com parâmetro start=07-05-2020, end=07-05-2021 e num_part=2\n\t", fake_partition0)
        self.assertFalse('Foo'.isupper())

    def test_fake_partition1(self):
        fake_partition1 = fake_partition(size=8, part_type="date", start="07-05-2011", end="07-05-2018", num_part=20)
        print("\nfake_partition com parâmetros start=07-05-2020, end=07-05-2021, num_part=2\n\t", fake_partition1)
        self.assertFalse('Foo'.isupper())

    def test_fake_partition2(self):
        print("\n\nTEST FAKE_PARTITION METHOD")
        fake_partition2 = fake_partition(size=5, part_type="date", start="07-05-2020", end="07-05-2021", num_part=10, format="%d/%m/%Y")
        print("\nfake_partition com parâmetros start=07-05-2020, end=07-05-2021, num_part=2 e format=%d/%m/%Y\n\t", fake_partition2)
        self.assertFalse('Foo'.isupper())

if __name__ == '__main__':
    unittest.main()