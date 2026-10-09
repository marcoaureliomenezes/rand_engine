import json
import os
import time
from pathlib import Path

import pytest

import benchmarks.speed as speed
from benchmarks.speed import baseline, check_tree, compare, parse_reply, plan_keys, run, Worker
from rand_engine.validators.method_specs import METHOD_CATALOG, NUMPY

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


def test_compare_gates_ab_records_on_their_own_base_times():
  records = [{"method": "integers", "rows": 10, "get_df_s": 1.31, "base_get_df_s": 1.0},
             {"sink": "csv", "rows": 10, "sink_s": 1.29, "base_sink_s": 1.0},
             {"method": "uuid4", "rows": 10, "get_df_s": 5.0}]
  assert compare(records, baseline(records)) == ([("integers", 10)], [("uuid4", 10)])


def test_existing_same_method_regression_limit_remains_1_3():
  assert speed.LIMIT == 1.3


def test_benchmark_inventory_covers_every_numpy_catalog_method():
  expected = {name for name, spec in METHOD_CATALOG.items() if NUMPY in spec.engines}
  assert set(speed.SAMPLE_KWARGS) == expected


@pytest.mark.parametrize(("method", "sibling"), [
  ("exponential", "floats"),
  ("lognormal", "floats_normal"),
  ("poisson", "integers"),
  ("zipf", "integers"),
])
def test_new_distribution_nearest_sibling_limit_is_1_5(method, sibling):
  siblings = getattr(speed, "METHOD_SIBLINGS", None)
  compare_siblings = getattr(speed, "compare_siblings", None)
  assert siblings is not None
  assert compare_siblings is not None
  assert siblings[method] == sibling

  boundary = [
    {"method": sibling, "rows": 10**6, "get_df_s": 2.0},
    {"method": method, "rows": 10**6, "get_df_s": 3.0},
  ]
  over = [{**row, "get_df_s": 3.01} if row["method"] == method else row for row in boundary]
  assert compare_siblings(boundary) == []
  assert compare_siblings(over) == [(method, 10**6)]


def test_official_run_enforces_the_new_distribution_sibling_limit(tmp_path):
  class SiblingWorker:
    keys = ("integers", "floats", "floats_normal", "exponential", "lognormal", "poisson", "zipf")
    returncode = None

    def ask(self, request):
      if "extra" in request:
        return {**request, "core_s": 0.5, "peak_mib": 2.0}
      seconds = {"floats": 1.0, "exponential": 1.51}.get(request["row"], 1.0)
      return {**request, "s": seconds}

    def reason(self):
      return "unexpected worker failure"

  with pytest.raises(SystemExit) as caught:
    speed.run(SiblingWorker(), None, [10], tmp_path, "no base tree")

  message = str(caught.value)
  assert "exponential" in message
  assert "1.5" in message
  assert "sibling" in message


def test_modifier_benchmark_inventory_is_literal():
  assert getattr(speed, "MODIFIERS", None) == {
    "null_rate": {"method": "integers", "null_rate": 0.1},
    "anomaly_rate": {
      "method": "integers",
      "anomaly_rate": 0.1,
      "anomaly_values": [-1],
    },
  }
  assert getattr(speed, "MODIFIER_LIMIT", None) == 1.25


def test_modifier_comparison_passes_at_1_25_and_fails_only_over():
  compare_modifiers = getattr(speed, "compare_modifiers", None)
  assert compare_modifiers is not None

  boundary = [
    {"method": "integers", "rows": 10**4, "get_df_s": 2.0},
    {"modifier": "null_rate", "method": "integers", "rows": 10**4, "get_df_s": 2.5},
    {"modifier": "anomaly_rate", "method": "integers", "rows": 10**4, "get_df_s": 2.5},
  ]
  over = [
    {**row, "get_df_s": 2.51} if row.get("modifier") == "anomaly_rate" else row
    for row in boundary
  ]
  assert compare_modifiers(boundary) == []
  assert compare_modifiers(over) == [("anomaly_rate", 10**4)]


def test_official_run_enforces_modifier_rows(tmp_path):
  class ModifierWorker:
    keys = ("integers",)
    returncode = None

    def ask(self, request):
      if "extra" in request:
        return {**request, "core_s": 0.5, "peak_mib": 2.0}
      seconds = {
        "null_rate": 1.25,
        "anomaly_rate": 1.26,
      }.get(request.get("modifier"), 1.0)
      return {**request, "s": seconds}

    def reason(self):
      return "unexpected worker failure"

  with pytest.raises(SystemExit) as caught:
    speed.run(ModifierWorker(), None, [10**4], tmp_path, "no base tree")

  report = json.loads((tmp_path / "benchmarks.json").read_text(encoding="utf-8"))
  modifier_rows = [record for record in report["records"] if "modifier" in record]
  assert [
    (record["modifier"], record["method"], record["rows"], record["get_df_s"])
    for record in modifier_rows
  ] == [
    ("null_rate", "integers", 10**4, 1.25),
    ("anomaly_rate", "integers", 10**4, 1.26),
  ]
  message = str(caught.value)
  assert "anomaly_rate" in message
  assert "1.25" in message
  assert "modifier" in message


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


def test_plan_keys_marks_base_only_deleted_and_head_only_added():
  assert plan_keys(["integers", "uuid4"], ["integers", "uuid4"], ["integers", "gone"]) == (
    ["integers", "uuid4"], {"gone": "deleted in head", "uuid4": "added in head"})


def test_plan_keys_exits_naming_a_head_method_sample_kwargs_lacks():
  with pytest.raises(SystemExit) as e:
    plan_keys(["integers"], ["integers", "new_method"], ["integers"])
  assert e.value.code == "SAMPLE_KWARGS lacks map_methods keys: ['new_method']"


@pytest.mark.parametrize("line, reply", [
  ('{"row": "csv", "rows": 10, "s": 1.5}\n', {"row": "csv", "rows": 10, "s": 1.5}),
  ('{"row": "csv", "rows": 11, "s": 1.5}\n', None),
  ('{"row": "json", "rows": 10, "s": 1.5}\n', None),
  ("Segmentation fault\n", None),
  ("", None),
])
def test_parse_reply_treats_unparseable_or_unechoed_lines_as_death(line, reply):
  assert parse_reply({"row": "csv", "rows": 10}, line) == reply


class Fake:
  """An in-process worker: logs every request, answers s = 1.0 (head 1.2, 1.2, 3.0 per row), extras {core_s, peak_mib}."""

  def __init__(self, name, log, keys=("integers",), fail=None, returncode=None):
    self.name, self.log, self.keys, self.fail, self.returncode = name, log, keys, fail or {}, returncode

  def ask(self, req):
    if "modifier" not in req: self.log.append((self.name, req))
    if (len(self.log), self.name) in self.fail: return self.fail[(len(self.log), self.name)]
    if "extra" in req: return {**req, "core_s": 0.5, "peak_mib": 2.0}
    return {**req, "s": 1.0 if self.name == "B" else [1.2, 1.2, 3.0][sum(n == "H" and r == req for n, r in self.log) % 3]}

  def reason(self):
    return "MemoryError: boom"


def ab(log, base=None, head=None, error=None, out=None, sizes=(10,)):
  run(head or Fake("H", log), base, list(sizes), out, error)
  report = json.loads((out / "benchmarks.json").read_text(encoding="utf-8"))
  # Legacy A/B protocol tests inspect ordinary rows; modifier tests read the raw artifact directly.
  report["records"] = [record for record in report["records"] if "modifier" not in record]
  return report, (out / "BENCHMARKS.md").read_text(encoding="utf-8")


@pytest.fixture(autouse=True)
def shas(monkeypatch):
  monkeypatch.setenv("HEAD_SHA", "h1"); monkeypatch.setenv("BASE_SHA", "b1"); monkeypatch.setenv("RUNNER_NAME", "r")


def test_run_alternates_six_timed_calls_per_row_then_head_extras_after_the_last_row(tmp_path):
  log = []
  report, md = ab(log, Fake("B", log), out=tmp_path)
  m, c = {"row": "integers", "rows": 10}, {"row": "csv", "rows": 10}
  assert log[:12] == [("B", m), ("H", m), ("B", m), ("H", m), ("B", m), ("H", m),
                      ("H", c), ("B", c), ("H", c), ("B", c), ("H", c), ("B", c)]
  assert len(log) == 5 * 6 + 1 and log[30] == ("H", {"extra": "integers", "rows": 10})
  assert report["commit"] == "h1" and report["base_commit"] == "b1"
  assert report["records"][0] == {"method": "integers", "rows": 10, "get_df_s": 1.2, "rows_per_us": 10 / 1.8e6,
                                  "base_get_df_s": 1.0, "core_s": 0.5, "peak_mib": 2.0}
  assert report["records"][1] == {"sink": "csv", "rows": 10, "sink_s": 1.2, "rows_per_us": 10 / 1.8e6, "base_sink_s": 1.0}
  assert "base rows 5/5\n" in md


def test_run_times_a_head_only_key_after_every_shared_row_with_no_base_request(tmp_path, monkeypatch):
  log = []
  monkeypatch.setattr("benchmarks.speed.SINKS", ())
  report, md = ab(log, Fake("B", log, keys=("integers", "booleans")), Fake("H", log, keys=("integers", "uuid4", "booleans")),
                  out=tmp_path)
  i, b, u = ({"row": k, "rows": 10} for k in ("integers", "booleans", "uuid4"))
  assert log == [("B", i), ("H", i), ("B", i), ("H", i), ("B", i), ("H", i),
                 ("H", b), ("B", b), ("H", b), ("B", b), ("H", b), ("B", b),
                 ("H", u), ("H", u), ("H", u),
                 ("H", {"extra": "integers", "rows": 10}), ("H", {"extra": "booleans", "rows": 10}),
                 ("H", {"extra": "uuid4", "rows": 10})]
  assert "base_get_df_s" not in report["records"][2] and report["records"][2]["core_s"] == 0.5
  assert "- `uuid4`: added in head\n" in md


def test_base_error_reply_leaves_that_row_absent_and_the_next_row_alternating(tmp_path):
  log = []
  report, md = ab(log, Fake("B", log, fail={(1, "B"): {"row": "integers", "rows": 10, "error": "ValueError: x"}}), out=tmp_path)
  assert [s for s, _ in log[:11]] == ["B", "H", "H", "H", "H", "B", "H", "B", "H", "B", "B"]
  assert "base_get_df_s" not in report["records"][0] and report["records"][1]["base_sink_s"] == 1.0
  assert "base rows 4/5\n- `integers`: base raised ValueError: x\n" in md


def test_base_eof_leaves_every_remaining_row_absent_with_base_pass_failed(tmp_path):
  log = []
  report, md = ab(log, Fake("B", log, fail={(8, "B"): None}), out=tmp_path)
  assert [s for s, _ in log].count("B") == 4
  assert [("base_get_df_s" in r or "base_sink_s" in r) for r in report["records"]] == [True, False, False, False, False]
  assert "base rows 1/5 · base pass failed: MemoryError: boom\n" in md


def test_no_base_tree_renders_every_row_absent(tmp_path):
  log = []
  report, md = ab(log, None, error="no base tree for commit ''", out=tmp_path, sizes=(10, 20))
  assert {s for s, _ in log} == {"H"}
  assert [(r.get("method") or r["sink"], r["rows"]) for r in report["records"]] == [
    ("integers", 10), ("integers", 20), ("csv", 10), ("parquet", 10), ("json", 10), ("stream_dict", 10)]
  assert "base rows 0/6 · base pass failed: no base tree for commit ''\n" in md


def test_base_returncode_3_exits_3_after_writing_the_table(tmp_path):
  log = []
  with pytest.raises(SystemExit) as e:
    ab(log, Fake("B", log, keys=None, returncode=3), out=tmp_path)
  assert e.value.code == 3
  assert "base pass failed: MemoryError: boom" in (tmp_path / "BENCHMARKS.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("head", [{"fail": {(2, "H"): None}}, {"keys": None}, {"keys": None, "returncode": 1},
                                  {"fail": {(2, "H"): {"row": "integers", "rows": 10, "error": "ValueError: x"}}}])
def test_head_error_or_eof_exits_non_zero(tmp_path, head):
  log = []
  with pytest.raises(SystemExit) as e:
    ab(log, Fake("B", log), Fake("H", log, **head), out=tmp_path)
  assert e.value.code not in (0, None, 3)
  assert not (tmp_path / "benchmarks.json").exists()


@pytest.mark.parametrize("head", [{"keys": None}, {"fail": {(2, "H"): None}}])
def test_head_worker_exit_3_exits_3(tmp_path, head):
  log = []
  with pytest.raises(SystemExit) as e:
    ab(log, Fake("B", log), Fake("H", log, returncode=3, **head), out=tmp_path)
  assert e.value.code == 3


def test_worker_on_a_foreign_rand_engine_exits_3_naming_the_tree(tmp_path):
  (tmp_path / "rand_engine").symlink_to(Path(__file__).parents[1] / "rand_engine")
  w = Worker(tmp_path)
  assert w.keys is None
  assert w.reason().endswith(f"expected tree {tmp_path}")
  assert w.returncode == 3


def test_worker_crashing_on_import_reports_its_last_stderr_line_and_exit_1(tmp_path):
  (tmp_path / "rand_engine").mkdir()
  (tmp_path / "rand_engine" / "__init__.py").write_text('raise RuntimeError("boom")\n', encoding="utf-8")
  w = Worker(tmp_path)
  assert (w.keys, w.reason(), w.returncode) == (None, "RuntimeError: boom", 1)


def test_worker_hung_past_the_cap_is_killed_at_the_cap(tmp_path, monkeypatch):
  monkeypatch.setattr("benchmarks.speed.CAP_S", 1)
  (tmp_path / "rand_engine").mkdir()
  (tmp_path / "rand_engine" / "__init__.py").write_text("import time\ntime.sleep(60)\n", encoding="utf-8")
  t = time.monotonic()
  w = Worker(tmp_path)
  assert (w.keys, w.returncode) == (None, -9 if os.name != "nt" else 1)  # Windows kill = TerminateProcess(1)
  assert time.monotonic() - t < 10
