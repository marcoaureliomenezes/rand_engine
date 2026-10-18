import ast
import importlib
import json
import os
import runpy
import subprocess
import sys
from importlib import resources
from pathlib import Path

try:
  import tomllib
except ModuleNotFoundError:
  import tomli as tomllib

import pytest

from rand_engine.cli import CASES

RUNNABLE_SLUGS = ["test-data", "lake", "kafka", "databricks", "faker"]
ALL_SLUGS = [*RUNNABLE_SLUGS, "agent"]
RESOURCES = {
  "test-data": "test-data.py.txt",
  "lake": "lake.py.txt",
  "kafka": "kafka.py.txt",
  "databricks": "databricks.py.txt",
  "faker": "faker.py.txt",
  "agent": "agent.md.txt",
}
TARGETS = {
  "test-data": "test-data-example.py",
  "lake": "lake-example.py",
  "kafka": "kafka-example.py",
  "databricks": "databricks-example.py",
  "faker": "faker-example.py",
  "agent": "AGENTS.md",
}
ROOT = Path(__file__).resolve().parent.parent


def run(argv):
  from rand_engine.cli import main
  try:
    code = main(argv)
  except SystemExit as e:
    code = e.code
  return code or 0


def case_bytes(slug):
  return (resources.files("rand_engine") / "cases" / CASES[slug].resource).read_bytes()


def test_case_descriptor_matches_the_literal_starter_contract():
  assert list(CASES) == ALL_SLUGS
  assert {slug: case.resource for slug, case in CASES.items()} == RESOURCES
  assert {slug: case.filename for slug, case in CASES.items()} == TARGETS
  assert [slug for slug, case in CASES.items() if case.kind == "runnable"] == RUNNABLE_SLUGS
  assert [slug for slug, case in CASES.items() if case.kind == "agent"] == ["agent"]


class NoStdin:
  def read(self, *a): raise AssertionError("stdin read")
  def readline(self, *a): raise AssertionError("stdin read")
  def readlines(self, *a): raise AssertionError("stdin read")
  def fileno(self): raise AssertionError("stdin read")
  def __iter__(self): raise AssertionError("stdin read")


def test_list_prints_six_slugs_in_order_with_descriptions(capsys):
  assert run(["list"]) == 0
  lines = capsys.readouterr().out.splitlines()
  assert len(lines) == 6
  assert lines[:5] == [
    "test-data  a DataFrame for pipeline tests with null_rate and anomaly_rate",
    "lake  pk/fk related tables written to a Parquet lake",
    "kafka  an event stream for Kafka: JSON lines to stdout by default, a producer block ready",
    "databricks  a Spark/Databricks notebook on native SparkGenerator",
    "faker  Faker pools sampled at NumPy speed through RandSpecs.faker_pool",
  ]
  for line, slug in zip(lines, ALL_SLUGS):
    assert line.startswith(slug)
    assert line[len(slug):].strip() != ""


def test_list_is_byte_identical_across_runs(capsys):
  run(["list"])
  first = capsys.readouterr().out
  run(["list"])
  assert capsys.readouterr().out == first != ""


@pytest.mark.parametrize("slug", RUNNABLE_SLUGS)
def test_get_started_writes_exact_file_and_creates_dir(slug, tmp_path, capsys):
  out = tmp_path / "new" / "deeper"
  assert run(["get-started", slug, "--out", str(out)]) == 0
  assert [p.name for p in out.iterdir()] == [f"{slug}-example.py"]
  assert (out / f"{slug}-example.py").read_bytes() == case_bytes(slug)
  assert str(out / f"{slug}-example.py") in capsys.readouterr().out


def test_get_started_agent_writes_only_agents_context_bytes(tmp_path, capsys):
  out = tmp_path / "project"
  target = out / "AGENTS.md"
  assert run(["get-started", "agent", "--out", str(out)]) == 0
  assert [path.name for path in out.iterdir()] == ["AGENTS.md"]
  assert target.read_bytes() == case_bytes("agent")
  assert capsys.readouterr().out == f"{target}\n"


def test_get_started_default_out_is_current_directory(tmp_path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  assert run(["get-started", "lake"]) == 0
  assert [p.name for p in tmp_path.iterdir()] == ["lake-example.py"]
  assert (tmp_path / "lake-example.py").read_bytes() == case_bytes("lake")


def test_get_started_twice_yields_identical_bytes(tmp_path):
  run(["get-started", "kafka", "--out", str(tmp_path / "a")])
  run(["get-started", "kafka", "--out", str(tmp_path / "b")])
  assert (tmp_path / "a" / "kafka-example.py").read_bytes() == (tmp_path / "b" / "kafka-example.py").read_bytes()


def check_test_data(ns, out, tmp_path):
  df = ns["df"]
  assert 0 < len(df) <= 10**4
  assert df.isna().sum().sum() > 0
  numeric = df.select_dtypes("number")
  spread = [(c.dropna() - c.dropna().median()).abs().max() / max(c.quantile(.75) - c.quantile(.25), 1e-9) for _, c in numeric.items()]
  assert max(spread) > 10


def check_lake(ns, out, tmp_path):
  import pandas as pd
  tables, relations = ns["tables"], ns["relations"]
  assert len(tables) >= 2 and relations
  frames = {}
  for name, path in tables.items():
    assert Path(path).resolve().is_relative_to(tmp_path.resolve())
    frames[name] = pd.read_parquet(path)
    assert 0 < len(frames[name]) <= 10**4
  for child, fk, parent, pk in relations:
    assert set(frames[child][fk]) <= set(frames[parent][pk])
    assert frames[child][fk].notna().all()


def check_kafka(ns, out, tmp_path):
  lines = [l for l in out.splitlines() if l.strip()]
  assert 0 < len(lines) <= 10**4
  assert all(isinstance(json.loads(l), dict) for l in lines)


def check_databricks(ns, out, tmp_path):
  assert 0 < ns["df"].count() <= 10**4


def check_faker(ns, out, tmp_path):
  assert 0 < len(ns["df"]) <= 10**4


CHECKS = {"test-data": check_test_data, "lake": check_lake, "kafka": check_kafka, "databricks": check_databricks, "faker": check_faker}


@pytest.mark.parametrize("slug", RUNNABLE_SLUGS)
def test_scaffold_is_databricks_source_and_runs_producing_its_promise(slug, tmp_path, monkeypatch, capsys, request):
  if slug == "databricks":
    request.getfixturevalue("spark_session")
  assert run(["get-started", slug, "--out", str(tmp_path)]) == 0
  capsys.readouterr()
  text = (tmp_path / f"{slug}-example.py").read_text(encoding="utf-8")
  assert text.splitlines()[0] == "# Databricks notebook source"
  assert "# COMMAND ----------" in text.splitlines()
  monkeypatch.chdir(tmp_path)
  monkeypatch.setitem(sys.modules, "kafka", None)
  monkeypatch.setitem(sys.modules, "confluent_kafka", None)
  ns = runpy.run_path(str(tmp_path / f"{slug}-example.py"), run_name="__main__")
  CHECKS[slug](ns, capsys.readouterr().out, tmp_path)


def test_test_data_scaffold_runs_under_plain_python(tmp_path):
  assert run(["get-started", "test-data", "--out", str(tmp_path)]) == 0
  env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(ROOT), os.environ.get("PYTHONPATH", "")]).rstrip(os.pathsep)}
  done = subprocess.run([sys.executable, str(tmp_path / "test-data-example.py")], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=120)
  assert done.returncode == 0, done.stderr


@pytest.mark.parametrize("tail", [["nope", "--out", "OUT"], []])
def test_bad_slug_or_missing_argument_exits_2_with_slugs_on_stderr(tail, tmp_path, capsys):
  argv = ["get-started"] + [str(tmp_path / "x") if a == "OUT" else a for a in tail]
  assert run(argv) == 2
  captured = capsys.readouterr()
  assert captured.out == ""
  for slug in ALL_SLUGS:
    assert slug in captured.err
  assert not (tmp_path / "x").exists()


def test_existing_target_is_left_unchanged_and_exit_1_names_it(tmp_path, capsys):
  target = tmp_path / "faker-example.py"
  target.write_bytes(b"mine\r\n")
  assert run(["get-started", "faker", "--out", str(tmp_path)]) == 1
  assert target.read_bytes() == b"mine\r\n"
  captured = capsys.readouterr()
  assert str(target) in captured.out + captured.err


def test_existing_agent_context_is_left_unchanged_with_no_stdout(tmp_path, capsys):
  target = tmp_path / "AGENTS.md"
  target.write_bytes(b"project rules\r\n")
  assert run(["get-started", "agent", "--out", str(tmp_path)]) == 1
  assert target.read_bytes() == b"project rules\r\n"
  captured = capsys.readouterr()
  assert captured.out == ""
  assert captured.err == f"error: {target} already exists, not overwriting\n"


@pytest.mark.parametrize("slug", ALL_SLUGS)
def test_get_started_preserves_target_created_at_write_boundary(slug, tmp_path, monkeypatch, capsys):
  target = tmp_path / TARGETS[slug]
  original_open = Path.open
  raced = False

  def open_with_competitor(path, mode="r", *args, **kwargs):
    nonlocal raced
    if path == target and mode in ("wb", "xb") and not raced:
      raced = True
      with original_open(target, "xb") as competitor:
        competitor.write(b"competitor")
    return original_open(path, mode, *args, **kwargs)

  monkeypatch.setattr(Path, "open", open_with_competitor)
  assert run(["get-started", slug, "--out", str(tmp_path)]) == 1
  assert target.read_bytes() == b"competitor"
  captured = capsys.readouterr()
  assert captured.out == ""
  assert captured.err == f"error: {target} already exists, not overwriting\n"


def test_cli_never_reads_stdin(tmp_path, monkeypatch):
  monkeypatch.setattr(sys, "stdin", NoStdin())
  assert run(["list"]) == 0
  assert run(["get-started", "lake", "--out", str(tmp_path)]) == 0
  assert run(["get-started", "lake", "--out", str(tmp_path)]) == 1
  assert run(["get-started", "agent", "--out", str(tmp_path)]) == 0
  assert run(["get-started", "nope"]) == 2


def test_top_level_help_describes_commands_and_lists_slugs(capsys):
  assert run(["--help"]) == 0
  out = capsys.readouterr().out
  assert "list" in out and "get-started" in out
  for slug in ALL_SLUGS:
    assert slug in out


def test_get_started_help_describes_every_argument_and_lists_slugs(capsys):
  assert run(["get-started", "--help"]) == 0
  out = capsys.readouterr().out
  assert "--out" in out and "slug" in out.lower()
  for slug in ALL_SLUGS:
    assert slug in out


def test_python_dash_m_runs_main(monkeypatch, capsys):
  run(["list"])
  expected = capsys.readouterr().out
  monkeypatch.setattr(sys, "argv", ["rand_engine", "list"])
  with pytest.raises(SystemExit) as e:
    runpy.run_module("rand_engine", run_name="__main__")
  assert (e.value.code or 0) == 0
  assert capsys.readouterr().out == expected != ""


def test_python_dash_m_writes_agent_context(tmp_path, monkeypatch, capsys):
  target = tmp_path / "AGENTS.md"
  monkeypatch.setattr(sys, "argv", ["rand_engine", "get-started", "agent", "--out", str(tmp_path)])
  with pytest.raises(SystemExit) as exit_code:
    runpy.run_module("rand_engine", run_name="__main__")
  assert (exit_code.value.code or 0) == 0
  assert target.read_bytes() == case_bytes("agent")
  assert capsys.readouterr().out == f"{target}\n"


def test_cli_imports_only_stdlib_and_rand_engine():
  module = importlib.import_module("rand_engine.cli")
  tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
  roots = set()
  for node in ast.walk(tree):
    if isinstance(node, ast.Import):
      roots |= {a.name.split(".")[0] for a in node.names}
    elif isinstance(node, ast.ImportFrom) and node.level == 0:
      roots.add(node.module.split(".")[0])
  assert roots - set(sys.stdlib_module_names) <= {"rand_engine"}


def test_pyproject_declares_open_python_and_the_four_dependencies():
  pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
  data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
  assert data.get("project", {}).get("requires-python") == ">=3.10"
  assert data["tool"]["poetry"]["dependencies"] == {
    "numpy": "^2.1.1",
    "pandas": "^2.2.2",
    "pyarrow": "^23.0.1",
    "faker": {"version": ">=28.4.1,<29.0.0", "optional": True},
  }
