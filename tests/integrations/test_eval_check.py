"""evals/_check.py: the three check layers' shared helper, on 10-row scripts written under tmp_path.

Contract under test (loaded by path, no Spark, no network, no agent):
  provenance(workdir, script, artifacts, python=sys.executable) -> None | str   (layer 2; str starts "provenance")
  value_hash(values) -> str                                                      (D7)
  legacy_hits(text) -> list[str]                                                 (layer 3, the seven legacy items)
  documented_method(spec, method, kwargs) -> bool                                (layer 3, the task's method and kwargs)
  token_ceiling(task_toml, env) -> None | str                                    (None: within, or skipped with no env)
  tool_events(transcript) -> list[{"name", "input"}]                             (the one transcript reader)
  web_tool_uses(events) -> list[str]; surfaces(events) -> list[str]
  result_text(layer, message, surfaces=()) -> str                                (failure line, then the D2 RESULT line)
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

CHECK = Path(__file__).resolve().parents[2] / "evals" / "_check.py"
SPEC = '{"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}'
TOKENS = ["llms.txt", "help(", "get-started", "cases/", "examples/", "method_specs", "SpecValidationError"]


@pytest.fixture(scope="module")
def check():
    assert CHECK.is_file(), f"{CHECK} does not exist"
    spec = importlib.util.spec_from_file_location("eval_check", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def script(tmp_path, body):
    (tmp_path / "make.py").write_text(body)
    return tmp_path / "make.py"


def provenance(check, tmp_path, body):
    return check.provenance(tmp_path, script(tmp_path, body), ["out.csv"], python=sys.executable)


def test_generator_made_file_passes(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).get_df().to_csv('out.csv', index=False)\n"
    assert provenance(check, tmp_path, body) is None


def test_writer_made_file_passes(check, tmp_path):
    body = f'from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format("csv").save("out.csv")\n'
    assert provenance(check, tmp_path, body) is None


def test_numpy_file_beside_decorative_call_fails(check, tmp_path):
    body = (
        "import numpy as np, pandas as pd\nfrom rand_engine import DataGenerator\n"
        f"DataGenerator({SPEC}, seed=1).size(10).get_df()\n"
        "pd.DataFrame({'age': np.arange(100, 110)}).to_csv('out.csv', index=False)\n"
    )
    msg = provenance(check, tmp_path, body)
    assert msg.startswith("provenance")


def test_script_that_cannot_rerun_fails_as_provenance(check, tmp_path):
    msg = provenance(check, tmp_path, "from rand_engine import DataGenerator\nraise SystemExit(3)\n")
    assert msg.startswith("provenance")


def test_missing_script_fails_as_provenance(check, tmp_path):
    assert check.provenance(tmp_path, tmp_path / "gone.py", ["out.csv"], python=sys.executable).startswith("provenance")


def test_static_check_names_the_missing_import(check, tmp_path):
    msg = provenance(check, tmp_path, "import pandas as pd\npd.DataFrame({'age': [1]}).to_csv('out.csv', index=False)\n")
    assert msg.startswith("provenance") and "rand_engine" in msg


def test_null_rule(check):
    assert check.value_hash([None, "a"]) == check.value_hash([float("nan"), "a"]) == check.value_hash(["", "a"])
    assert check.value_hash([1, 2]) != check.value_hash([2, 1])


@pytest.mark.parametrize("text, name", [
    ("from rand_engine import ExampleSpecs", "ExampleSpecs"),
    ('spec = {"constraints": {"pk": {}}}', "constraints"),
    ("gen.db_checkpoint('x.db')", "db_checkpoint"),
    ('DataGenerator(spec).option("reset_checkpoint", True)', "option"),
    ('{"method": "uuid4", "kwargs": {"length": 8}}', "uuid4 length"),
    ('{"method": "integers", "args": [1, 9]}', "args"),
    ('{"splitable": True, "sep": ";"}', "splitable"),
    ("from rand_engine import validate_with_warnings", "validate_with_warnings"),
    ("validate_spark_with_warnings(spec)", "validate_with_warnings"),
])
def test_legacy_name_is_caught(check, text, name):
    assert name in check.legacy_hits(text)


@pytest.mark.parametrize("text", [
    "from rand_engine import RandGenerator",
    "from rand_engine.main import DataGenerator",
    "from rand_engine.templates import x",
    '{"id": {"method": "pk", "kwargs": {}}}',
    '{"method": "uuid4", "kwargs": {}}',
    'DataGenerator(spec).size(10).write.format("csv").option("header", True).save("o")',
    "from rand_engine import RandSpecs",
])
def test_current_names_are_not_caught(check, text):
    assert check.legacy_hits(text) == []


def test_documented_method_and_kwargs(check):
    spec = json.loads(SPEC)
    assert check.documented_method(spec, "integers", {"min", "max"})
    assert not check.documented_method(spec, "floats", {"min"})
    assert not check.documented_method(spec, "integers", {"min", "step"})


def stream(*tool_uses):
    return "\n".join(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "text", "text": "x"}, {"type": "tool_use", "name": n, "input": i}]}}) for n, i in tool_uses) + "\n"


def test_tool_events_and_web_use(check, tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text(stream(("Bash", {"command": "ls"}), ("WebFetch", {"url": "https://pypi.org/project/rand-engine"})) + '{"type": "result"}\n')
    events = check.tool_events(t)
    assert [e["name"] for e in events] == ["Bash", "WebFetch"]
    assert events[0]["input"] == {"command": "ls"}
    assert check.web_tool_uses(events) == ["WebFetch"]
    assert check.web_tool_uses(events[:1]) == []


def test_ceiling(check, tmp_path):
    toml = tmp_path / "task.toml"
    toml.write_text("[task]\nround = \"usage\"\n[limits]\nceiling_tokens = 1000\n")
    assert check.token_ceiling(toml, {"RAND_EVAL_TOKENS": "1000"}) is None
    assert "1001" in check.token_ceiling(toml, {"RAND_EVAL_TOKENS": "1001"})
    assert check.token_ceiling(toml, {}) is None


@pytest.mark.parametrize("token", TOKENS)
def test_each_surface_token_is_matched(check, token):
    events = [{"name": "Bash", "input": {"command": f"cat x # {token}"}}, {"name": "Bash", "input": {"command": "ls"}}]
    assert check.surfaces(events) == [token]


def test_surfaces_read_any_input_field(check):
    assert check.surfaces([{"name": "Read", "input": {"file_path": "/v/rand_engine/llms.txt"}}]) == ["llms.txt"]


def test_failing_result_names_layer_and_ends_with_result_line(check):
    out = check.result_text("provenance", "provenance: no rand_engine import", ["llms.txt"])
    lines = out.strip().splitlines()
    assert "provenance" in lines[0]
    assert lines[-1].startswith("RESULT ")
    assert json.loads(lines[-1][len("RESULT "):]) == {"layer": "provenance", "surfaces": ["llms.txt"]}
