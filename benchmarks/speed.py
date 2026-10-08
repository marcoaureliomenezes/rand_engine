"""FR11 speed benchmark, same-runner A/B interleaved per row. CI-only (benchmarks.yml).

python benchmarks/speed.py --base-tree ../base --out docs/
The coordinator times nothing: it alternates requests between two `--worker <tree>` processes (base, head)
over line-delimited JSON, so runner drift hits both sides alike.
"""
import argparse
import gc
import itertools
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import tracemalloc
from pathlib import Path

import numpy as np

PK = {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}
SAMPLE_KWARGS = {
  "integers": {"min": 0, "max": 10**6, "int_type": "int64"},
  "int_zfilled": {"length": 10},
  "floats": {"min": 0, "max": 10**6, "decimals": 2},
  "floats_normal": {"mean": 0, "std": 10**6, "decimals": 2},
  "exponential": {"scale": 1.0, "decimals": 2},
  "lognormal": {"mean": 0.0, "std": 1.0, "decimals": 2},
  "poisson": {"lam": 1.0},
  "zipf": {"a": 2.0},
  "constant": {"value": 1},
  "distincts": {"distincts": ["A", "B", "C", "D", "E"]},
  "distincts_prop": {"distincts": {"gold": 10, "silver": 30, "bronze": 60}},
  "unix_timestamps": {"start": "2020-01-01", "end": "2025-12-31", "date_format": "%Y-%m-%d"},
  "uuid4": {},
  "booleans": {"true_prob": 0.5},
  "dates": {"start": "2020-01-01", "end": "2025-12-31", "date_format": "%Y-%m-%d"},
  "distincts_map": {"distincts": {"mobile": ["android", "ios"], "desktop": ["windows", "macos", "linux"]}},
  "distincts_multi_map": {"distincts": {"tech": [["software", "hardware"], ["small", "medium", "large"]]}},
  "distincts_map_prop": {"distincts": {"EQUITY": [("BUY", 6), ("SELL", 4)], "FX": [("BUY", 5), ("SELL", 5)]}},
  "complex_distincts": {"pattern": "x.x.x.x", "replacement": "x", "templates": [
    {"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}},
    {"method": "integers", "kwargs": {"min": 0, "max": 255}},
    {"method": "integers", "kwargs": {"min": 0, "max": 255}},
    {"method": "integers", "kwargs": {"min": 1, "max": 254}}]},
  "pk": PK["kwargs"],
  "fk": {"parent": PK, "parent_size": 1000},
}
# CommonRandSpecs.customers, copied so both trees write one spec
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
SINKS = ("csv", "parquet", "json", "stream_dict")
RUNS, LIMIT, CAP_S = 3, 1.3, 15 * 60
METHOD_SIBLINGS = {
  "exponential": "floats",
  "lognormal": "floats_normal",
  "poisson": "integers",
  "zipf": "integers",
}
SIBLING_LIMIT = 1.5
MODIFIERS = {
  "null_rate": {"method": "integers", "null_rate": 0.1},
  "anomaly_rate": {
    "method": "integers",
    "anomaly_rate": 0.1,
    "anomaly_values": [-1],
  },
}
MODIFIER_LIMIT = 1.25


def timed(fn):
  t = time.perf_counter()
  result = fn()  # noqa: F841 — freed after the clock stops, so teardown is not timed
  elapsed = time.perf_counter() - t
  return elapsed


def column(method, modifier=None):
  col = {"method": method, "kwargs": SAMPLE_KWARGS[method]}
  if method in COLS: col["cols"] = COLS[method]
  if modifier: col.update({k: v for k, v in MODIFIERS[modifier].items() if k != "method"})
  return col


def drain_stream(gen, rows):
  # the real stream_dict path; its throughput sleep is a no-op in the worker (see worker)
  for _ in itertools.islice(gen.stream_dict(), rows): pass


def serve(req):
  from rand_engine.main._rand_generator import RandGenerator
  from rand_engine.main.data_generator import DataGenerator
  row, rows = req.get("extra") or req["row"], req["rows"]
  if row in SINKS:
    gen = DataGenerator(SINK_SPEC, seed=42).size(rows)
    with tempfile.TemporaryDirectory() as d:
      fn = (lambda: drain_stream(gen, rows)) if row == "stream_dict" else (lambda: gen.write.format(row).save(f"{d}/{row}"))
      return {"s": timed(fn)}
  gen = DataGenerator({"c": column(row, req.get("modifier"))}, seed=42).size(rows)
  if "extra" not in req: return {"s": timed(gen.get_df)}
  core = RandGenerator({"c": column(row)}).map_methods(np.random.default_rng(42), 0, 0, "c")[row]
  core_s = statistics.median(timed(lambda: core(rows, **SAMPLE_KWARGS[row])) for _ in range(RUNS))
  tracemalloc.start(); gen.get_df(); peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
  return {"core_s": core_s, "peak_mib": peak / 2**20}


def worker(tree):
  reply = os.fdopen(os.dup(1), "w", encoding="utf-8")
  os.dup2(2, 1)  # a print or C-level write lands in stderr, never in the protocol
  import rand_engine
  from rand_engine.main._rand_generator import RandGenerator
  from rand_engine.utils.stream_handler import StreamHandler
  check_tree(rand_engine.__file__, tree)
  StreamHandler.sleep_to_contro_throughput = staticmethod(lambda *a: None)

  def send(msg):
    reply.write(json.dumps(msg) + "\n"); reply.flush()
  send({"keys": list(RandGenerator({}).map_methods())})
  for line in sys.stdin:
    req = json.loads(line)
    try: out = serve(req)
    except Exception as e: out = {"error": f"{type(e).__name__}: {e}"}
    gc.collect()
    send({**req, **out})


def parse_reply(req, line):
  """The reply dict, or None when the line is not JSON or does not echo the request (= the worker's death)."""
  try: reply = json.loads(line)
  except ValueError: return None
  return reply if isinstance(reply, dict) and all(reply.get(k) == v for k, v in req.items()) else None


class Worker:
  """One tree's worker process; ask() returns the reply, or None once the worker is dead."""

  def __init__(self, tree):
    self.err = tempfile.TemporaryFile("w+", encoding="utf-8")
    self.proc = subprocess.Popen([sys.executable, "-u", __file__, "--worker", str(tree)], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=self.err, encoding="utf-8",
                                 env={**os.environ, "PYTHONPATH": str(tree), "PYTHONIOENCODING": "utf-8"})
    self.keys = (self.read({}) or {}).get("keys")

  @property
  def returncode(self):
    return self.proc.poll()

  def ask(self, req):
    try: self.proc.stdin.write(json.dumps(req) + "\n"); self.proc.stdin.flush()
    except OSError: return self.end()
    return self.read(req)

  def read(self, req):
    line = []
    t = threading.Thread(target=lambda: line.append(self.proc.stdout.readline()), daemon=True)
    t.start(); t.join(CAP_S)
    reply = parse_reply(req, line[0]) if line else None
    if reply is None and (not line or line[0]): self.proc.kill()  # alive and misbehaving: hung past the cap, or garbled
    return reply if reply is not None else self.end()

  def end(self):
    """The one death path: the worker's real exit status (a bounded wait, then kill); always None."""
    try: self.proc.wait(timeout=30)
    except subprocess.TimeoutExpired: self.proc.kill(); self.proc.wait()

  def reason(self):
    self.end(); self.err.seek(0)
    lines = self.err.read().strip().splitlines()
    return lines[-1] if lines else f"exit {self.proc.returncode}"

  def close(self):
    self.proc.kill(); self.proc.wait(); self.err.seek(0)
    sys.stderr.write(self.err.read())


def key(r):
  return (r.get("modifier") or r.get("method") or r["sink"], r["rows"])


def field(r):
  return "get_df_s" if "method" in r else "sink_s"


def metric(r):
  return r[field(r)]


def compare(current, baseline, limit=LIMIT):
  base = {key(r): metric(r) for r in baseline}
  failed = [key(r) for r in current if key(r) in base and metric(r) > limit * base[key(r)]]
  return failed, [key(r) for r in current if key(r) not in base]


def compare_siblings(current, siblings=METHOD_SIBLINGS, limit=SIBLING_LIMIT):
  rows = {key(record): metric(record) for record in current if "method" in record and "modifier" not in record}
  return [
    (method, count)
    for (method, count), elapsed in rows.items()
    if method in siblings
    and (siblings[method], count) in rows
    and elapsed > limit * rows[(siblings[method], count)]
  ]


def compare_modifiers(current, modifiers=MODIFIERS, limit=MODIFIER_LIMIT):
  methods = {(record["method"], record["rows"]): metric(record)
             for record in current if "method" in record and "modifier" not in record}
  return [
    (record["modifier"], record["rows"])
    for record in current
    if record.get("modifier") in modifiers
    and metric(record) > limit * methods[(record["method"], record["rows"])]
  ]


def baseline(records):
  """The base side of A/B records, in compare's record shape."""
  return [{**r, field(r): r["base_" + field(r)]} for r in records if "base_" + field(r) in r]


def check_tree(module_file, expected):
  if Path(module_file).resolve().parents[1] != Path(expected).resolve():
    print(f"rand_engine imported from {module_file}, expected tree {expected}", file=sys.stderr)
    sys.exit(3)


def plan_keys(sample_keys, head_keys, base_keys):
  missing = sorted(set(head_keys) - set(sample_keys))
  if missing: sys.exit(f"SAMPLE_KWARGS lacks map_methods keys: {missing}")
  absent = {} if base_keys is None else {**{k: "deleted in head" for k in base_keys if k not in head_keys},
                                         **{k: "added in head" for k in head_keys if k not in base_keys}}
  return [k for k in sample_keys if k in head_keys], absent


def render(report, absent, error):
  records = report["records"]
  base_candidates = [r for r in records if "modifier" not in r]
  failed, _ = compare(records, baseline(records))
  modifier_failed = set(compare_modifiers(records))
  method_times = {(r["method"], r["rows"]): metric(r)
                  for r in records if "method" in r and "modifier" not in r}
  lines = [(f"# Speed benchmark (same-runner A/B)\n\nhead `{report['commit']}` · base `{report['base_commit'] or 'none'}` · "
            f"Python {report['python']} · NumPy {report['numpy']} · {report['runner']}\n"),
           f"base rows {len(baseline(records))}/{len(base_candidates)}" + (f" · base pass failed: {error}" if error else ""),
           *(f"- `{k}`: {why}" for k, why in absent.items()), "",
           "| method / sink | rows | rows/µs | base s | head s | ratio | peak MiB |", "|---|---|---|---|---|---|---|"]
  for r in records:
    k, b = key(r), r.get("base_" + field(r))
    if "modifier" in r:
      ratio = f"{metric(r) / method_times[(r['method'], r['rows'])]:.2f}"
      if k in modifier_failed: ratio += f" ❌ > {MODIFIER_LIMIT}"
    else:
      ratio = f"{metric(r) / b:.2f}" + (f" ❌ > {LIMIT}" if k in failed else "") if b else "absent → recorded"
    peak = f"{r['peak_mib']:.1f}" if "peak_mib" in r else "—"
    lines.append(f"| {k[0]} | {k[1]:,} | {r['rows_per_us']:.3f} | {f'{b:.3f}' if b else '—'} | {metric(r):.3f} | {ratio} | {peak} |")
  return "\n".join(lines) + "\n"


def run(head, base, sizes, out, error=None):
  """Coordinate the A/B rows, write benchmarks.json + BENCHMARKS.md, exit 3 on a foreign base tree, 1 over LIMIT."""
  def ask_head(req):
    reply = head.ask(req)
    if reply is None or "error" in reply:
      if head.returncode == 3: sys.exit(3)
      sys.exit(f"head worker failed on {req}: {reply['error'] if reply else head.reason()}")
    return reply

  if head.keys is None: sys.exit(3 if head.returncode == 3 else f"head worker failed: {head.reason()}")
  if error is None and base.keys is None: error = base.reason()
  methods, absent = plan_keys(list(SAMPLE_KWARGS), head.keys, None if error else base.keys)
  def shared(row): return error is None and (row in SINKS or row in base.keys)
  rows = sorted([(m, n) for n in sizes for m in methods] + [(s, sizes[0]) for s in SINKS], key=lambda rn: not shared(rn[0]))
  requests = [{"row": row, "rows": n} for row, n in rows]
  requests.extend(
    {"row": config["method"], "rows": n, "modifier": name}
    for n in sizes
    for name, config in MODIFIERS.items()
  )
  records = []
  for i, req in enumerate(requests):  # head-only rows last: both workers share one call history while shared rows time
    row, n, times = req["row"], req["rows"], {"head": [], "base": []}
    base_ok = "modifier" not in req and shared(row)
    for side in (["base", "head"] if i % 2 == 0 else ["head", "base"]) * RUNS:
      if side == "head": times["head"].append(ask_head(req)["s"]); continue
      if not base_ok: continue
      reply = base.ask(req)
      if reply is None: error, base_ok = base.reason(), False
      elif "error" in reply: absent[row], base_ok = f"base raised {reply['error']}", False
      else: times["base"].append(reply["s"])
    r = {("sink" if row in SINKS else "method"): row, "rows": n}
    if "modifier" in req: r["modifier"] = req["modifier"]
    r[field(r)] = statistics.median(times["head"])
    r["rows_per_us"] = n / (statistics.mean(times["head"]) * 1e6)
    if base_ok: r["base_" + field(r)] = statistics.median(times["base"])
    records.append(r)
  for r in records:  # extras after the last timed row, so they never skew a timed call's history
    if "method" in r and "modifier" not in r:
      extra = ask_head({"extra": r["method"], "rows": r["rows"]})
      r.update(core_s=extra["core_s"], peak_mib=extra["peak_mib"])
  report = {"commit": os.environ.get("HEAD_SHA", "local"), "base_commit": os.environ.get("BASE_SHA") or None,
            "python": platform.python_version(), "numpy": np.__version__,
            "runner": os.environ.get("RUNNER_NAME", platform.node()), "records": records}
  os.makedirs(out, exist_ok=True)
  with open(os.path.join(out, "benchmarks.json"), "w", encoding="utf-8") as f: json.dump(report, f, indent=2)
  with open(os.path.join(out, "BENCHMARKS.md"), "w", encoding="utf-8") as f: f.write(render(report, absent, error))
  if base is not None and base.returncode == 3: sys.exit(3)
  failed, _ = compare(records, baseline(records))
  sibling_failed = compare_siblings(records)
  modifier_failed = compare_modifiers(records)
  failures = []
  if failed: failures.append(f"over {LIMIT}x base: {failed}")
  if sibling_failed: failures.append(f"over {SIBLING_LIMIT}x sibling: {sibling_failed}")
  if modifier_failed: failures.append(f"over {MODIFIER_LIMIT}x modifier baseline: {modifier_failed}")
  if failures: sys.exit("; ".join(failures))


def main(argv=None):
  p = argparse.ArgumentParser()
  p.add_argument("--worker", metavar="TREE", help=argparse.SUPPRESS)
  p.add_argument("--base-tree", type=Path, help="the base commit's tree; missing = every row absent")
  p.add_argument("--out", default="docs/")
  p.add_argument("--sizes", type=int, nargs="+", default=[10**6, 10**7], help="method sizes; the first is the sink size")
  a = p.parse_args(argv)
  if a.worker: return worker(a.worker)
  head = Worker(Path(__file__).parents[1])
  base = Worker(a.base_tree) if a.base_tree and a.base_tree.is_dir() else None
  try: run(head, base, a.sizes, a.out, None if base else f"no base tree for commit '{os.environ.get('BASE_SHA', '')}'")
  finally:
    for w in (head, base):
      if w: w.close()


if __name__ == "__main__":
  main()
