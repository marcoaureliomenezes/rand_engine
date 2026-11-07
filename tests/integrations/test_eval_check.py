"""evals/_check.py: the three check layers' shared helper, on 10-row scripts written under tmp_path.

Contract under test (loaded by path, no Spark, no network, no agent; the re-run's interpreter gets
`rand_engine` and `evals` through the PYTHONPATH the test sets, as the runner does):
  provenance(workdir, script, artifacts, python=sys.executable, specs=None) -> None | str   (layer 2)
      The re-run happens in a scratch copy of workdir without the artifacts. provenance grades the artifacts as
      delivered, reading them before the re-run, and itself writes nothing in workdir; the re-run may write
      wherever the script's own paths point. A failure string starts "provenance". When `specs` is a list, the spec each recorded
      `DataGenerator` got is appended to it (the choice for F6: the re-run's records feed `documented_method`).
      Csv and json-lines artifacts are read as written text, with no dtype or NA inference.
  value_hash(values) -> str                                           (nulls hash as the empty string)
  legacy_hits(text) -> list[str]                                      (layer 3, the seven legacy items)
  documented_method(specs, method, kwargs) -> bool                    (layer 3: judges the recorded specs; True when
      some recorded spec dict has a column of `method` whose kwargs hold every name in `kwargs`; a non-dict
      column value is skipped, never raised on). A callable spec is recorded as the dict it returns.
  token_ceiling(task_toml, env) -> None | str                         (None: within, or skipped with no env)
  tool_events(transcript) -> list[{"name", "input"}]                  (the one transcript reader)
  web_tool_uses(events) -> list[str]; surfaces(events) -> list[str]
  result_text(layer, message, surfaces=()) -> str                     (failure line, then the `RESULT {json}` line)
"""
import importlib.util
import json
import os
import subprocess
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


REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def pythonpath(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", f"{REPO}{os.pathsep}{REPO / 'evals'}")


def run_script(tmp_path, body):
    """Deliver the artifacts the way a trial does: the agent's own run, in the workdir."""
    subprocess.run([sys.executable, str(script(tmp_path, body))], cwd=tmp_path, capture_output=True)


def provenance(check, tmp_path, body, artifacts=("out.csv",), deliver=True, specs=None, **extra):
    if deliver:
        run_script(tmp_path, body)
    return check.provenance(tmp_path, script(tmp_path, body), list(artifacts), python=sys.executable, specs=specs, **extra)


SEEDED = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).get_df().to_csv('out.csv', index=False)\n"


def test_generator_made_file_passes(check, tmp_path):
    assert provenance(check, tmp_path, SEEDED) is None


def test_zero_padded_column_passes(check, tmp_path):
    spec = '{"uid": {"method": "int_zfilled", "kwargs": {"length": 8}}}'
    body = f"from rand_engine import DataGenerator\nDataGenerator({spec}, seed=1).size(10).get_df().to_csv('out.csv', index=False)\n"
    assert provenance(check, tmp_path, body) is None


def test_replaced_artifact_fails(check, tmp_path):
    run_script(tmp_path, SEEDED)
    (tmp_path / "out.csv").write_text("age\n" + "\n".join(str(i) for i in range(100, 110)) + "\n")
    assert provenance(check, tmp_path, SEEDED, deliver=False).startswith("provenance")


def test_unseeded_script_fails(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}).size(10).get_df().to_csv('out.csv', index=False)\n"
    run_script(tmp_path, body)
    assert provenance(check, tmp_path, body, deliver=False).startswith("provenance")


def test_agent_artifact_is_never_modified(check, tmp_path):
    run_script(tmp_path, SEEDED)
    before = (tmp_path / "out.csv").read_bytes()
    assert provenance(check, tmp_path, SEEDED, deliver=False) is None
    assert (tmp_path / "out.csv").read_bytes() == before
    (tmp_path / "out.csv").write_text("age\n999\n")
    provenance(check, tmp_path, SEEDED, deliver=False)
    assert (tmp_path / "out.csv").read_text() == "age\n999\n"


def test_spark_parts_directory_skips_hidden_files(check, tmp_path):
    import pandas as pd
    out = tmp_path / "out.parquet"
    out.mkdir()
    pd.DataFrame({"id": [1, 2, 3]}).to_parquet(out / "part-00000.snappy.parquet", index=False)
    (out / "_SUCCESS").write_text("")
    (out / ".part-00000.snappy.parquet.crc").write_bytes(b"crc\x00\xff")
    assert check.read_artifact(out).to_dict("list") == {"id": [1, 2, 3]}


def test_parts_directory_frame_does_not_depend_on_part_names(check, tmp_path):
    for d, names in {"x": ("part_a", "part_b"), "y": ("part_b", "part_a")}.items():
        (tmp_path / d).mkdir()
        (tmp_path / d / f"{names[0]}.csv").write_text("age\n1\n2\n")
        (tmp_path / d / f"{names[1]}.csv").write_text("age\n3\n4\n")
    for d in ("x", "y"):
        assert check.read_artifact(tmp_path / d).to_dict("list") == {"age": ["1", "2", "3", "4"]}


def test_jsonl_artifact_read_as_written(check, tmp_path):
    spec = '{"uid": {"method": "int_zfilled", "kwargs": {"length": 8}}}'
    body = ("from rand_engine import DataGenerator\n"
            f"DataGenerator({spec}, seed=1).size(10).get_df().to_json('out.jsonl', orient='records', lines=True)\n")
    assert provenance(check, tmp_path, body, ["out.jsonl"]) is None


def test_inherited_pythonpath_entry_is_kept(check, tmp_path, monkeypatch):
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    (fixtures / "helper_mod.py").write_text("SIZE = 10\n")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(REPO), str(fixtures)]))
    body = f"from rand_engine import DataGenerator\nimport helper_mod\nDataGenerator({SPEC}, seed=1).size(helper_mod.SIZE).get_df().to_csv('out.csv', index=False)\n"
    assert provenance(check, tmp_path, body) is None


def test_writer_made_file_passes(check, tmp_path):
    body = f'from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format("csv").save("out.csv")\n'
    assert provenance(check, tmp_path, body) is None


BATCH_VIA_VARIABLE = (f"from rand_engine import DataGenerator\nw = DataGenerator({SPEC}, seed=1).size(10).write.format('csv')\n"
                      "w.save('out.csv')\n")
STREAM_VIA_VARIABLE = (f"from rand_engine import DataGenerator\n"
                       f"w = DataGenerator({SPEC}, seed=1).size(10).writeStream.format('csv').trigger(frequency=0.2).option('timeout', 1)\n"
                       "w.start('sink')\n")
UNCALLED_WRITERS = SEEDED + "def unused(g):\n    g.write.save('x')\n    g.writeStream.start('y')\n"


@pytest.mark.parametrize("body, artifacts, expected", [
    (BATCH_VIA_VARIABLE, ["out.csv"], ["save"]),
    (STREAM_VIA_VARIABLE, [], ["start"]),
    (UNCALLED_WRITERS, ["out.csv"], []),
], ids=["batch-via-variable", "stream-via-variable", "never-called"])
def test_provenance_reports_the_writer_entry_points_that_ran(check, tmp_path, body, artifacts, expected):
    calls = []
    assert provenance(check, tmp_path, body, artifacts, calls=calls) is None
    assert calls == expected


def test_rerun_env_keeps_java_home(check, tmp_path, monkeypatch):
    monkeypatch.setenv("JAVA_HOME", "/opt/jh")
    assert provenance(check, tmp_path, SEEDED + "import os\nassert os.environ.get('JAVA_HOME') == '/opt/jh'\n") is None


def test_rerun_writes_no_bytecode(check, tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    assert provenance(check, tmp_path, SEEDED + "import sys\nassert sys.dont_write_bytecode\n") is None


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


def test_rerun_writing_by_absolute_path_cannot_launder_the_artifact(check, tmp_path):
    (tmp_path / "out.csv").write_text("age\n" + "\n".join(str(i) for i in range(100, 110)) + "\n")
    body = (
        "from rand_engine import DataGenerator\n"
        f"DataGenerator({SPEC}, seed=1).size(10).get_df().to_csv({str(tmp_path / 'out.csv')!r}, index=False)\n"
    )
    msg = provenance(check, tmp_path, body, deliver=False)
    assert msg == "provenance: column 'age' of out.csv matches no frame rand_engine generated"


def test_symlink_loop_artifact_fails_as_not_delivered(check, tmp_path):
    (tmp_path / "out.csv").symlink_to("out.csv")
    msg = provenance(check, tmp_path, SEEDED, deliver=False)
    assert msg == "provenance: artifact out.csv was not delivered"


def test_dangling_link_that_is_not_an_artifact_is_skipped(check, tmp_path):
    (tmp_path / "stale.csv").symlink_to("missing.csv")
    assert provenance(check, tmp_path, SEEDED) is None


def test_self_loop_that_is_not_an_artifact_is_skipped(check, tmp_path):
    (tmp_path / "loop").symlink_to("loop")
    assert provenance(check, tmp_path, SEEDED) is None


def test_absent_artifact_fails(check, tmp_path):
    msg = provenance(check, tmp_path, SEEDED, deliver=False)
    assert msg.startswith("provenance") and "out.csv" in msg


def test_missing_script_fails_as_provenance(check, tmp_path):
    assert check.provenance(tmp_path, tmp_path / "gone.py", ["out.csv"], python=sys.executable).startswith("provenance")


def test_static_check_names_the_missing_import(check, tmp_path):
    msg = provenance(check, tmp_path, "import pandas as pd\npd.DataFrame({'age': [1]}).to_csv('out.csv', index=False)\n")
    assert msg == "provenance: the script does not import rand_engine"


def test_static_check_names_the_missing_call(check, tmp_path):
    msg = provenance(check, tmp_path, "import rand_engine\nopen('out.csv', 'w').write('age\\n1\\n')\n")
    assert msg == "provenance: the script imports rand_engine but calls none of its generating API"


def test_null_rule(check):
    assert check.value_hash([None, "a"]) == check.value_hash([float("nan"), "a"]) == check.value_hash(["", "a"])
    assert check.value_hash([1, 2]) == check.value_hash([2, 1])


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
    specs = [json.loads(SPEC)]
    assert check.documented_method(specs, "integers", {"min", "max"})
    assert check.documented_method(specs, "integers", {"min"})
    assert not check.documented_method(specs, "floats", {"min"})
    assert not check.documented_method(specs, "integers", {"min", "step"})
    assert not check.documented_method([], "integers", {"min"})


@pytest.mark.parametrize("value", ["text", [1], None, 3])
def test_documented_method_never_raises_on_a_non_dict_column_value(check, value):
    assert check.documented_method([{"a": value}], "integers", {"min"}) is False


def test_recorded_specs_are_judged(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).get_df().to_csv('out.csv', index=False)\n"
    specs = []
    msg = provenance(check, tmp_path, body, specs=specs)
    assert msg is None
    assert check.documented_method(specs, "integers", {"min", "max"})
    assert not check.documented_method(specs, "floats", {"min", "max"})


def test_callable_spec_is_judged_by_its_evaluated_dict(check, tmp_path):
    body = (f"from rand_engine import DataGenerator\nDataGenerator(lambda: {SPEC}, seed=1).size(10).get_df()"
            ".to_csv('out.csv', index=False)\n")
    specs = []
    msg = provenance(check, tmp_path, body, specs=specs)
    assert msg is None
    assert check.documented_method(specs, "integers", {"min", "max"})


def test_batch_save_records_the_spec(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('out.csv')\n"
    specs = []
    assert provenance(check, tmp_path, body, specs=specs) is None
    assert check.documented_method(specs, "integers", {"min", "max"})


def test_stream_start_records_the_spec(check, tmp_path):
    body = (f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).writeStream.format('csv')"
            ".trigger(frequency=0.1).option('timeout', 0.3).start('out')\n")
    specs = []
    provenance(check, tmp_path, body, artifacts=("out",), specs=specs)
    assert check.documented_method(specs, "integers", {"min", "max"})


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
    out = check.result_text("2", "provenance: no rand_engine import", ["llms.txt"])
    lines = out.strip().splitlines()
    assert "provenance" in lines[0]
    assert lines[-1].startswith("RESULT ")
    assert json.loads(lines[-1][len("RESULT "):]) == {"layer": "2", "surfaces": ["llms.txt"]}


def test_check_imports_without_pandas():
    env = {**os.environ, "PYTHONPATH": str(REPO / "evals")}
    done = subprocess.run([sys.executable, "-c", "import sys; sys.modules['pandas'] = None; import _check"],
                          env=env, capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def test_sqlite_save_is_recorded_not_read_back(check, tmp_path):
    body = ("from rand_engine import DataGenerator\n"
            f"g = DataGenerator({SPEC}, seed=1).size(10)\n"
            "g.write.format('sqlite').option('table', 't').save('out.sqlite')\n"
            "g.get_df().to_csv('out.csv', index=False)\n")
    assert provenance(check, tmp_path, body, ["out.csv"]) is None


def test_child_python_process_outliving_the_script_does_not_overwrite_the_record(check, tmp_path):
    body = ("import subprocess, sys\n" + SEEDED +
            "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(1)'])\n")
    assert provenance(check, tmp_path, body) is None
