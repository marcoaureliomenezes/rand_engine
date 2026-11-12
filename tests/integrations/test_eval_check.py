"""evals/_check.py: the three check layers' shared helper, on 10-row scripts written under tmp_path.

Contract under test (loaded by path, no Spark, no network, no agent; the re-run's interpreter gets
`rand_engine` and `evals` through the PYTHONPATH the test sets, as the runner does):
  provenance(workdir, script, artifacts, python=sys.executable) -> (None | str, generations)   (layer 2)
      The re-run happens in a scratch copy of workdir without the artifacts. provenance grades the artifacts as
      delivered, reading them before the re-run, and itself writes nothing in workdir; the re-run may write
      wherever the script's own paths point. A failure string starts "provenance". `generations` holds one
      {"entry", "spec", "agent"} per distinct generation: `entry` is get_df, stream_dict, save or start (sqlite
      and multi-file saves are `save`), `spec` the evaluated spec dict, `agent` True when the calling frame's file
      lies under the scratch copy (the script or a module written beside it). An artifact column passes only
      against output of an agent generations.
      Csv and json-lines artifacts are read as written text, with no dtype or NA inference.
  value_hash(values) -> str                                           (nulls hash as the empty string; a column's values hash as a
      multiset, so order does not count)
  legacy_hits(text) -> list[str]                                      (layer 3, the eight legacy items)
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
import shutil
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
    subprocess.run([sys.executable, str(script(tmp_path, body))], cwd=tmp_path, capture_output=True,
                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


def rerun(check, tmp_path, body, artifacts=("out.csv",), deliver=True):
    if deliver:
        run_script(tmp_path, body)
    return check.provenance(tmp_path, script(tmp_path, body), list(artifacts), python=sys.executable)


def provenance(check, tmp_path, body, artifacts=("out.csv",), deliver=True):
    return rerun(check, tmp_path, body, artifacts, deliver)[0]


def agent_specs(generations):
    return [r["spec"] for r in generations if r["agent"]]


NO_AGENT_RECORD = "provenance: the re-run recorded no rand_engine generation from the agent's code"
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


def test_provenance_leaves_the_delivered_artifact_as_it_was(check, tmp_path):
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


SQLITE_SAVE = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('sqlite').option('table', 't').save('out.sqlite')\n"
TWICE = f"from rand_engine import DataGenerator\ng = DataGenerator({SPEC}, seed=1).size(10)\ng.get_df()\ng.get_df().to_csv('out.csv', index=False)\n"


@pytest.mark.parametrize("body, artifacts, expected", [
    (BATCH_VIA_VARIABLE, ["out.csv"], ["save"]),
    (STREAM_VIA_VARIABLE, [], ["start"]),
    (SQLITE_SAVE, [], ["save"]),
    (TWICE, ["out.csv"], ["get_df"]),
    (UNCALLED_WRITERS, ["out.csv"], ["get_df"]),
], ids=["batch-via-variable", "stream-start-once", "sqlite-is-save", "repeated-call-is-one-entry", "never-called"])
def test_provenance_reports_the_deduplicated_entry_points_that_ran(check, tmp_path, body, artifacts, expected):
    msg, generations = rerun(check, tmp_path, body, artifacts)
    assert msg is None
    assert [r["entry"] for r in generations if r["agent"]] == expected


def stream_body(tail):
    return f"from rand_engine import DataGenerator\nimport itertools\nrows = list(itertools.islice(DataGenerator({SPEC}, seed=1).size(10).stream_dict(1000, 1000), 2))\n{tail}"


@pytest.mark.parametrize("body, artifacts, entry", [
    (SEEDED, ["out.csv"], "get_df"),
    (stream_body(""), [], "stream_dict"),
    (f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('out.csv')\n", ["out.csv"], "save"),
    (SQLITE_SAVE, [], "save"),
    (STREAM_VIA_VARIABLE, [], "start"),
], ids=["get_df", "stream_dict", "save-csv", "save-sqlite", "start"])
def test_each_generation_path_leaves_one_record_with_its_spec_and_entry(check, tmp_path, body, artifacts, entry):
    msg, generations = rerun(check, tmp_path, body, artifacts)
    assert msg is None
    assert generations == [{"entry": entry, "spec": json.loads(SPEC), "agent": True}]


def test_rerun_env_keeps_java_home(check, tmp_path, monkeypatch):
    monkeypatch.setenv("JAVA_HOME", "/opt/jh")
    assert provenance(check, tmp_path, SEEDED + "import os\nassert os.environ.get('JAVA_HOME') == '/opt/jh'\n") is None


def test_rerun_writes_no_bytecode(check, tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONDONTWRITEBYTECODE", raising=False)
    before = set((REPO / "rand_engine").rglob("*.pyc"))
    assert provenance(check, tmp_path, SEEDED + "import sys\nassert sys.dont_write_bytecode\n") is None
    assert set((REPO / "rand_engine").rglob("*.pyc")) == before


def test_numpy_file_beside_decorative_call_fails(check, tmp_path):
    body = (
        "import numpy as np, pandas as pd\nfrom rand_engine import DataGenerator\n"
        f"DataGenerator({SPEC}, seed=1).size(10).get_df()\n"
        "pd.DataFrame({'age': np.arange(100, 110)}).to_csv('out.csv', index=False)\n"
    )
    msg, generations = rerun(check, tmp_path, body)
    assert msg.startswith("provenance")
    assert generations == [{"entry": "get_df", "spec": json.loads(SPEC), "agent": True}]


def test_numpy_file_beside_a_writer_that_ran_on_other_data_fails(check, tmp_path):
    body = (
        "import numpy as np, pandas as pd\nfrom rand_engine import DataGenerator\n"
        f"DataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('other.csv')\n"
        "pd.DataFrame({'age': np.arange(100, 110)}).to_csv('out.csv', index=False)\n"
    )
    msg, generations = rerun(check, tmp_path, body)
    assert msg.startswith("provenance")
    assert generations == [{"entry": "save", "spec": json.loads(SPEC), "agent": True}]


def test_generation_called_from_a_module_beside_the_script_is_the_agents(check, tmp_path):
    (tmp_path / "gen_helper.py").write_text(
        "def make(gen):\n    return gen.size(10).get_df()\n")
    body = f"import gen_helper\nfrom rand_engine import DataGenerator\ngen_helper.make(DataGenerator({SPEC}, seed=1)).to_csv('out.csv', index=False)\n"
    msg, generations = rerun(check, tmp_path, body)
    assert msg is None
    assert generations == [{"entry": "get_df", "spec": json.loads(SPEC), "agent": True}]


def test_generation_called_from_outside_the_scratch_copy_is_not_the_agents(check, tmp_path, monkeypatch):
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "gen_lib.py").write_text(
        "def make(gen):\n    return gen.size(10).get_df()\n")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([str(REPO), str(lib)]))
    work = tmp_path / "work"
    work.mkdir()
    body = f"import gen_lib\nfrom rand_engine import DataGenerator\ngen_lib.make(DataGenerator({SPEC}, seed=1)).to_csv('out.csv', index=False)\n"
    msg, generations = rerun(check, work, body)
    assert msg == NO_AGENT_RECORD
    assert generations == [{"entry": "get_df", "spec": json.loads(SPEC), "agent": False}]


OWN_STREAM = f"from rand_engine import DataGenerator\nimport itertools\nstream = DataGenerator({SPEC}, seed=1).size(10).stream_dict(1000, 1000)\n"


@pytest.mark.parametrize("consume", [
    "import pandas as pd\npd.DataFrame(itertools.islice(stream, 5))[['age']].to_csv('out.csv', index=False)\n",
    "import csv\nwith open('out.csv', 'w', newline='') as f:\n    w = csv.DictWriter(f, fieldnames=['age'], extrasaction='ignore')\n    w.writeheader()\n    w.writerows(itertools.islice(stream, 5))\n",
], ids=["pandas-dataframe", "csv-dictwriter"])
def test_agents_own_stream_dict_consumed_by_a_library_passes(check, tmp_path, consume):
    assert provenance(check, tmp_path, OWN_STREAM + consume) is None


def test_dangling_link_beside_a_save_destination_does_not_crash_the_rerun(check, tmp_path):
    (tmp_path / "latest.csv").symlink_to("out.csv")
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('out.csv')\n"
    assert provenance(check, tmp_path, body) is None


def test_artifact_resolving_outside_the_work_directory_is_refused_and_left_untouched(check, tmp_path):
    work, outside = tmp_path / "work", tmp_path / "outside"
    work.mkdir()
    outside.mkdir()
    (work / "data").symlink_to(outside)
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).get_df().to_csv('data/out.csv', index=False)\n"
    run_script(work, body)
    before = (outside / "out.csv").read_bytes()
    assert provenance(check, work, body, ["data/out.csv"], deliver=False) == "provenance: artifact data/out.csv resolves outside the work directory"
    assert (outside / "out.csv").read_bytes() == before


def linked_work(tmp_path, spelling):
    """A work dir whose `data` is an absolute link to its own `real` dir, spelled directly or through an alias of its parent."""
    work = tmp_path / "work"
    (work / "real").mkdir(parents=True)
    (tmp_path / "alias").symlink_to(tmp_path)
    (work / "data").symlink_to((work if spelling == "direct" else tmp_path / "alias" / "work") / "real")
    return work


GEN = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).get_df().to_csv('data/out.csv', index=False)\n"


@pytest.mark.parametrize("spelling", ["direct", "alias"])
def test_artifact_reached_through_an_absolute_link_inside_the_work_directory_passes(check, tmp_path, spelling):
    assert provenance(check, linked_work(tmp_path, spelling), GEN, ["data/out.csv"]) is None


@pytest.mark.parametrize("spelling", ["direct", "alias"])
def test_rerun_writing_through_an_absolute_link_inside_the_work_directory_leaves_the_original_untouched(check, tmp_path, spelling):
    work = linked_work(tmp_path, spelling)
    run_script(work, GEN)
    before = (work / "real" / "out.csv").read_bytes()
    assert provenance(check, work, GEN + "open('data/note.txt', 'w').write('x')\n", ["data/out.csv"], deliver=False) is None
    assert sorted(p.name for p in (work / "real").iterdir()) == ["out.csv"]
    assert (work / "real" / "out.csv").read_bytes() == before


def test_script_that_cannot_rerun_fails_as_provenance(check, tmp_path):
    body = "from rand_engine import DataGenerator\nimport sys\nprint('boom', file=sys.stderr)\nraise SystemExit(3)\n"
    assert provenance(check, tmp_path, body, []) == "provenance: the script exited 3 on re-run: boom"


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


def test_dangling_link_that_is_not_an_artifact_passes_provenance(check, tmp_path):
    (tmp_path / "stale.csv").symlink_to("missing.csv")
    assert provenance(check, tmp_path, SEEDED) is None


def test_self_loop_that_is_not_an_artifact_passes_provenance(check, tmp_path):
    (tmp_path / "loop").symlink_to("loop")
    assert provenance(check, tmp_path, SEEDED) is None


def test_two_directory_links_to_the_work_dir_pass_provenance(check, tmp_path, monkeypatch):
    real, copied = shutil.copytree, []

    def bounded(src, dst, *rest, **kw):
        if rest:
            return real(src, dst, *rest, **kw)
        def count(s, d, **k):
            copied.append(s)
            assert len(copied) < 100, "the copy follows directory links"
            return shutil.copy2(s, d, **k)
        return real(src, dst, copy_function=count, **kw)

    monkeypatch.setattr(shutil, "copytree", bounded)
    (tmp_path / "a").symlink_to(".")
    (tmp_path / "b").symlink_to(".")
    assert provenance(check, tmp_path, SEEDED) is None


def test_hand_written_sibling_of_a_save_destination_matches_no_generated_frame(check, tmp_path):
    body = ("import numpy as np, pandas as pd\nfrom rand_engine import DataGenerator\n"
            "pd.DataFrame({'age': np.arange(100, 110)}).to_csv('out.a', index=False)\n"
            f"DataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('out')\n")
    assert provenance(check, tmp_path, body, ["out.a"]) == "provenance: column 'age' of out.a matches no frame rand_engine generated"


def test_append_mode_save_passes(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('csv').mode('append').save('out.csv')\n"
    assert provenance(check, tmp_path, body) is None


def test_absent_artifact_message_is_pinned(check, tmp_path):
    assert provenance(check, tmp_path, SEEDED, deliver=False) == "provenance: artifact out.csv was not delivered"


def test_variable_outside_rerun_env_is_absent_from_the_rerun(check, tmp_path, monkeypatch):
    monkeypatch.setenv("EVAL_DUMMY_VAR", "dummy-value")
    body = SEEDED + "import os\nassert 'EVAL_DUMMY_VAR' not in os.environ, dict(os.environ)\n"
    run_script(tmp_path, body)
    assert provenance(check, tmp_path, body, deliver=False) is None


def test_symlink_in_the_workdir_is_copied_as_a_link(check, tmp_path):
    (tmp_path / "target.txt").write_text("t")
    (tmp_path / "link.txt").symlink_to("target.txt")
    assert provenance(check, tmp_path, SEEDED + "import os\nassert os.path.islink('link.txt')\n") is None


def test_copy_failure_reports_as_provenance(check, tmp_path):
    locked = tmp_path / "locked.txt"
    locked.write_text("x")
    locked.chmod(0)
    try:
        if os.access(locked, os.R_OK):
            pytest.skip("file permissions are not enforced here")
        msg = provenance(check, tmp_path, SEEDED)
    finally:
        locked.chmod(0o600)
    assert msg == "provenance: the copy of the work directory failed on locked.txt"


BOOL_SPEC = '{"flag": {"method": "booleans", "kwargs": {"true_prob": 0.5}}}'


def test_csv_bool_column_written_by_save_passes(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({BOOL_SPEC}, seed=1).size(10).write.format('csv').save('out.csv')\n"
    assert provenance(check, tmp_path, body) is None


def test_save_of_more_rows_than_one_batch_passes(check, tmp_path):
    body = (f"from rand_engine import DataGenerator\n"
            f"DataGenerator({SPEC}, seed=1).size(50).write.format('csv').option('maxRowsPerBatch', 20).save('out.csv')\n")
    assert provenance(check, tmp_path, body) is None


@pytest.mark.parametrize("message, line", [
    ("2 columns differ", "2: 2 columns differ"),
    ("provenance: no rand_engine import", "2: provenance: no rand_engine import"),
])
def test_failure_line_starts_with_its_layer_once(check, message, line):
    assert check.result_text("2", message).splitlines()[0] == line


def test_missing_script_fails_as_provenance(check, tmp_path):
    assert check.provenance(tmp_path, tmp_path / "gone.py", ["out.csv"], python=sys.executable)[0].startswith("provenance")


def test_script_without_a_rand_engine_import_fails_with_the_no_generation_line(check, tmp_path):
    msg = provenance(check, tmp_path, "import pandas as pd\npd.DataFrame({'age': [1]}).to_csv('out.csv', index=False)\n")
    assert msg == NO_AGENT_RECORD


def test_script_importing_rand_engine_without_generating_fails_with_the_no_generation_line(check, tmp_path):
    msg = provenance(check, tmp_path, "import rand_engine\nopen('out.csv', 'w').write('age\\n1\\n')\n")
    assert msg == NO_AGENT_RECORD


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
    msg, generations = rerun(check, tmp_path, body)
    assert msg is None
    assert check.documented_method(agent_specs(generations), "integers", {"min", "max"})
    assert not check.documented_method(agent_specs(generations), "floats", {"min", "max"})


def test_callable_spec_is_judged_by_its_evaluated_dict(check, tmp_path):
    body = (f"from rand_engine import DataGenerator\nDataGenerator(lambda: {SPEC}, seed=1).size(10).get_df()"
            ".to_csv('out.csv', index=False)\n")
    msg, generations = rerun(check, tmp_path, body)
    assert msg is None
    assert check.documented_method(agent_specs(generations), "integers", {"min", "max"})


def test_batch_save_records_the_spec(check, tmp_path):
    body = f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).write.format('csv').save('out.csv')\n"
    msg, generations = rerun(check, tmp_path, body)
    assert msg is None
    assert check.documented_method(agent_specs(generations), "integers", {"min", "max"})


def test_stream_start_records_the_spec(check, tmp_path):
    body = (f"from rand_engine import DataGenerator\nDataGenerator({SPEC}, seed=1).size(10).writeStream.format('csv')"
            ".trigger(frequency=0.1).option('timeout', 0.3).start('out')\n")
    _, generations = rerun(check, tmp_path, body, artifacts=("out",))
    assert check.documented_method(agent_specs(generations), "integers", {"min", "max"})


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


@pytest.mark.skipif(not hasattr(os, "fork"), reason="os.fork exists on POSIX only")
def test_forked_child_leaving_through_the_interpreter_does_not_overwrite_the_record(check, tmp_path):
    body = ("import os, sys, time\n"
            "if os.fork() == 0:\n    time.sleep(1)\n    sys.exit(0)\n" + SEEDED)
    assert provenance(check, tmp_path, body) is None
