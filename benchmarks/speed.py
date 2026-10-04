"""FR11 speed benchmark, same-runner A/B: one row per map_methods method and size, one per sink. CI-only (benchmarks.yml).

Base pass: PYTHONPATH=<base tree> python benchmarks/speed.py --base-pass <base tree> --out <dir>
Head pass: python benchmarks/speed.py --baseline <dir>/benchmarks.json --out docs/
"""
import argparse
import itertools
import json
import os
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

import numpy as np

import rand_engine
from rand_engine.main._rand_generator import RandGenerator
from rand_engine.main.data_generator import DataGenerator
from rand_engine.utils.stream_handler import StreamHandler

PK = {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}
SAMPLE_KWARGS = {
  "integers": {"min": 0, "max": 10**6, "int_type": "int64"},
  "int_zfilled": {"length": 10},
  "floats": {"min": 0, "max": 10**6, "decimals": 2},
  "floats_normal": {"mean": 0, "std": 10**6, "decimals": 2},
  "distincts": {"distincts": ["A", "B", "C", "D", "E"]},
  "distincts_prop": {"distincts": {"gold": 10, "silver": 30, "bronze": 60}},
  "unix_timestamps": {"start": "2020-01-01", "end": "2025-12-31", "date_format": "%Y-%m-%d"},
  "uuid4": {},
  "booleans": {"true_prob": 0.5},
  "dates": {"start": "2020-01-01", "end": "2025-12-31", "date_format": "%Y-%m-%d"},
  "distincts_map": {"distincts": {"mobile": ["android", "ios"], "desktop": ["windows", "macos", "linux"]}},
  "distincts_multi_map": {"distincts": {"tech": [["software", "hardware"], [0.7, 0.3], ["small", "medium", "large"]]}},
  "distincts_map_prop": {"distincts": {"EQUITY": [("BUY", 6), ("SELL", 4)], "FX": [("BUY", 5), ("SELL", 5)]}},
  "complex_distincts": {"pattern": "x.x.x.x", "replacement": "x", "templates": [
    {"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}},
    {"method": "integers", "kwargs": {"min": 0, "max": 255}},
    {"method": "integers", "kwargs": {"min": 0, "max": 255}},
    {"method": "integers", "kwargs": {"min": 1, "max": 254}}]},
  "pk": PK["kwargs"],
  "fk": {"parent": PK, "parent_size": 1000},
}
# CommonRandSpecs.customers, copied so both passes write one spec
SINK_SPEC = {
  "customer_id": {"method": "uuid4", "kwargs": {}},
  "age": {"method": "integers", "kwargs": {"min": 18, "max": 80, "int_type": "int32"}},
  "city": {"method": "distincts", "kwargs": {"distincts": [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador", "Brasília", "Curitiba", "Porto Alegre"]}},
  "total_spent": {"method": "floats_normal", "kwargs": {"mean": 1500.0, "std": 500.0, "decimals": 2}},
  "is_premium": {"method": "booleans", "kwargs": {"true_prob": 0.15}},
  "registration_date": {"method": "dates", "kwargs": {"start": "2020-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}},
}
COLS = {"distincts_map": ["a", "b"], "distincts_map_prop": ["a", "b"], "distincts_multi_map": ["a", "b", "c"]}
RUNS, LIMIT = 3, 1.3


def timed(fn):
  t = time.perf_counter()
  result = fn()  # noqa: F841 — freed after the clock stops, so teardown is not timed
  elapsed = time.perf_counter() - t
  return elapsed


def method_row(method, rows, base_pass):
  col = {"method": method, "kwargs": SAMPLE_KWARGS[method]}
  if method in COLS: col["cols"] = COLS[method]
  gen = DataGenerator({"c": col}, seed=42).size(rows)
  get_df_s = [timed(gen.get_df) for _ in range(RUNS)]
  row = {"method": method, "rows": rows, "get_df_s": statistics.median(get_df_s)}
  if base_pass: return row  # the base times the public path only
  core = RandGenerator({"c": col}).map_methods(0, 0, "c")[method]
  core_s = [timed(lambda: core(rows, **SAMPLE_KWARGS[method])) for _ in range(RUNS)]
  tracemalloc.start(); gen.get_df(); peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
  return {**row, "core_s": statistics.median(core_s), "peak_mib": peak / 2**20,
          "rows_per_us": rows / (statistics.mean(get_df_s) * 1e6)}


def drain_stream(gen, rows):
  # the real stream_dict path; its throughput sleep is a no-op in this process (see main)
  for _ in itertools.islice(gen.stream_dict(), rows): pass


def sink_rows(rows, absent):
  gen = DataGenerator(SINK_SPEC, seed=42).size(rows)
  out = []
  with tempfile.TemporaryDirectory() as d:
    sinks = {fmt: (lambda fmt=fmt: gen.write.format(fmt).save(f"{d}/{fmt}")) for fmt in ("csv", "parquet", "json")}
    sinks["stream_dict"] = lambda: drain_stream(gen, rows)
    for sink, fn in sinks.items():
      try: s = [timed(fn) for _ in range(RUNS)]
      except Exception as e:
        if absent is None: raise
        absent[sink] = f"base raised {type(e).__name__}: {e}"; continue
      out.append({"sink": sink, "rows": rows, "sink_s": statistics.median(s), "rows_per_us": rows / (statistics.mean(s) * 1e6)})
  return out


def key(r):
  return (r.get("method") or r["sink"], r["rows"])


def metric(r):
  return r["get_df_s"] if "get_df_s" in r else r["sink_s"]


def compare(current, baseline, limit=LIMIT):
  base = {key(r): metric(r) for r in baseline}
  failed = [key(r) for r in current if key(r) in base and metric(r) > limit * base[key(r)]]
  return failed, [key(r) for r in current if key(r) not in base]


def check_tree(module_file, expected):
  if Path(module_file).resolve().parents[1] != Path(expected).resolve():
    print(f"rand_engine imported from {module_file}, expected tree {expected}", file=sys.stderr)
    sys.exit(3)


def plan_keys(sample_keys, tree_keys, base_pass):
  if not base_pass and set(tree_keys) - set(sample_keys):
    sys.exit(f"SAMPLE_KWARGS lacks map_methods keys: {sorted(set(tree_keys) - set(sample_keys))}")
  absent = {k: "deleted in head" for k in tree_keys if k not in sample_keys}
  return [k for k in sample_keys if k in tree_keys], absent


def attach_base(records, base_records):
  base_t = {key(r): metric(r) for r in base_records}
  for r in records:
    if key(r) in base_t: r["base_get_df_s" if "method" in r else "base_sink_s"] = base_t[key(r)]


def render(report, base):
  failed, _ = compare(report["records"], base.get("records", []))
  absent = base.get("absent", {})
  covered = sum("base_get_df_s" in r or "base_sink_s" in r for r in report["records"])
  lines = [(f"# Speed benchmark (same-runner A/B)\n\nhead `{report['commit']}` · base `{report['base_commit'] or 'none'}` · "
            f"Python {report['python']} · NumPy {report['numpy']} · {report['runner']}\n"),
           f"base rows {covered}/{len(report['records'])}" + (f" · base pass failed: {base['error']}" if base.get("error") else ""),
           *(f"- `{k}`: {why}" for k, why in absent.items()), "",
           "| method / sink | rows | rows/µs | base s | head s | ratio | peak MiB |", "|---|---|---|---|---|---|---|"]
  for r in report["records"]:
    k, b = key(r), r.get("base_get_df_s", r.get("base_sink_s"))
    ratio = f"{metric(r) / b:.2f}" + (f" ❌ > {LIMIT}" if k in failed else "") if b else "absent → recorded"
    peak = f"{r['peak_mib']:.1f}" if "peak_mib" in r else "—"
    lines.append(f"| {k[0]} | {k[1]:,} | {r['rows_per_us']:.3f} | {f'{b:.3f}' if b else '—'} | {metric(r):.3f} | {ratio} | {peak} |")
  return "\n".join(lines) + "\n"


def read_base(path):
  base = json.loads(path.read_text()) if path.exists() else {}
  err = path.with_name("error.txt")
  if err.exists(): base["error"] = err.read_text().strip()
  return base


def main(argv=None):
  p = argparse.ArgumentParser()
  p.add_argument("--baseline", type=Path, default=Path("docs/benchmarks.json"))
  p.add_argument("--base-pass", metavar="TREE", help="measure the base tree at TREE (on PYTHONPATH)")
  p.add_argument("--out", default="docs/")
  p.add_argument("--sizes", type=int, nargs="+", default=[10**6, 10**7], help="method sizes; the first is the sink size")
  a = p.parse_args(argv)
  base_pass = a.base_pass is not None
  check_tree(rand_engine.__file__, a.base_pass if base_pass else Path(__file__).parents[1])
  StreamHandler.sleep_to_contro_throughput = staticmethod(lambda *a: None)
  methods, absent = plan_keys(list(SAMPLE_KWARGS), list(RandGenerator({}).map_methods()), base_pass)
  records = []
  for n in a.sizes:
    for m in methods:
      try: records.append(method_row(m, n, base_pass))
      except Exception as e:
        if not base_pass: raise
        absent[m] = f"base raised {type(e).__name__}: {e}"
  records += sink_rows(a.sizes[0], absent if base_pass else None)
  report = {"commit": os.environ.get("HEAD_SHA", "local"), "python": platform.python_version(), "numpy": np.__version__,
            "runner": os.environ.get("RUNNER_NAME", platform.node()), "records": records}
  os.makedirs(a.out, exist_ok=True)
  if base_pass:
    with open(os.path.join(a.out, "benchmarks.json"), "w") as f: json.dump({**report, "absent": absent}, f, indent=2)
    return
  base = read_base(a.baseline)
  attach_base(records, base.get("records", []))
  report["base_commit"] = base.get("commit")
  with open(os.path.join(a.out, "benchmarks.json"), "w") as f: json.dump(report, f, indent=2)
  with open(os.path.join(a.out, "BENCHMARKS.md"), "w") as f: f.write(render(report, base))
  failed, _ = compare(records, base.get("records", []))
  if failed: sys.exit(f"over {LIMIT}x base: {failed}")


if __name__ == "__main__":
  main()
