"""Eval coverage guard: the usage task folders under evals/tasks equal the catalog's non-quality slugs."""
import ast
import json
import re
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
])
def test_get_started_matcher_refuses_other_commands(matcher, command):
    assert matcher(command) is False, command


def test_get_started_check_without_a_transcript_fails_layer_2(tmp_path):
    import os
    import shutil
    import subprocess
    import sys

    (tmp_path / "starter").mkdir()
    shutil.copy(ROOT / "rand_engine/cases/lake.py.txt", tmp_path / "starter/lake-example.py")
    env = {k: v for k, v in os.environ.items() if k != "RAND_EVAL_TRANSCRIPT"}
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(ROOT / "evals")])
    run = subprocess.run([sys.executable, str(GET_STARTED_CHECK)], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert run.returncode == 1, run.stdout + run.stderr
    assert '"layer": "2"' in run.stdout or "'layer': '2'" in run.stdout, run.stdout
