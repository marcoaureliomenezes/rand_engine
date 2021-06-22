from numpy.random import randint
from dateutil import parser
from datetime import datetime
import unittest
from perform import performance


@performance
def fake_date1(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else (100000000, 100010000)
    int_array = randint(interval[0], interval[1], size)

    if type(kwargs.get("format")) is list:
        return [datetime.fromtimestamp(i).strftime(kwargs["format"][randint(0, len(kwargs["format"]))])
                for i in int_array]
    elif type(kwargs.get("format")) is str:
        return [datetime.fromtimestamp(i).strftime(kwargs["format"]) for i in int_array]
    return [datetime.fromtimestamp(i).strftime("%d-%m-%Y") for i in int_array]

@performance
def fake_date2(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") is not None and kwargs.get("start") is not None else (100000000, 100010000)
    int_array = randint(interval[0], interval[1], size)
    return [datetime.fromtimestamp(i).strftime(kwargs["format"]) if type(kwargs.get("format")) is str
            else (datetime.fromtimestamp(i).strftime(kwargs["format"][randint(0, len(kwargs["format"]))])
            if type(kwargs.get("format")) is list else
            datetime.fromtimestamp(i).strftime("%d-%m-%Y")) for i in int_array]


class TestCoreMethods(unittest.TestCase):

    def test_fake_date1(self):
        print("\n\nResults for FAKE_DATE with different parameters")
        # fake_date1(size=1000000, start="01/20/2021", end="12-20-2021")
        fake_date1(size=1000000, start="01/20/2021", end="12-20-2021", format="%d/%m/%Y")
        # fake_date1(size=1000000, start="01/20/2021", end="12-20-2021",format=["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y"])
        self.assertFalse('Foo'.isupper())

    def test_fake_date2(self):
        print("\n\nResults for FAKE_DATE with different parameters")
        # fake_date2(size=1000000, start="01/20/2021", end="12-20-2021")
        fake_date2(size=1000000, start="01/20/2021", end="12-20-2021", format="%d/%m/%Y")
        # fake_date2(size=1000000, start="01/20/2021", end="12-20-2021",format=["%d-%m-%Y", "%d/%m/%Y", "%d %m %Y"])
        self.assertFalse('Foo'.isupper())


if __name__ == '__main__':
    unittest.main()