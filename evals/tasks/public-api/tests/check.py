"""Usage check, run in the trial directory: layer 1 the artifact, layer 2 provenance, layer 3 the public-API import shape."""
import ast
import json
import os
import sys
from pathlib import Path

import _check
import pandas as pd

COLUMNS = ["id", "score"]
specs = []


def fail(layer, message):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

# Layer 1: the asked rows and columns.
try:
    df = pd.read_parquet("people.parquet")
except Exception as e:
    fail("1", f"people.parquet unreadable: {type(e).__name__}")
if len(df) != 100 or list(df.columns) != COLUMNS:
    fail("1", f"expected 100 rows and columns {COLUMNS}, got {len(df)} rows and {list(df.columns)}")

# Layer 2: the script's re-run (same seed, same frames) regenerates every column through rand_engine.
if (msg := _check.provenance(".", "solve.py", ["people.parquet"], python=sys.executable, specs=specs)):
    fail("2", msg)

# Layer 3: only top-level rand_engine imports, the version printed, no legacy names, token ceiling, no web.
script = Path("solve.py").read_text(encoding="utf-8")
nodes = list(ast.walk(ast.parse(script)))
submodules = sorted(
    {a.name for n in nodes if isinstance(n, ast.Import) for a in n.names if a.name.startswith("rand_engine.")}
    | {n.module for n in nodes if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("rand_engine.")})
if submodules:
    fail("3", f"solve.py imports rand_engine submodules: {submodules}")
prints_version = any(
    isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"
    and any(isinstance(a, ast.Attribute) and a.attr == "__version__"
            and isinstance(a.value, ast.Name) and a.value.id == "rand_engine" for a in ast.walk(n))
    for n in nodes)
if not prints_version:
    fail("3", "solve.py does not print rand_engine.__version__")
if (hits := _check.legacy_hits(script)):
    fail("3", f"legacy names in solve.py: {hits}")
if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
    fail("3", msg)
if (web := _check.web_tool_uses(events)):
    fail("3", f"web tools used: {web}")

print("PASS")
print("RESULT " + json.dumps({"surfaces": surfaces}))
