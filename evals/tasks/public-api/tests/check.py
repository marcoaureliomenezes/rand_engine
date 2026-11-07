"""Usage check, run in the trial directory: layer 1 the artifact, layer 2 provenance, layer 3 the public-API import shape."""
import ast
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd
import rand_engine

COLUMNS = ["id", "score"]


def fail(layer, message):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

# Layer 1: the asked rows and column set, and the installed version the script wrote.
try:
    df = pd.read_parquet("people.parquet")
except Exception as e:
    fail("1", f"people.parquet unreadable: {type(e).__name__}")
if len(df) != 100 or set(df.columns) != set(COLUMNS):
    fail("1", f"expected 100 rows and columns {COLUMNS}, got {len(df)} rows and {list(df.columns)}")
try:
    written = Path("version.txt").read_text(encoding="utf-8", errors="ignore").strip()
except OSError as e:
    fail("1", f"version.txt unreadable: {type(e).__name__}")
if written != rand_engine.__version__:
    fail("1", f"version.txt holds {written!r}, expected the installed version {rand_engine.__version__!r}")

# Layer 2: the script's re-run (same seed, same frames) regenerates every column through rand_engine.
msg, _ = _check.provenance(".", "solve.py", ["people.parquet"], python=sys.executable)
if msg:
    fail("2", msg)

# Layer 3: only top-level rand_engine imports, no legacy names in the agent's files, token ceiling, no web.
script = Path("solve.py").read_text(encoding="utf-8", errors="ignore")
nodes = list(ast.walk(ast.parse(script)))
submodules = sorted(
    {a.name for n in nodes if isinstance(n, ast.Import) for a in n.names if a.name.startswith("rand_engine.")}
    | {n.module for n in nodes if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("rand_engine.")})
if submodules:
    fail("3", f"solve.py imports rand_engine submodules: {submodules}")
if (hits := [h for p in Path(".").glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8", errors="ignore"))]):
    fail("3", f"legacy names in the agent's .py files: {hits}")
if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
    fail("3", msg)
if (web := _check.web_tool_uses(events)):
    fail("3", f"web tools used: {web}")

print("RESULT " + json.dumps({"layer": "pass", "surfaces": surfaces}))
