"""Discovery record, run in the trial directory with the trial venv's python: prints one RESULT line
saying whether the agent adopted rand-engine and which surface it reached first. Always exits 0."""

import json
import os
import re
from pathlib import Path

import _check

NAME = re.compile(r"rand[-_]engine", re.I)
INSTALL = re.compile(r"(pip|uv|poetry|pipx)\b[^\n;&|]*\b(install|add)\b[^\n;&|]*rand[-_]engine", re.I)
IMPORT = re.compile(r"^\s*(from|import)\s+rand_engine", re.M)


def surface(event):
    blob = json.dumps(event["input"])
    if event["name"] == "WebSearch":
        return "search"
    if "pypi.org" in blob:
        return "PyPI"
    if re.search(r"readthedocs|github\.io|docs\.", blob):
        return "docs site"
    if "README" in blob:
        return "README"
    return "other"


events = _check.tool_events(os.environ["RAND_EVAL_TRANSCRIPT"]) if "RAND_EVAL_TRANSCRIPT" in os.environ else []
named = [e for e in events if NAME.search(json.dumps(e["input"]))]
py = "\n".join(
    p.read_text(encoding="utf-8", errors="ignore") for p in Path(".").rglob("*.py")
    if "site-packages" not in p.parts and ".venv" not in p.parts
)
installed = any(INSTALL.search(e["input"].get("command", "")) for e in events)
print("RESULT " + json.dumps({
    "adopted": installed and bool(IMPORT.search(py)),
    "surface": surface(named[0]) if named else "other",
    "legacy": _check.legacy_hits(py),
}))
