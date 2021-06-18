from numpy.random import randint
from dateutil import parser
from datetime import datetime
import unittest
from perform import performance
import numpy as np


# @performance
def fake_partition(size=5, **kwargs):
    interval = parser.parse(kwargs["start"]).timestamp(), parser.parse(kwargs["end"]).timestamp() \
        if kwargs.get("start") and kwargs.get("start") else (100000000, 100010000)
    # int_array = randint(interval[0], interval[1], size)
    times = np.linspace(interval[0], interval[1], kwargs["num_part"] if kwargs.get("num_part") else 2)
    return [datetime.fromtimestamp(i).strftime("%d-%m-%Y") for i in times]
    # if type(kwargs.get("format")) is list:
    #     return [datetime.fromtimestamp(i).strftime(kwargs["format"][randint(0, len(kwargs["format"]))])
    #             for i in int_array]
    # elif type(kwargs.get("format")) is str:
    #     return [datetime.fromtimestamp(i).strftime(kwargs["format"]) for i in int_array]
    # return [datetime.fromtimestamp(i).strftime("%d-%m-%Y") for i in int_array]


class TestCoreMethods(unittest.TestCase):

    def test_fake_date1(self):
        print("\n\nResults for FAKE_PARTITION with different parameters")
        a = fake_partition(size=10, part_type="date", start="07-05-2011", end="07-05-2018", num_part=30)
        print(a)


if __name__ == '__main__':
    unittest.main()