import pytest

from benchmarks.speed import compare

BASELINE = [
  {"method": "integers", "rows": 10**6, "get_df_s": 1.0},
  {"sink": "csv", "rows": 10**6, "sink_s": 2.0},
]


@pytest.mark.parametrize("current, failed", [
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.29}], []),
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.3}], []),
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.31}], [("integers", 10**6)]),
  ([{"sink": "csv", "rows": 10**6, "sink_s": 2.58}], []),
  ([{"sink": "csv", "rows": 10**6, "sink_s": 2.62}], [("csv", 10**6)]),
])
def test_compare_fails_only_rows_over_1_3x_baseline(current, failed):
  assert compare(current, BASELINE) == (failed, [])


def test_compare_reports_unbaselined_row_without_failing():
  current = [{"method": "uuid4", "rows": 10**7, "get_df_s": 99.0}]
  assert compare(current, BASELINE) == ([], [("uuid4", 10**7)])
