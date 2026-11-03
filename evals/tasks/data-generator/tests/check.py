"""Usage check, run in the trial directory: layer 1 the artifact, layer 2 provenance, layer 3 the documented features."""
import os
import sys
from pathlib import Path

import _check
import pandas as pd

COLUMNS = ["age", "salary", "salary_k"]
specs = []


def fail(layer, message):
    print(_check.result_text(layer, message, surfaces), end="")
    sys.exit(1)


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
surfaces = _check.surfaces(events)

# Layer 1: the asked rows, columns and nulls.
try:
    df = pd.read_parquet("users.parquet")
except Exception as e:
    fail("1", f"users.parquet unreadable: {type(e).__name__}")
if len(df) != 500 or sorted(df.columns) != sorted(COLUMNS):
    fail("1", f"expected 500 rows and the column set {COLUMNS}, got {len(df)} rows and {list(df.columns)}")
if not 0.03 <= df["age"].isna().mean() <= 0.2:
    fail("1", f"age null share {df['age'].isna().mean():.2f} is not about 0.10")
if not ((df["salary"] / 1000 - df["salary_k"]).abs() < 1e-6).all():
    fail("1", "salary_k is not salary / 1000")

# Layer 2: the script's re-run (same seed, same frames) regenerates every column through rand_engine.
if (msg := _check.provenance(".", "solve.py", ["users.parquet"], python=sys.executable, specs=specs)):
    fail("2", msg)

# Layer 3: documented features, no legacy names, token ceiling, no web.
script = Path("solve.py").read_text(encoding="utf-8")
if not any(isinstance(c, dict) and c.get("null_rate") for spec in specs for c in spec.values()):
    fail("3", "the recorded spec has no column with null_rate")
if "transformers" not in script:
    fail("3", "solve.py does not use transformers for the derived column")
if (hits := [h for p in Path(".").glob("*.py") for h in _check.legacy_hits(p.read_text(encoding="utf-8"))]):
    fail("3", f"legacy names: {sorted(set(hits))}")
if (msg := _check.token_ceiling(Path(__file__).parent.parent / "task.toml", os.environ)):
    fail("3", msg)
if (web := _check.web_tool_uses(events)):
    fail("3", f"web tools used: {web}")

print("PASS")
print(f'RESULT {{"surfaces": {surfaces!r}}}'.replace("'", '"'))
