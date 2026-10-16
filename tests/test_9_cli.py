import ast
import importlib
import runpy
import sys
import tomllib
from importlib import resources
from pathlib import Path

import pytest

SLUGS = ["test-data", "lake", "kafka", "databricks", "faker"]


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


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize("slug", SLUGS)
def test_get_started_writes_exact_file_and_creates_dir(slug, tmp_path, capsys):
  out = tmp_path / "new" / "deeper"
  assert run(["get-started", slug, "--out", str(out)]) == 0
  assert [p.name for p in out.iterdir()] == [f"{slug}.py"]
  assert (out / f"{slug}.py").read_bytes() == case_bytes(slug)
  assert str(out / f"{slug}.py") in capsys.readouterr().out


@pytest.mark.xfail(strict=True)
def test_get_started_default_out_is_current_directory(tmp_path, monkeypatch):
  monkeypatch.chdir(tmp_path)
  assert run(["get-started", "lake"]) == 0
  assert [p.name for p in tmp_path.iterdir()] == ["lake.py"]
  assert (tmp_path / "lake.py").read_bytes() == case_bytes("lake")


@pytest.mark.xfail(strict=True)
def test_get_started_twice_yields_identical_bytes(tmp_path):
  run(["get-started", "kafka", "--out", str(tmp_path / "a")])
  run(["get-started", "kafka", "--out", str(tmp_path / "b")])
  assert (tmp_path / "a" / "kafka.py").read_bytes() == (tmp_path / "b" / "kafka.py").read_bytes()


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
  target = tmp_path / "faker.py"
  target.write_bytes(b"mine\r\n")
  assert run(["get-started", "faker", "--out", str(tmp_path)]) == 1
  assert target.read_bytes() == b"mine\r\n"
  captured = capsys.readouterr()
  assert str(target) in captured.out + captured.err


@pytest.mark.xfail(strict=True)
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
