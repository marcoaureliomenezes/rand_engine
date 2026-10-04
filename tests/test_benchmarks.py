import pytest

from benchmarks.speed import attach_base, check_tree, compare, plan_keys

BASE = [
  {"method": "integers", "rows": 10**6, "get_df_s": 1.0},
  {"sink": "csv", "rows": 10**6, "sink_s": 2.0},
]


@pytest.mark.parametrize("head, failed", [
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.29}], []),
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.3}], []),
  ([{"method": "integers", "rows": 10**6, "get_df_s": 1.31}], [("integers", 10**6)]),
  ([{"sink": "csv", "rows": 10**6, "sink_s": 2.58}], []),
  ([{"sink": "csv", "rows": 10**6, "sink_s": 2.62}], [("csv", 10**6)]),
])
def test_compare_fails_only_head_over_base_ratio_above_1_3(head, failed):
  assert compare(head, BASE) == (failed, [])


def test_compare_reports_row_the_base_lacks_without_failing():
  head = [{"method": "uuid4", "rows": 10**7, "get_df_s": 99.0}]
  assert compare(head, BASE) == ([], [("uuid4", 10**7)])


def test_check_tree_exits_3_on_a_foreign_rand_engine():
  with pytest.raises(SystemExit) as e:
    check_tree("/head/rand_engine/__init__.py", "/base")
  assert e.value.code == 3


def test_check_tree_accepts_the_expected_tree():
  check_tree("/base/rand_engine/__init__.py", "/base")


def test_check_tree_accepts_a_relative_expected_tree(tmp_path, monkeypatch):
  (tmp_path / "head").mkdir()
  monkeypatch.chdir(tmp_path / "head")
  check_tree(f"{tmp_path}/base/rand_engine/__init__.py", "../base")


def test_base_pass_skips_keys_the_tree_lacks_and_marks_base_only_keys_deleted():
  assert plan_keys(["integers", "uuid4"], ["integers", "gone"], base_pass=True) == (["integers"], {"gone": "deleted in head"})


def test_head_pass_exits_naming_a_method_sample_kwargs_lacks():
  with pytest.raises(SystemExit) as e:
    plan_keys(["integers"], ["integers", "new_method"], base_pass=False)
  assert "new_method" in str(e.value.code)


def test_attach_base_copies_same_job_base_times_onto_head_rows():
  head = [{"method": "integers", "rows": 10**6, "get_df_s": 1.1}, {"sink": "csv", "rows": 10**6, "sink_s": 2.2},
          {"method": "uuid4", "rows": 10**6, "get_df_s": 3.0}]
  attach_base(head, BASE)
  assert head == [{"method": "integers", "rows": 10**6, "get_df_s": 1.1, "base_get_df_s": 1.0},
                  {"sink": "csv", "rows": 10**6, "sink_s": 2.2, "base_sink_s": 2.0},
                  {"method": "uuid4", "rows": 10**6, "get_df_s": 3.0}]
