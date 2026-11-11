"""Check of get-started-cli, run in the trial directory with the trial venv's python.

Layer 1: `starter/lake-example.py` exists. Layer 2: it is byte-equal to the packaged `cases/lake.py.txt`, and
the required transcript shows a Bash call of the package CLI's `get-started lake`, options in any order. Layer 3: no web
tool, within the ceiling.
"""
import itertools
import os
import shlex
import sys
from importlib import resources
from pathlib import Path

import _check

TASK_TOML = Path(__file__).resolve().parents[1] / "task.toml"
SCAFFOLD = Path("starter") / "lake-example.py"


def ran_get_started_lake(command):
    """True when a command of the line runs the package CLI's `get-started` with `lake` as its first positional.

    Commands end at a shell control operator or a newline; the line is lexed lazily, so a lexing error after a match
    does not undo it. The CLI is `rand-engine` by basename, `-m rand_engine`, or `-c` code calling `main` of `rand_engine`;
    `--out` takes a value.
    """
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = []
    try:
        for tok in itertools.chain(lexer, [";"]):
            if not set(tok) <= set(lexer.punctuation_chars):
                tokens.append(tok)
                continue
            for i, name in enumerate(tokens):
                prev = tokens[i - 1] if i else ""
                if name == "get-started" and (os.path.basename(prev) == "rand-engine" or tokens[i - 2:i - 1] == ["-m"] and prev == "rand_engine"
                                              or tokens[i - 2:i - 1] == ["-c"] and "rand_engine" in prev and "main(" in prev):
                    rest = iter(tokens[i + 1:])
                    for arg in rest:
                        if arg == "--out":
                            next(rest, None)
                        elif not arg.startswith("-"):
                            if arg == "lake":
                                return True
                            break
            tokens = []
    except ValueError:
        pass
    return False


def verdict():
    transcript = os.environ.get("RAND_EVAL_TRANSCRIPT")
    events = _check.tool_events(transcript) if transcript else []
    seen = _check.surfaces(events)
    if not SCAFFOLD.is_file():
        return "1", f"{SCAFFOLD} does not exist", seen
    packaged = (resources.files("rand_engine") / "cases" / "lake.py.txt").read_bytes()
    if SCAFFOLD.read_bytes() != packaged:
        return "2", f"{SCAFFOLD} is not byte-equal to the packaged cases/lake.py.txt", seen
    if not any(e["name"] == "Bash" and ran_get_started_lake(e["input"].get("command", ""))
                              for e in events):
        return "2", "the transcript shows no Bash call of the package CLI's get-started lake", seen
    if web := _check.web_tool_uses(events):
        return "3", f"web tools used: {web}", seen
    if msg := _check.token_ceiling(TASK_TOML, os.environ):
        return "3", msg, seen
    return None, None, seen


layer, message, seen = verdict()
if layer:
    sys.stdout.write(_check.result_text(layer, message, seen))
    sys.exit(1)
print(f"RESULT {_check.json.dumps({'layer': 'pass', 'surfaces': seen})}")
