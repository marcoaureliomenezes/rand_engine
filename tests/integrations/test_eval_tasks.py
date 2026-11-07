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
