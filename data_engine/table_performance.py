from table import *
from performance import loop_complexity
from names import *
import unittest
from names import names, last_names


class TestTablePerformanceMethods(unittest.TestCase):
    size = 100000
    def test_int_table_performance(self):
        metadata = dict(
            names=["fake_int1", "fake_int2", "fake_int3", "fake_int4"],
            data=[
                dict(method="fake_int"),
                dict(method="fake_int", min=10, max=20),
                dict(method="fake_int", min=4, max=7, algnum=True),
                dict(method="fake_int", min=4, max=7, algnum=True, algsize=10),
            ]
        )
        loop_complexity(create_table, size=self.size, **metadata)

    def test_float_table_performance(self):
        metadata = dict(
            names=["fake_float1","fake_float2","fake_float3", "fake_normal1", "fake_normal2", "fake_float4","fake_float5"],
            data=[
                dict(method="fake_float"),
                dict(method="fake_float", min=10, max=20),
                dict(method="fake_float", min=10, max=20, round=2),
                dict(method="fake_float", mean=100., std=20., type="normal", round=2),
                dict(method="fake_float", mean=100., std=20., type="normal", round=2, outlier=True),
                dict(method="fake_float", min=10, max=20, round=2, outlier=True),
                dict(method="fake_float", min=5, max=7, round=2, algnum=True),
            ]
        )
        loop_complexity(create_table, size=self.size, **metadata)

    def test_discrete_table_performance(self):
        metadata = dict(
            names=["fake_discrete1", "fake_discrete2", "fake_discrete3",
            "fake_discrete4", "fake_discrete5", "fake_discrete6"],
            data=[
                dict(method="fake_discrete", distinct=["bitcoin","etherium", "ripple"] ),
                dict(method="fake_discrete", distinct=names),
                dict(method="fake_discrete", distinct=[names, last_names]),
            ]
        )
        loop_complexity(create_table, size=self.size, **metadata)



if __name__ == '__main__':
    unittest.main()