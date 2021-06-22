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
    times = list(np.linspace(interval[0], interval[1], kwargs["num_part"] if kwargs.get("num_part") else 2))
    if kwargs["num_part"] >= size:
        test = [int(i) for i in np.linspace(0, size-1, len(times))]
        selected = [test.index(i) for i in range(size)]
        result = [times[i] for i in selected]
    else:
        count1=0; count2=0; vect = []
        while count1 < size:
            vect.append(times[count2])
            count1 += 1 ; count2 += 1
            count2 = 0 if count2 >= (len(times) - 1) else count2
        vect.sort()
        result = vect

    return [datetime.fromtimestamp(i).strftime("%d-%m-%Y") for i in result]
  
class TestCoreMethods(unittest.TestCase):

    def test_fake_date1(self):
        print("\n\nResults for FAKE_PARTITION with different parameters")
        a = fake_partition(size=40, part_type="date", start="07-05-2011", end="07-05-2018", num_part=5)
        print(a)


if __name__ == '__main__':
    unittest.main()