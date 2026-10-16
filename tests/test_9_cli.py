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

SLUGS = ["test-data", "lake", "kafka", "databricks", "faker"]
OWNER = {"test-data": "J6.T4", "lake": "J6.T5", "kafka": "J6.T6", "databricks": "J6.T7", "faker": "J6.T8"}
SEAM = {
  "test-data": "module-level `df`: a pandas DataFrame with nulls and anomalous values",
  "lake": "module-level `tables` {name: Path of its Parquet} and `relations` [(child, fk_col, parent, pk_col)]",
  "kafka": "JSON lines on stdout, nothing else; no `kafka` import at module level",
  "databricks": "module-level `df`: a Spark DataFrame of 1..10^4 rows",
  "faker": "module-level `df`: a non-empty pandas DataFrame",
}
ROOT = Path(__file__).resolve().parent.parent


def owned(slug, what):
  reason = f"{OWNER[slug]} adds rand_engine/cases/{slug}.py.txt; {what}"
  return pytest.param(slug, marks=pytest.mark.xfail(strict=True, reason=reason), id=slug)


def run(argv):
  from rand_engine.cli import main
  try:
    code = main(argv)
  except SystemExit as e:
    code = e.code
  return code or 0


def case_bytes(slug):
  return (resources.files("rand_engine") / "cases" / f"{slug}.py.txt").read_bytes()


class NoStdin:
  def read(self, *a): raise AssertionError("stdin read")
  def readline(self, *a): raise AssertionError("stdin read")
  def readlines(self, *a): raise AssertionError("stdin read")
  def fileno(self): raise AssertionError("stdin read")
  def __iter__(self): raise AssertionError("stdin read")


def test_list_prints_five_slugs_in_order_with_descriptions(capsys):
  assert run(["list"]) == 0
  lines = capsys.readouterr().out.splitlines()
  assert len(lines) == 5
  for line, slug in zip(lines, SLUGS):
    assert line.startswith(slug)
    assert line[len(slug):].strip() != ""


def test_list_is_byte_identical_across_runs(capsys):
  run(["list"])
  first = capsys.readouterr().out
  run(["list"])
  assert capsys.readouterr().out == first != ""


@pytest.mark.parametrize("slug", [s if s in ("test-data", "lake", "kafka", "databricks", "faker") else owned(s, "file bytes") for s in SLUGS])
def test_get_started_writes_exact_file_and_creates_dir(slug, tmp_path, capsys):
  out = tmp_path / "new" / "deeper"
  assert run(["get-started", slug, "--out", str(out)]) == 0
  assert [p.name for p in out.iterdir()] == [f"{slug}-example.py"]
  assert (out / f"{slug}-example.py").read_bytes() == case_bytes(slug)
  assert str(out / f"{slug}-example.py") in capsys.readouterr().out


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


@pytest.mark.parametrize("slug", [s if s in ("test-data", "lake", "kafka", "databricks", "faker") else owned(s, "the written file runs and leaves: " + SEAM[s]) for s in SLUGS])
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
  for slug in SLUGS:
    assert slug in captured.err
  assert not (tmp_path / "x").exists()


def test_existing_target_is_left_unchanged_and_exit_1_names_it(tmp_path, capsys):
  target = tmp_path / "faker-example.py"
  target.write_bytes(b"mine\r\n")
  assert run(["get-started", "faker", "--out", str(tmp_path)]) == 1
  assert target.read_bytes() == b"mine\r\n"
  captured = capsys.readouterr()
  assert str(target) in captured.out + captured.err


def test_cli_never_reads_stdin(tmp_path, monkeypatch):
  monkeypatch.setattr(sys, "stdin", NoStdin())
  assert run(["list"]) == 0
  assert run(["get-started", "lake", "--out", str(tmp_path)]) == 0
  assert run(["get-started", "lake", "--out", str(tmp_path)]) == 1
  assert run(["get-started", "nope"]) == 2


def test_top_level_help_describes_commands_and_lists_slugs(capsys):
  assert run(["--help"]) == 0
  out = capsys.readouterr().out
  assert "list" in out and "get-started" in out
  for slug in SLUGS:
    assert slug in out


def test_get_started_help_describes_every_argument_and_lists_slugs(capsys):
  assert run(["get-started", "--help"]) == 0
  out = capsys.readouterr().out
  assert "--out" in out and "slug" in out.lower()
  for slug in SLUGS:
    assert slug in out


def test_python_dash_m_runs_main(monkeypatch, capsys):
  run(["list"])
  expected = capsys.readouterr().out
  monkeypatch.setattr(sys, "argv", ["rand_engine", "list"])
  with pytest.raises(SystemExit) as e:
    runpy.run_module("rand_engine", run_name="__main__")
  assert (e.value.code or 0) == 0
  assert capsys.readouterr().out == expected != ""


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
  pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
  deps = tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"]["poetry"]["dependencies"]
  assert deps == {
    "python": "^3.10",
    "numpy": "^2.1.1",
    "pandas": "^2.2.2",
    "pyarrow": "^23.0.1",
    "faker": {"version": ">=28.4.1,<29.0.0", "optional": True},
  }
