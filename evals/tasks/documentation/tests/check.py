"""Documentation task check, run in the trial dir with the trial venv's python.

Layer 1 ("artifact"): answer.txt exists. Layer 2 ("provenance"): its URL is a link of the installed rand_engine/llms.txt (D8, no shim).
Layer 3: the URL is the page that documents `writeStream` options, no web tool, within the ceiling.
"""
import os
import re
import sys
from pathlib import Path

import _check
import rand_engine

TASK_TOML = Path(__file__).resolve().parent.parent / "task.toml"
events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if os.environ.get("RAND_EVAL_TRANSCRIPT") else []
surfaces = _check.surfaces(events)
answer = Path("answer.txt")
if not answer.is_file():
    sys.exit(print(_check.result_text("1", "answer.txt was not written", surfaces), end="") or 1)
url = answer.read_text(encoding="utf-8", errors="ignore").strip()

llms = (Path(rand_engine.__file__).parent / "llms.txt").read_text(encoding="utf-8")
links = {m[0]: m[1] for m in re.findall(r"\]\(([^)\s]+)\)(?::\s*(.*))?", llms)}
if url not in links:
    sys.exit(print(_check.result_text("2", f"{url} is not a link of the installed llms.txt", surfaces), end="") or 1)

if "writeStream" not in links[url]:
    sys.exit(print(_check.result_text("3", f"{url} is not the page documenting writer options", surfaces), end="") or 1)
if (msg := _check.token_ceiling(TASK_TOML, os.environ)):
    sys.exit(print(_check.result_text("3", msg, surfaces), end="") or 1)
if (web := _check.web_tool_uses(events)):
    sys.exit(print(_check.result_text("3", f"web tools used: {web}", surfaces), end="") or 1)
import json
print("RESULT " + json.dumps({"layer": "pass", "surfaces": surfaces}))
