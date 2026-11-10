"""Eval task contract: the usage task folders under evals/tasks equal the catalog's non-quality slugs, and the task checks' behaviour pinned here
(the pk-fk parent comparison, reads of agent-written files, the get-started-cli command matcher and its layer 2)."""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
USAGE_SLUGS = {
    "data-generator", "documentation", "generation-methods", "get-started-cli", "pk-fk-constraints",
    "public-api", "rand-spec-grammar", "spark-generator", "templates-and-examples", "writers-and-streaming",
}


def catalog_usage_slugs():
    features = json.loads((ROOT / "specs/memory/product/catalog.json").read_text(encoding="utf-8"))["features"]
    return {f["slug"] for f in features if f["area"] != "quality"}


def usage_folders():
    return {
        p.parent.name for p in (ROOT / "evals/tasks").glob("*/task.toml")
        if tomllib.loads(p.read_text(encoding="utf-8"))["task"]["round"] == "usage"
    }


def test_catalog_non_quality_slugs_are_the_ten_usage_slugs():
    assert catalog_usage_slugs() == USAGE_SLUGS


def test_usage_task_folders_cover_the_catalog():
    found = usage_folders()
    expected = catalog_usage_slugs()
    assert found == expected, f"missing: {sorted(expected - found)}, extra: {sorted(found - expected)}"


CHECKS = sorted(USAGE_SLUGS)
PASS_LINE = re.compile(r"""RESULT.*layer['"]: ['"]pass['"].*surfaces|RESULT.*surfaces.*layer['"]: ['"]pass['"]""")


def check_source(slug):
    return (ROOT / "evals/tasks" / slug / "tests/check.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("slug", CHECKS)
def test_usage_check_prints_one_pass_line_with_layer_and_surfaces(slug):
    lines = check_source(slug).splitlines()
    assert sum(bool(PASS_LINE.search(line)) for line in lines) == 1, f"{slug}: not one RESULT pass line with layer and surfaces"
    assert not [line for line in lines if re.search(r"""print\(f?['"]PASS""", line)], f"{slug}: prints a bare PASS line"


@pytest.mark.parametrize("slug", CHECKS)
def test_usage_check_fails_through_fail_layer_message(slug):
    fails = [n for n in ast.walk(ast.parse(check_source(slug))) if isinstance(n, ast.FunctionDef) and n.name == "fail"]
    assert [[a.arg for a in n.args.args] + [bool(n.args.defaults)] for n in fails] in ([], [["layer", "message", False]]), f"{slug}: fail is not fail(layer, message)"


def test_spark_generator_requires_pyspark_4_and_no_setuptools():
    requirements = tomllib.loads((ROOT / "evals/tasks/spark-generator/task.toml").read_text(encoding="utf-8"))["environment"]["requirements"]
    assert requirements == ["pyspark>=4"]


def test_spark_generator_check_imports_no_pandas():
    imported = {a.name.split(".")[0] for n in ast.walk(ast.parse(check_source("spark-generator"))) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(ast.parse(check_source("spark-generator"))) if isinstance(n, ast.ImportFrom)}
    assert "pandas" not in imported


PK_FK = ROOT / "evals/tasks/pk-fk-constraints"
CUSTOMER_PK = '{"method": "pk", "kwargs": {"start": 1}}'


def run_pk_fk_check(tmp_path, parent):
    reference = (PK_FK / "tests/solution/solve.py").read_text(encoding="utf-8")
    solve = reference.replace("customer_pk = " + CUSTOMER_PK, f"customer_pk = {CUSTOMER_PK}\nfk_parent = {parent}").replace('"parent": customer_pk', '"parent": fk_parent')
    assert solve.count("fk_parent") == 2 and solve != reference, "the reference solve no longer holds the text the parent swap replaces"
    (tmp_path / "solve.py").write_text(solve, encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k != "RAND_EVAL_TRANSCRIPT"}
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "evals")])
    subprocess.run([sys.executable, "solve.py"], cwd=tmp_path, env=env, check=True)
    return subprocess.run([sys.executable, str(PK_FK / "tests/check.py")], cwd=tmp_path, env=env, capture_output=True, text=True)


@pytest.mark.parametrize("parent", [
    CUSTOMER_PK,
    '{"method": "pk", "kwargs": {"step": 1, "start": 1}}',
    '{"method": "pk", "kwargs": {"start": 1, "style": "sequence", "step": 1}}',
])
def test_pk_fk_check_accepts_a_parent_equal_to_the_pk_after_its_defaults(tmp_path, parent):
    run = run_pk_fk_check(tmp_path, parent)
    assert run.returncode == 0 and '"layer": "pass"' in run.stdout, run.stdout + run.stderr


def test_pk_fk_check_refuses_a_parent_that_is_another_pk(tmp_path):
    run = run_pk_fk_check(tmp_path, '{"method": "pk", "kwargs": {"start": 1, "style": "permuted", "domain": 1000, "key": 7}}')
    assert run.returncode == 1 and '"layer": "3"' in run.stdout and '"layer": "pass"' not in run.stdout, run.stdout + run.stderr


def run_check(cwd, *paths):
    env = {k: v for k, v in os.environ.items() if k != "RAND_EVAL_TRANSCRIPT"}
    env["PYTHONPATH"] = os.pathsep.join([*map(str, paths), str(ROOT), str(ROOT / "evals")])
    return env, lambda script: subprocess.run([sys.executable, script], cwd=cwd, env=env, capture_output=True, text=True)


def reference_trial(slug, tmp_path):
    """The directory a correct agent leaves for `slug`; returns a runner of the task's check in it."""
    env, run = run_check(tmp_path)
    if slug == "canary":
        commands = ["python -c 'import rand_engine' > import.txt", "pip --version > pip.txt", "python urlopen > network.txt"]
        events = [{"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": c}}]}} for c in commands]
        (tmp_path / "transcript.jsonl").write_text("\n".join(map(json.dumps, events)), encoding="utf-8")
        env["RAND_EVAL_TRANSCRIPT"] = str(tmp_path / "transcript.jsonl")
        for name, text in {"import": "exit=0\n", "pip": "exit=0\n", "network": "NET_FAIL\nexit=1\n"}.items():
            (tmp_path / f"{name}.txt").write_text(text, encoding="utf-8")
    else:
        shutil.copy(ROOT / "evals/tasks" / slug / "tests/solution/solve.py", tmp_path / "solve.py")
        subprocess.run([sys.executable, "solve.py"], cwd=tmp_path, env=env, check=True)
    return lambda: subprocess.run([sys.executable, str(ROOT / "evals/tasks" / slug / "tests/check.py")], cwd=tmp_path, env=env, capture_output=True, text=True)


def taint(path):
    if path.name == "solve.py":
        path.write_bytes(b"# coding: latin-1\n" + path.read_bytes() + b"\n# \xff\n")
    else:
        path.write_bytes((path.read_bytes() if path.exists() else b"") + b"\xff")


@pytest.mark.parametrize("slug, written", [
    ("documentation", "answer.txt"), ("canary", "import.txt"), ("data-generator", "extra.py"),
    ("generation-methods", "extra.py"), ("pk-fk-constraints", "extra.py"), ("templates-and-examples", "extra.py"),
    ("public-api", "version.txt"), ("public-api", "solve.py"), ("public-api", "extra.py"),
])
def test_agent_written_reads_survive_an_undecodable_byte(tmp_path, slug, written):
    check = reference_trial(slug, tmp_path)
    taint(tmp_path / written)
    run = check()
    assert "UnicodeDecodeError" not in run.stderr and run.returncode == 0 and ("probe:network" if slug == "canary" else '"layer": "pass"') in run.stdout, run.stdout + run.stderr


def test_harness_written_llms_read_stays_strict(tmp_path):
    stub = tmp_path / "stub/rand_engine"
    stub.mkdir(parents=True)
    (stub / "__init__.py").write_text("", encoding="utf-8")
    (stub / "llms.txt").write_bytes(b"[page](https://x/WRITING_FILES): writeStream \xff\n")
    (tmp_path / "answer.txt").write_text("https://x/WRITING_FILES\n", encoding="utf-8")
    env, run = run_check(tmp_path, tmp_path / "stub")
    result = run(str(ROOT / "evals/tasks/documentation/tests/check.py"))
    assert result.returncode == 1 and "UnicodeDecodeError" in result.stderr, result.stdout + result.stderr


GET_STARTED_CHECK = ROOT / "evals/tasks/get-started-cli/tests/check.py"


@pytest.fixture
def matcher(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(ROOT / "evals"))
    monkeypatch.chdir(tmp_path)
    namespace = {"__file__": str(GET_STARTED_CHECK)}
    try:
        exec(compile(GET_STARTED_CHECK.read_text(encoding="utf-8"), str(GET_STARTED_CHECK), "exec"), namespace)
    except SystemExit:
        pass
    return namespace["ran_get_started_lake"]


PYTHON_C = '"import sys; from rand_engine.cli import main; sys.exit(main())"'


@pytest.mark.parametrize("command", [
    "rand-engine get-started lake",
    ".venv/bin/rand-engine get-started lake --out starter",
    "rand-engine get-started --out starter lake",
    "uvx rand-engine get-started lake",
    "uv run rand-engine get-started lake",
    "poetry run rand-engine get-started lake",
    "pipx run rand-engine get-started lake",
    "timeout 30 rand-engine get-started lake",
    "python -m rand_engine get-started lake",
    f"python -c {PYTHON_C} get-started lake --out starter",
    "cd /tmp && rand-engine get-started lake",
    "rand-engine get-started lake; ls starter",
    "rand-engine get-started lake&&ls",
    "rand-engine get-started lake|tail -1",
    "cd x;rand-engine get-started lake",
    "rand-engine get-started --help && rand-engine get-started lake",
    "rand-engine get-started lake\ncat <<'EOF'\nit's the starter\nEOF",
    'python -c "from rand_engine import cli; cli.main()" get-started lake',
])
def test_get_started_matcher_accepts_the_package_cli_forms(matcher, command):
    assert matcher(command) is True, command


@pytest.mark.parametrize("command", [
    "rand-engine get-started other lake",
    'rand-engine get-started "a b" lake',
    'rand-engine get-started "lake x"',
    "rand-engine lake",
    "my-rand-engine get-started lake",
    f"python -c {PYTHON_C} lake",
    'python -c "print(1)" get-started lake',
    "cat lake.py.txt",
    'python -c "import rand_engine.cli" get-started lake',
])
def test_get_started_matcher_refuses_other_commands(matcher, command):
    assert matcher(command) is False, command


def test_get_started_check_without_a_transcript_fails_layer_2(tmp_path):
    (tmp_path / "starter").mkdir()
    shutil.copy(ROOT / "rand_engine/cases/lake.py.txt", tmp_path / "starter/lake-example.py")
    env = {k: v for k, v in os.environ.items() if k != "RAND_EVAL_TRANSCRIPT"}
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "evals")])
    run = subprocess.run([sys.executable, str(GET_STARTED_CHECK)], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert run.returncode == 1, run.stdout + run.stderr
    assert '"layer": "2"' in run.stdout, run.stdout
