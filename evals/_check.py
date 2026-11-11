"""Shared helper of the agent-eval task checks (layers 1 to 3).

`provenance(workdir, script, artifacts, python)` -> (None | "provenance: ...", record); `agent(record, field)` -> [values];
`value_hash(values)` -> str;
`tool_events(path)` -> [{"name", "input"}]; `web_tool_uses(events)` -> [tool names].
Layer 3: `legacy_hits(text)` -> [names]; `documented_method(specs, method, kwargs)` -> bool;
`token_ceiling(task_toml, env)` -> None | "ceiling: ..."; `surfaces(events)` -> [tokens];
`result_text(layer, message, surfaces)` -> the failure line and the `RESULT {json}` line.
Side effects: `provenance` runs `script` once as a subprocess in a scratch copy of `workdir`.
"""
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

WEB_TOOLS = ("WebFetch", "WebSearch")
RERUN_ENV = ("PATH", "HOME", "TMPDIR", "TEMP", "TMP", "LANG", "SYSTEMROOT", "JAVA_HOME")

# Runs first in the re-run interpreter: one record per distinct generation (the _file_seam hook, plus SparkGenerator.get_df),
# then the output hashes of get_df, save and stream_dict, each tagged with whether the agent's code called it.
SHIM = '''
import atexit, json, os, sys
import pandas as pd
from rand_engine import DataGenerator
import _check

LIB = os.path.dirname(sys.modules["rand_engine"].__file__) + os.sep
ROOT = os.path.realpath(os.environ["RAND_EVAL_ROOT"]) + os.sep
records, frames, streams = [], [], []
RECORD, OWNER = os.environ.pop("RAND_EVAL_RECORD", None), os.getpid()

def origin(entry=None):
    """The entry point (outermost rand_engine frame) and whether the code that called it lies under the scratch root."""
    f = sys._getframe(1)
    while f and f.f_code.co_filename.startswith((LIB, __file__)):
        if f.f_code.co_filename.startswith(LIB):
            entry = f.f_code.co_name
        if "tag" in f.f_locals:
            return entry, f.f_locals["tag"]
        f = f.f_back
    return entry, f is not None and os.path.isabs(f.f_code.co_filename) and os.path.realpath(f.f_code.co_filename).startswith(ROOT)

def note(spec, entry=None):
    entry, agent = origin(entry)
    record = {"entry": entry, "spec": json.loads(json.dumps(spec, default=str)), "agent": agent}
    if record not in records:
        records.append(record)

def hashed(df, agent):
    frames.append({"agent": agent, "cols": [(str(c), len(df), _check.value_hash(df[c].tolist())) for c in df.columns]})

def listing(path):
    parent = os.path.dirname(path) or "."
    if not os.path.isdir(parent):
        return {}
    return {e.name: ((s := e.stat(follow_symlinks=False)).st_mtime_ns, s.st_size) for e in os.scandir(parent) if e.name[0] != "."}

seam = DataGenerator._file_seam
def file_seam(self):
    pair = seam(self)
    note(pair[0].args[0])
    return pair
DataGenerator._file_seam = file_seam

def wrap_get_df(cls, spec=None):
    orig = cls.get_df
    def get_df(self, *a, **k):
        out = orig(self, *a, **k)
        if spec:
            note(spec(self), "get_df")
        hashed(out.toPandas() if hasattr(out, "toPandas") else out, origin()[1])
        return out
    cls.get_df = get_df

def wrap_save(cls):
    orig = cls.save
    def save(self, path, *a, **k):
        if self.write_format == "sqlite":
            return orig(self, path, *a, **k)
        before = listing(path)
        out = orig(self, path, *a, **k)
        for name, _ in listing(path).items() - before.items():
            hashed(_check.read_artifact(os.path.join(os.path.dirname(path), name)), origin()[1])
        return out
    cls.save = save

def wrap_stream(cls):
    orig = cls.stream_dict
    def stream_dict(self, *a, **k):
        return run(orig(self, *a, **k), origin()[1])
    def run(gen, tag):
        streams.append((rows := [], tag))
        for row in gen:
            rows.append(row)
            yield row
    cls.stream_dict = stream_dict

from rand_engine.file_handlers._writer_batch import FileBatchWriter
wrap_get_df(DataGenerator); wrap_save(FileBatchWriter); wrap_stream(DataGenerator)
try:
    from rand_engine.main.spark_generator import SparkGenerator
except ImportError:
    pass
else:
    wrap_get_df(SparkGenerator, lambda gen: gen.metadata)

@atexit.register
def dump():
    if not RECORD or os.getpid() != OWNER:
        return
    for rows, agent in streams:
        hashed(pd.DataFrame(rows), agent)
    with open(RECORD, "w") as f:
        json.dump({"records": records, "frames": frames}, f)
'''


def value_hash(values):
    """SHA-256 of the values as strings; None, NaN and NaT hash as the empty string, sorted first: a column is a multiset, row order does not count."""
    import pandas as pd
    text = sorted("" if pd.isna(v) else str(v) for v in values)
    return hashlib.sha256(json.dumps(text).encode()).hexdigest()


def read_artifact(path):
    """DataFrame of a csv or json-lines file as written (text, no inference), a parquet file, or a directory of parts (entries whose name starts with `_` or `.` are hidden and skipped; the parts are concatenated in content order, never name order); gzip is decompressed."""
    import pandas as pd
    path = Path(path)
    if path.is_dir():
        return pd.concat(sorted((read_artifact(p) for p in path.iterdir() if p.is_file() and p.name[0] not in "_."), key=lambda f: f.astype(str).values.tolist()), ignore_index=True)
    name = path.name.removesuffix(".gz")
    if name.endswith(".parquet"):
        return pd.read_parquet(path)
    if name.endswith((".json", ".jsonl")):
        opener = gzip.open if path.suffix == ".gz" else open
        with opener(path, "rt", encoding="utf-8") as f:
            return pd.DataFrame([json.loads(line) for line in f if line.strip()], dtype=object)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def agent(record, field):
    """The `field` of every record or frame the agent's own code generated, in order."""
    return [r[field] for r in record if r["agent"]]


def provenance(workdir, script, artifacts, python=sys.executable):
    """(None | "provenance: ...", record): None when every artifact column equals a column the agent's code generated through rand_engine on a re-run.

    Every artifact is read and hashed as delivered before anything runs; the re-run happens in a scratch copy of `workdir` without the artifacts, and its record is compared with those hashes, so the originals are only read.
    A listed artifact the agent did not deliver fails, and so does a re-run that recorded no generation from the agent's code.
    `record` is a list of distinct {"entry", "spec", "agent"}: the entry point that ran ("get_df", "stream_dict", "save", "start"), its evaluated spec, and whether code under the scratch copy called it.
    """
    workdir, script, record = Path(workdir).resolve(), Path(script).resolve(), []
    delivered = []
    for art in artifacts:
        if not (workdir / art).exists():
            return f"provenance: artifact {art} was not delivered", record
        try:
            df = read_artifact(workdir / art)
        except Exception as e:
            return f"provenance: cannot read artifact {art}: {type(e).__name__}", record
        delivered += [(art, c, (str(c), len(df), value_hash(df[c].tolist()))) for c in df.columns]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "shim").mkdir()
        (tmp / "shim" / "sitecustomize.py").write_text(SHIM)
        shutil.copy(__file__, tmp / "shim" / "_check.py")
        scratch = tmp / "work"
        output = tmp / "record.json"
        env = {k: os.environ[k] for k in RERUN_ENV if k in os.environ}
        env.update(PYTHONPATH=os.pathsep.join(filter(None, [str(tmp / "shim"), os.environ.get("PYTHONPATH")])),
                   RAND_EVAL_RECORD=str(output), RAND_EVAL_ROOT=str(scratch), PYTHONDONTWRITEBYTECODE="1")
        target = scratch / script.relative_to(workdir) if script.is_relative_to(workdir) else script
        try:
            shutil.copytree(workdir, scratch, symlinks=True)
            for art in artifacts:
                real = (workdir / art).resolve()
                if not real.is_relative_to(workdir):
                    return f"provenance: artifact {art} resolves outside the work directory", record
                shutil.rmtree(scratch / real.relative_to(workdir), ignore_errors=True)
                (scratch / real.relative_to(workdir)).unlink(missing_ok=True)
            run = subprocess.run([python, str(target)], cwd=scratch, env=env, capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.TimeoutExpired) as e:
            return f"provenance: the script could not re-run: {type(e).__name__}", record
        if run.returncode != 0:
            return f"provenance: the script exited {run.returncode} on re-run: {run.stderr.strip()[-300:]}", record
        data = json.loads(output.read_text()) if output.exists() else {"records": [], "frames": []}
        record = data["records"]
        if not agent(record, "entry"):
            return "provenance: the re-run recorded no rand_engine generation from the agent's code", record
        recorded = {tuple(t) for cols in agent(data["frames"], "cols") for t in cols}
        if (bad := next(((a, c) for a, c, key in delivered if key not in recorded), None)):
            return f"provenance: column {bad[1]!r} of {bad[0]} matches no frame rand_engine generated", record
    return None, record


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
    return f"{layer}: {message}\nRESULT {json.dumps({'layer': layer, 'surfaces': list(surfaces)})}\n"
