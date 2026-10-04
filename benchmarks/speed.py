"""FR11 speed benchmark: one row per map_methods method and size, one per sink. CI-only (benchmarks.yml)."""
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

from rand_engine.examples.common_rand_specs import CommonRandSpecs
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
COLS = {"distincts_map": ["a", "b"], "distincts_map_prop": ["a", "b"], "distincts_multi_map": ["a", "b", "c"]}
RUNS, LIMIT = 3, 1.3


def timed(fn):
  t = time.perf_counter()
  result = fn()  # noqa: F841 — freed after the clock stops, so teardown is not timed
  elapsed = time.perf_counter() - t
  return elapsed


def method_row(method, rows):
  col = {"method": method, "kwargs": SAMPLE_KWARGS[method]}
  if method in COLS: col["cols"] = COLS[method]
  gen = DataGenerator({"c": col}, seed=42).size(rows)
  core = RandGenerator({"c": col}).map_methods(0, 0, "c")[method]
  core_s = [timed(lambda: core(rows, **SAMPLE_KWARGS[method])) for _ in range(RUNS)]
  get_df_s = [timed(gen.get_df) for _ in range(RUNS)]
  tracemalloc.start(); gen.get_df(); peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
  return {"method": method, "rows": rows, "core_s": statistics.median(core_s), "get_df_s": statistics.median(get_df_s),
          "peak_mib": peak / 2**20, "rows_per_us": rows / (statistics.mean(get_df_s) * 1e6)}


def drain_stream(gen, rows):
  # the real stream_dict path; its throughput sleep is a no-op in this process (see main)
  for _ in itertools.islice(gen.stream_dict(), rows): pass


def sink_rows(rows):
  gen = DataGenerator(CommonRandSpecs.customers(), seed=42).size(rows)
  out = []
  with tempfile.TemporaryDirectory() as d:
    sinks = {fmt: (lambda fmt=fmt: gen.write.format(fmt).save(f"{d}/{fmt}")) for fmt in ("csv", "parquet", "json")}
    sinks["stream_dict"] = lambda: drain_stream(gen, rows)
    for sink, fn in sinks.items():
      s = [timed(fn) for _ in range(RUNS)]
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


def render(report, baseline):
  base = {key(r): metric(r) for r in baseline}
  failed, _ = compare(report["records"], baseline)
  lines = [f"# Speed benchmark\n\ncommit `{report['commit']}` · Python {report['python']} · NumPy {report['numpy']} · {report['runner']}\n",
           "| method / sink | rows | rows/µs | median s | baseline s | ratio | peak MiB |", "|---|---|---|---|---|---|---|"]
  for r in report["records"]:
    k, b = key(r), base.get(key(r))
    ratio = f"{metric(r) / b:.2f}" + (f" ❌ > {LIMIT}" if k in failed else "") if b else "absent → recorded"
    peak = f"{r['peak_mib']:.1f}" if "peak_mib" in r else "—"
    lines.append(f"| {k[0]} | {k[1]:,} | {r['rows_per_us']:.3f} | {metric(r):.3f} | {f'{b:.3f}' if b else '—'} | {ratio} | {peak} |")
  return "\n".join(lines) + "\n"


def main(argv=None):
  p = argparse.ArgumentParser()
  p.add_argument("--baseline", default="docs/benchmarks.json")
  p.add_argument("--out", default="docs/")
  p.add_argument("--sizes", type=int, nargs="+", default=[10**6, 10**7], help="method sizes; the first is the sink size")
  a = p.parse_args(argv)
  StreamHandler.sleep_to_contro_throughput = staticmethod(lambda *a: None)
  gap = set(SAMPLE_KWARGS) ^ set(RandGenerator({}).map_methods())
  if gap: sys.exit(f"SAMPLE_KWARGS and map_methods differ: {sorted(gap)}")
  records = [method_row(m, n) for n in a.sizes for m in SAMPLE_KWARGS] + sink_rows(a.sizes[0])
  report = {"commit": os.environ.get("HEAD_SHA", "local"), "python": platform.python_version(), "numpy": np.__version__,
            "runner": os.environ.get("RUNNER_NAME", platform.node()), "records": records}
  baseline = json.loads(Path(a.baseline).read_text())["records"] if os.path.exists(a.baseline) else []
  os.makedirs(a.out, exist_ok=True)
  with open(os.path.join(a.out, "benchmarks.json"), "w") as f: json.dump(report, f, indent=2)
  with open(os.path.join(a.out, "BENCHMARKS.md"), "w") as f: f.write(render(report, baseline))
  failed, _ = compare(records, baseline)
  if failed: sys.exit(f"over {LIMIT}x baseline: {failed}")


if __name__ == "__main__":
  main()
