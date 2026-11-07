"""Shared helper of the agent-eval task checks (layers 1 to 3).

`provenance(workdir, script, artifacts, python, specs, calls)` -> None | "provenance: ..."; `value_hash(values)` -> str;
`tool_events(path)` -> [{"name", "input"}]; `web_tool_uses(events)` -> [tool names].
Layer 3: `legacy_hits(text)` -> [names]; `documented_method(specs, method, kwargs)` -> bool;
`token_ceiling(task_toml, env)` -> None | "ceiling: ..."; `surfaces(events)` -> [tokens];
`result_text(layer, message, surfaces)` -> the failure line and the `RESULT {json}` line.
Side effects: `provenance` runs `script` once as a subprocess in `workdir`.
"""
import ast
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

API_CALLS = {"DataGenerator", "SparkGenerator", "get_df", "save", "start", "stream_dict"}
WEB_TOOLS = ("WebFetch", "WebSearch")
RERUN_ENV = ("PATH", "HOME", "TMPDIR", "TEMP", "TMP", "LANG", "SYSTEMROOT", "JAVA_HOME")

# Runs first in the re-run interpreter: records each produced frame (rows, per-column hash) and each generator's spec.
SHIM = '''
import atexit, glob, json, os
import pandas as pd
import _check

frames, specs, streams, calls = [], [], [], []

def record(df):
    frames.append({"rows": len(df), "cols": {str(c): _check.value_hash(df[c].tolist()) for c in df.columns}})

def record_spec(gen):
    spec = getattr(gen, "metadata", None) if hasattr(gen, "metadata") else gen.lazy_random_spec
    spec = spec() if callable(spec) else spec
    specs.append(json.loads(json.dumps(spec, default=str)))

def read(path):
    p = path if os.path.exists(path) else next(iter(sorted(glob.glob(path + ".*"))), path)
    return _check.read_artifact(p)

def wrap_get_df(cls):
    orig = cls.get_df
    def get_df(self, *a, **k):
        out = orig(self, *a, **k)
        record_spec(self)
        record(out.toPandas() if hasattr(out, "toPandas") else out)
        return out
    cls.get_df = get_df

def wrap_save(cls):
    orig = cls.save
    def save(self, path, *a, **k):
        calls.append("save")
        out = orig(self, path, *a, **k)
        record_spec(self.size_def.__self__)
        if self.write_format != "sqlite":
            record(read(str(path)))
        return out
    cls.save = save

def wrap_start(cls):
    orig = cls.start
    def start(self, *a, **k):
        calls.append("start")
        record_spec(self.size_def.__self__)
        return orig(self, *a, **k)
    cls.start = start

def wrap_stream(cls):
    orig = cls.stream_dict
    def stream_dict(self, *a, **k):
        rows = []
        streams.append(rows)
        record_spec(self)
        for row in orig(self, *a, **k):
            rows.append(row)
            yield row
    cls.stream_dict = stream_dict

from rand_engine import DataGenerator
from rand_engine.file_handlers._writer_batch import FileBatchWriter
wrap_get_df(DataGenerator); wrap_save(FileBatchWriter); wrap_stream(DataGenerator)
from rand_engine.file_handlers._writer_stream import FileStreamWriter
wrap_start(FileStreamWriter)
try:
    from rand_engine.main.spark_generator import SparkGenerator
except ImportError:
    pass
else:
    wrap_get_df(SparkGenerator)

@atexit.register
def dump():
    for rows in streams:
        if rows:
            record(pd.DataFrame(rows))
    with open(os.environ["RAND_EVAL_RECORD"], "w") as f:
        json.dump({"frames": frames, "specs": specs, "calls": calls}, f)
'''


def value_hash(values):
    """SHA-256 of the values as strings; None, NaN and NaT hash as the empty string, order counts."""
    import pandas as pd
    text = ["" if pd.isna(v) else str(v) for v in values]
    return hashlib.sha256(json.dumps(text).encode()).hexdigest()


def read_artifact(path):
    """DataFrame of a csv or json-lines file as written (text, no inference), a parquet file, or a directory of parts (entries whose name starts with `_` or `.` are hidden and skipped); gzip is decompressed."""
    import pandas as pd
    path = Path(path)
    if path.is_dir():
        return pd.concat([read_artifact(p) for p in sorted(path.iterdir()) if p.is_file() and p.name[0] not in "_."], ignore_index=True)
    name = path.name.removesuffix(".gz")
    if name.endswith(".parquet"):
        return pd.read_parquet(path)
    if name.endswith((".json", ".jsonl")):
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt", encoding="utf-8") as f:
            return pd.DataFrame([json.loads(line) for line in f if line.strip()], dtype=object)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


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


def provenance(workdir, script, artifacts, python=sys.executable, specs=None, calls=None):
    """None when every artifact column equals a column the script generated through rand_engine on a re-run, else a "provenance: ..." line.

    The re-run happens in a scratch copy of `workdir` without the artifacts, so the originals are only read.
    A listed artifact the agent did not deliver fails.
    When `specs` is a list, each generator's evaluated spec dict is appended to it; when `calls` is a list, the name ("save", "start") of each writer entry point that ran is appended.
    """
    if (msg := _static(script)):
        return msg
    workdir, script = Path(workdir).resolve(), Path(script).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "shim").mkdir()
        (tmp / "shim" / "sitecustomize.py").write_text(SHIM)
        shutil.copy(__file__, tmp / "shim" / "_check.py")
        scratch = tmp / "work"
        shutil.copytree(workdir, scratch)
        for art in artifacts:
            (shutil.rmtree if (scratch / art).is_dir() else Path.unlink)(scratch / art) if (scratch / art).exists() else None
        record = tmp / "record.json"
        env = {k: os.environ[k] for k in RERUN_ENV if k in os.environ}
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(tmp / "shim"), os.environ.get("PYTHONPATH")]))
        env["RAND_EVAL_RECORD"] = str(record)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        target = scratch / script.relative_to(workdir) if script.is_relative_to(workdir) else script
        try:
            run = subprocess.run([python, str(target)], cwd=scratch, env=env, capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"provenance: the script could not re-run: {type(e).__name__}"
        if run.returncode != 0:
            return f"provenance: the script exited {run.returncode} on re-run: {run.stderr.strip()[-300:]}"
        if not record.exists():
            return "provenance: the re-run recorded no generated frame"
        data = json.loads(record.read_text())
        if specs is not None:
            specs.extend(data["specs"])
        if calls is not None:
            calls.extend(data["calls"])
        recorded = {(c, f["rows"], h) for f in data["frames"] for c, h in f["cols"].items()}
        for art in artifacts:
            if not (workdir / art).exists():
                return f"provenance: artifact {art} was not delivered"
            try:
                df = read_artifact(workdir / art)
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


SURFACES = ("llms.txt", "help(", "get-started", "cases/", "examples/", "method_specs", "SpecValidationError")

# The legacy names and syntax the CHANGELOG marks removed or renamed; each item is one pattern.
LEGACY = {
    "ExampleSpecs": r"\bExampleSpecs\b",
    "constraints": r"""["']constraints["']\s*:""",
    "db_checkpoint": r"\.db_checkpoint\(",
    "option": r"DataGenerator\([^()]*\)\.option\(",
    "uuid4 length": r"""uuid4[^\n]*["']length["']\s*:""",
    "args": r"""["']args["']\s*:""",
    "splitable": r"""["'](?:splitable|sep)["']\s*:""",
    "validate_with_warnings": r"\bvalidate(?:_spark)?_with_warnings\b",
}


def legacy_hits(text):
    """Names of the LEGACY items the text uses, in LEGACY order."""
    return [name for name, pattern in LEGACY.items() if re.search(pattern, text)]


def documented_method(specs, method, kwargs):
    """True when some recorded spec dict has a column of `method` whose kwargs hold every name in `kwargs`; non-dict columns are skipped."""
    return any(isinstance(e, dict) and e.get("method") == method and isinstance(e.get("kwargs", {}), dict)
               and set(kwargs) <= set(e.get("kwargs", {})) for spec in specs if isinstance(spec, dict) for e in spec.values())


def token_ceiling(task_toml, env):
    """None when within the ceiling or skipped (no RAND_EVAL_TOKENS), else a "ceiling: ..." line."""
    if "RAND_EVAL_TOKENS" not in env:
        return None
    ceiling = tomllib.loads(Path(task_toml).read_text(encoding="utf-8")).get("limits", {}).get("ceiling_tokens")
    tokens = int(env["RAND_EVAL_TOKENS"])
    if ceiling is not None and tokens > ceiling:
        return f"ceiling: {tokens} tokens exceed the task.toml ceiling of {ceiling}"
    return None


def surfaces(events):
    """The SURFACES tokens any tool_use input holds, in SURFACES order."""
    blobs = [json.dumps(e["input"]) for e in events]
    return [t for t in SURFACES if any(t in b for b in blobs)]


def result_text(layer, message, surfaces=()):
    """The failure line, naming its layer, then the `RESULT {json}` line; `layer` is the string "1", "2" or "3"."""
    line = message if message.startswith(layer) else f"{layer}: {message}"
    return f"{line}\nRESULT {json.dumps({'layer': layer, 'surfaces': list(surfaces)})}\n"
