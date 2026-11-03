"""Shared helper of the agent-eval task checks (layers 1 and 2).

`provenance(workdir, script, artifacts, python)` -> None | "provenance: ..."; `value_hash(values)` -> str;
`tool_events(path)` -> [{"name", "input"}]; `web_tool_uses(events)` -> [tool names].
Side effects: `provenance` runs `script` once as a subprocess in `workdir`.
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

API_CALLS = {"DataGenerator", "SparkGenerator", "get_df", "save", "start", "stream_dict"}
WEB_TOOLS = ("WebFetch", "WebSearch")

# Runs first in the re-run interpreter: records each produced frame as (columns, rows, per-column hash).
SHIM = '''
import atexit, json, os, sys
sys.path.insert(0, os.environ["RAND_EVAL_EVALS"])
sys.path.append(os.path.dirname(os.environ["RAND_EVAL_EVALS"]))  # ponytail: last-resort source tree for a venv without the package
import _check

frames, streams = [], []

def record(df):
    frames.append({"rows": len(df), "cols": {str(c): _check.value_hash(df[c].tolist()) for c in df.columns}})

def read(path):
    p = path if os.path.exists(path) else next(iter(sorted(__import__("glob").glob(path + ".*"))), path)
    return _check.read_artifact(p)

def wrap_get_df(cls):
    orig = cls.get_df
    def get_df(self, *a, **k):
        out = orig(self, *a, **k)
        record(out if hasattr(out, "columns") and not hasattr(out, "toPandas") else out.toPandas())
        return out
    cls.get_df = get_df

def wrap_save(cls):
    orig = cls.save
    def save(self, path, *a, **k):
        out = orig(self, path, *a, **k)
        record(read(str(path)))
        return out
    cls.save = save

def wrap_stream(cls):
    orig = cls.stream_dict
    def stream_dict(self, *a, **k):
        rows = []
        streams.append(rows)
        for row in orig(self, *a, **k):
            rows.append(row)
            yield row
    cls.stream_dict = stream_dict

try:
    from rand_engine import DataGenerator
    from rand_engine.file_handlers._writer_batch import FileBatchWriter
    wrap_get_df(DataGenerator); wrap_save(FileBatchWriter); wrap_stream(DataGenerator)
except Exception:
    pass
try:
    from rand_engine.main.spark_generator import SparkGenerator
    wrap_get_df(SparkGenerator)
except Exception:
    pass

@atexit.register
def dump():
    for rows in streams:
        if rows:
            record(pd.DataFrame(rows))
    with open(os.environ["RAND_EVAL_RECORD"], "w") as f:
        json.dump(frames, f)
'''.replace("import atexit,", "import pandas as pd, atexit,")


def value_hash(values):
    """SHA-256 of the values as strings; None, NaN and NaT hash as the empty string, order counts."""
    text = ["" if pd.isna(v) else str(v) for v in values]
    return hashlib.sha256(json.dumps(text).encode()).hexdigest()


def read_artifact(path):
    """DataFrame of a csv, json (lines), or parquet file, or of a directory of such parts (gzip decompressed)."""
    path = Path(path)
    if path.is_dir():
        return pd.concat([read_artifact(p) for p in sorted(path.iterdir()) if p.is_file()], ignore_index=True)
    name = path.name.removesuffix(".gz")
    if name.endswith(".parquet"):
        return pd.read_parquet(path)
    if name.endswith((".json", ".jsonl")):
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def _static(script):
    try:
        tree = ast.parse(Path(script).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError) as e:
        return f"provenance: cannot read {script}: {type(e).__name__}"
    nodes = list(ast.walk(tree))
    if not any(isinstance(n, ast.Import) and any(a.name.split(".")[0] == "rand_engine" for a in n.names)
               or isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "rand_engine" for n in nodes):
        return "provenance: the script does not import rand_engine"
    called = {n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "") for n in nodes if isinstance(n, ast.Call)}
    if not called & API_CALLS:
        return "provenance: the script imports rand_engine but calls none of its generating API"
    return None


def provenance(workdir, script, artifacts, python=sys.executable):
    """None when every artifact column equals a column the re-run script generated through rand_engine, else a "provenance: ..." line."""
    if (msg := _static(script)):
        return msg
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "sitecustomize.py").write_text(SHIM)
        record = Path(tmp) / "record.json"
        env = {**os.environ, "PYTHONPATH": tmp, "RAND_EVAL_RECORD": str(record),
               "RAND_EVAL_EVALS": str(Path(__file__).resolve().parent)}
        try:
            run = subprocess.run([python, str(Path(script).resolve())], cwd=workdir, env=env,
                                 capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"provenance: the script could not re-run: {type(e).__name__}"
        if run.returncode != 0:
            return f"provenance: the script exited {run.returncode} on re-run: {run.stderr.strip()[-300:]}"
        if not record.exists():
            return "provenance: the re-run recorded no generated frame"
        recorded = {(c, f["rows"], h) for f in json.loads(record.read_text()) for c, h in f["cols"].items()}
    for art in artifacts:
        try:
            df = read_artifact(Path(workdir) / art)
        except Exception as e:
            return f"provenance: cannot read artifact {art}: {type(e).__name__}"
        for col in df.columns:
            if (str(col), len(df), value_hash(df[col].tolist())) not in recorded:
                return f"provenance: column {col!r} of {art} matches no frame rand_engine generated"
    return None


def tool_events(path):
    """Every tool_use of an assistant message in the stream-json transcript, as {"name", "input"}, in order."""
    events = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if msg.get("type") != "assistant":
            continue
        events += [{"name": b["name"], "input": b.get("input", {})}
                   for b in msg["message"]["content"] if b.get("type") == "tool_use"]
    return events


def web_tool_uses(events):
    """Names of the web tools the events used."""
    return [e["name"] for e in events if e["name"] in WEB_TOOLS]
