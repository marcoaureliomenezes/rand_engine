"""E1 record, run in the trial directory with the trial venv's python: prints one JSON line saying
whether rand-engine is installed, whether the agent's own files import it, and which syntax era
they use. Always exits 0."""

import importlib.util
import json
import re
from pathlib import Path

files = [
    p for p in Path(".").rglob("*")
    if p.is_file() and p.suffix == ".py" and "site-packages" not in p.parts
]
py = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in files)
installed = importlib.util.find_spec("rand_engine") is not None or any(
    Path(".").rglob("site-packages/rand_engine/__init__.py")
)
imported = bool(re.search(r"^\s*(from|import)\s+rand_engine", py, re.M))
if re.search(r"RandGenerator|rand_engine\.main\.|rand_engine\.core\.", py):
    era = "legacy"
elif imported and "DataGenerator" in py and '"kwargs"' in py.replace("'", '"'):
    era = "dict-spec"
else:
    era = "unknown" if imported else "none"
print(json.dumps({"installed": installed, "imported": imported, "era": era}))
