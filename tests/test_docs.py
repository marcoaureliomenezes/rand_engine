import ast
import doctest
import importlib
import io
import inspect
import json
import re
import tempfile
import textwrap
import warnings
from pathlib import Path

try:
  import tomllib
except ModuleNotFoundError:
  import tomli as tomllib

import pytest

from rand_engine.cli import CASES

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
REPO_BLOB = "https://github.com/marcoaureliomenezes/rand_engine/blob/"
GITFLOW = re.search(r"^gitflow: (.*)$", (ROOT / "specs" / "constitution.md").read_text(encoding="utf-8"), re.M)
PRINCIPAL = json.loads(GITFLOW.group(1))["principal"]
LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```((?:python|py)[^\n]*)\n(.*?)^```", re.M | re.S)


def python_blocks(path: Path) -> list[tuple[str, str]]:
  return [(info.strip(), body) for info, body in FENCE.findall(path.read_text(encoding="utf-8"))]


SKILL = ROOT / "skills" / "rand-engine" / "SKILL.md"


@pytest.mark.parametrize("doc", [*(pytest.param(p, id=p.relative_to(DOCS).as_posix()) for p in sorted(DOCS.glob("**/*.md"))),
                                 pytest.param(SKILL, id="SKILL.md")])
def test_doc_python_blocks_execute_in_order(doc, tmp_path, monkeypatch, request):
  """Every `python` block runs, in file order, in one namespace."""
  blocks = [body for info, body in python_blocks(doc) if info == "python"]
  if any("pyspark" in body for body in blocks):
    request.getfixturevalue("spark_session")  # the doc's getOrCreate() reuses it; skips where Spark cannot run
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__docs__"}
  for i, body in enumerate(blocks):
    exec(compile(body, f"{doc.name}[{i}]", "exec"), namespace)


def test_no_run_is_only_the_kafka_producer():
  """`python no-run` only for a client outside the test dependencies (a Kafka producer)."""
  infos = {info for doc in DOCS.glob("*.md") for info, _ in python_blocks(doc)}
  assert infos <= {"python", "python no-run"}
  no_run = {(doc.name, body) for doc in DOCS.glob("*.md") for info, body in python_blocks(doc) if info == "python no-run"}
  assert {name for name, _ in no_run} == {"5_RECIPES.md"}
  assert all("from kafka import" in body for _, body in no_run)
  skill = python_blocks(SKILL)
  assert {info for info, _ in skill} <= {"python", "python no-run"}
  assert all("from pyspark" in body for info, body in skill if info == "python no-run")


def skill_method_table() -> dict[str, str]:
  """Method name -> the Spark column's text, for every row of SKILL.md's method table."""
  rows = re.findall(r"^\| Method \|.*\n\|[-| ]+\n((?:\|.*\n)+)", SKILL.read_text(encoding="utf-8"), re.M)[0].splitlines()
  cells = [[c.strip() for c in row.strip("|").split("|")] for row in rows]
  return {name: cell[-1] for cell in cells for name in re.findall(r"`(\w+)`", cell[0])}


def spark_outcome(spec) -> str:
  """How Spark validation treats a spec, in the table's vocabulary."""
  from rand_engine.validators.common_validator import CommonValidator
  from rand_engine.validators.exceptions import SpecValidationError
  with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    try:
      CommonValidator.validate_spark_and_raise({"c": dict(spec)})
    except SpecValidationError:
      return "refused"
  return "NULL + warning" if caught else "yes"


def test_skill_method_table_lists_every_method():
  """SKILL.md's method table names exactly the methods of METHOD_CATALOG."""
  from rand_engine.validators.method_specs import METHOD_CATALOG
  assert set(skill_method_table()) == set(METHOD_CATALOG)


def test_skill_method_table_spark_column_is_what_validation_does():
  """Each row's Spark cell (yes / refused / NULL + warning) is the outcome of Spark validation of that method's catalog example."""
  from rand_engine.validators.method_specs import METHOD_CATALOG
  claimed = skill_method_table()
  assert set(claimed.values()) <= {"yes", "refused", "NULL + warning"}
  actual = {name: spark_outcome(spec.example) for name, spec in METHOD_CATALOG.items()}
  assert {m: (claimed[m], actual[m]) for m in actual if claimed[m] != actual[m]} == {}

INCLUDE = re.compile(r'--8<-- "(rand_engine/cases/[a-z-]+\.py\.txt)"')


def _include_of(body: str):
  match = INCLUDE.fullmatch(body.strip())
  return match.group(1) if match else None


@pytest.mark.parametrize("slug", CASES)
def test_tutorial_includes_its_case_file(slug):
  """Each tutorial holds one `python no-run` fence whose body is the snippet include of its own case file, which exists."""
  blocks = python_blocks(DOCS / "tutorials" / f"{slug}.md")
  assert [(info, _include_of(body)) for info, body in blocks if info == "python no-run"] == [
    ("python no-run", f"rand_engine/cases/{slug}.py.txt")]
  assert (ROOT / f"rand_engine/cases/{slug}.py.txt").is_file()


def test_tutorial_no_run_fences_are_only_case_includes():
  """A `no-run` fence under docs/tutorials/ is exactly one snippet-include line of an existing case file."""
  bodies = [body for doc in DOCS.glob("tutorials/*.md") for info, body in python_blocks(doc) if info == "python no-run"]
  assert [b for b in bodies if _include_of(b) is None or not (ROOT / _include_of(b)).is_file()] == []


def test_readme_python_blocks_execute_in_order(tmp_path, monkeypatch):
  """Every README `python` block runs, in order, in one namespace; only {python, python no-run} fences."""
  blocks = python_blocks(ROOT / "README.md")
  assert {info for info, _ in blocks} <= {"python", "python no-run"}
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__readme__"}
  for i, (info, body) in enumerate(blocks):
    if info == "python":
      exec(compile(body, f"README.md[{i}]", "exec"), namespace)


@pytest.mark.parametrize("name", ["README.md", "llms.txt"])
def test_links_resolve(name):
  """No relative link (PyPI breaks them); a link into this repo targets the principal branch and a file that exists."""
  links = LINK.findall((ROOT / name).read_text(encoding="utf-8"))
  assert links
  assert [u for u in links if not u.startswith("https://")] == []
  repo = [u[len(REPO_BLOB):].split("#")[0].split("/", 1) for u in links if u.startswith(REPO_BLOB)]
  assert [b for b, _ in repo if b != PRINCIPAL] == []
  assert [p for _, p in repo if not (ROOT / p).is_file()] == []


NEW_METHODS = {"exponential", "lognormal", "poisson", "zipf", "constant"}
MODIFIERS = {"null_rate", "anomaly_rate", "anomaly_values"}


def block_text(name: str) -> str:
  return "\n".join(body for info, body in python_blocks(DOCS / name) if info == "python")


def documented_specs(name, tmp_path, monkeypatch):
  """Run a doc's python blocks and return every (spec, refused) a generator was constructed with."""
  from rand_engine import DataGenerator
  from rand_engine.validators.exceptions import SpecValidationError
  seen = []
  init = DataGenerator.__init__

  def record(self, spec, *args, **kwargs):
    resolved = spec() if callable(spec) else spec
    try:
      init(self, spec, *args, **kwargs)
    except SpecValidationError:
      seen.append((resolved, True))
      raise
    seen.append((resolved, False))

  monkeypatch.setattr(DataGenerator, "__init__", record)
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__docs__"}
  for i, body in enumerate(b for info, b in python_blocks(DOCS / name) if info == "python"):
    exec(compile(body, f"{name}[{i}]", "exec"), namespace)
  return seen


def test_skill_front_matter_names_the_skill_and_says_when_to_use_it():
  """SKILL.md opens with `---` front matter holding `name: rand-engine` and a description naming its triggers."""
  head = re.match(r"---\n(.*?)\n---\n", SKILL.read_text(encoding="utf-8"), re.S)
  fields = dict(re.findall(r"^(\w+):\s*(.+)$", head.group(1), re.M))
  assert fields["name"] == "rand-engine"
  assert "synthetic data" in fields["description"] and "RandSpec" in fields["description"]


def test_skill_blocks_build_relations_and_write_through_a_sink(tmp_path, monkeypatch):
  """The skill's executed blocks construct accepted specs, one with pk and one with fk, and leave a file written by a sink."""
  seen = documented_specs(SKILL, tmp_path, monkeypatch)
  methods = {c["method"] for spec, raised in seen if not raised for c in spec.values()}
  assert {"pk", "fk"} <= methods
  assert [p for p in tmp_path.rglob("*") if p.is_file()] != []


def test_data_generator_doc_runs_every_new_method_and_modifier(tmp_path, monkeypatch):
  """1_DATA_GENERATOR.md builds a generator with each 0.7.0 method and modifier (blocks run at light sizes)."""
  columns = [c for spec, _ in documented_specs("1_DATA_GENERATOR.md", tmp_path, monkeypatch) for c in spec.values()]
  assert NEW_METHODS - {c["method"] for c in columns} == set()
  assert MODIFIERS - {key for c in columns for key in c} == set()


def test_data_generator_doc_shows_modifier_and_negative_decimals_refusals(tmp_path, monkeypatch):
  """The guide's executed blocks refuse a modifier on pk and on a multi-column map, and negative decimals on exponential or lognormal."""
  refused = [c for spec, raised in documented_specs("1_DATA_GENERATOR.md", tmp_path, monkeypatch) if raised for c in spec.values()]
  modified = {c["method"] for c in refused if "null_rate" in c or "anomaly_rate" in c}
  assert "pk" in modified and modified & {"distincts_map", "distincts_map_prop", "distincts_multi_map"}
  assert {c["method"] for c in refused if c.get("kwargs", {}).get("decimals", 0) < 0} & {"exponential", "lognormal"}


def test_spark_doc_runs_the_refusal_of_new_methods():
  """2_SPARK_GENERATOR.md shows (in an executed block) SparkGenerator refusing a 0.7.0 method and pointing at DataGenerator."""
  code = block_text("2_SPARK_GENERATOR.md")
  assert "SpecValidationError" in code and "DataGenerator" in code
  assert any(method in code for method in NEW_METHODS - {"constant"})


def test_writing_doc_runs_row_batches_and_append():
  """3_WRITING_FILES.md executes maxRowsPerBatch and mode("append") (new parts beside the old ones)."""
  code = block_text("3_WRITING_FILES.md")
  assert "maxRowsPerBatch" in code and 'mode("append")' in code


def test_recipes_run_the_helpers():
  """5_RECIPES.md builds specs with RandSpecs.faker_pool and RandSpecs.from_schema."""
  code = block_text("5_RECIPES.md")
  assert "faker_pool(" in code and "from_schema(" in code


@pytest.mark.parametrize("token", ["exponential", "lognormal", "poisson", "zipf", "constant", "null_rate", "anomaly_rate",
                                   "maxRowsPerBatch", "splitable", "faker_pool", "from_schema"])
def test_changelog_0_7_0_lists_the_new_surface_and_migration(token):
  """the 0.7.0 section names each addition and the legacy key migration."""
  text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
  section = text.split("## [0.7.0]", 1)[1].split("\n## [", 1)[0]
  assert token in section


def _public(cls, names):
  return [(n, m) for n, m in inspect.getmembers(cls)
          if (n in names if names else not n.startswith("_")) and (callable(m) or isinstance(m, property))]


def _returns_value(func) -> bool:
  func = func.fget if isinstance(func, property) else func
  tree = ast.parse(textwrap.dedent(inspect.getsource(func))).body[0]
  stack = list(tree.body)
  while stack:
    node = stack.pop()
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
      continue
    if isinstance(node, (ast.Yield, ast.YieldFrom)) or (isinstance(node, ast.Return) and node.value is not None):
      return True
    stack.extend(ast.iter_child_nodes(node))
  return False


def _gaps(cls, names=None) -> list[str]:
  cls_doc = inspect.getdoc(cls) or ""
  gaps = [] if cls_doc.strip() else [f"{cls.__name__}: no summary"]
  if not re.search(r"^Examples\n-{3,}$", cls_doc, re.M):
    gaps.append(f"{cls.__name__}: no Examples section")
  for name, func in _public(cls, names):
    who, doc = f"{cls.__name__}.{name}", inspect.getdoc(func) or ""
    has = lambda section: re.search(rf"^{section}\n-{{3,}}$", doc, re.M)
    prop = isinstance(func, property)
    if not doc.strip():
      gaps.append(f"{who}: no summary")
    if not prop and not has("Examples"):
      gaps.append(f"{who}: no Examples section")
    if not prop and [p for p in inspect.signature(func).parameters if p not in ("self", "cls")] and not has("Parameters"):
      gaps.append(f"{who}: no Parameters section")
    if _returns_value(func) and not (has("Returns") or has("Yields")):
      gaps.append(f"{who}: no Returns section")
  return gaps


def _surface():
  from rand_engine import DataGenerator, RandSpecs, SparkGenerator
  from rand_engine.file_handlers._writer_batch import FileBatchWriter
  from rand_engine.file_handlers._writer_stream import FileStreamWriter
  from rand_engine.file_handlers.writer import FileWriter
  return {
    "DataGenerator": (DataGenerator, None),
    "SparkGenerator": (SparkGenerator, None),
    "FileWriter": (FileWriter, {"mode", "format", "option", "options"}),
    "FileBatchWriter": (FileBatchWriter, {"save"}),
    "FileStreamWriter": (FileStreamWriter, {"trigger", "start"}),
    "RandSpecs": (RandSpecs, None),
  }


@pytest.mark.parametrize("name", ["DataGenerator", "SparkGenerator", "FileWriter", "FileBatchWriter", "FileStreamWriter", "RandSpecs"])
def test_public_callables_carry_numpydoc(name):
  """Every public class, callable and property has a summary; callables and classes an Examples section; Parameters/Returns as they apply."""
  cls, names = _surface()[name]
  assert _gaps(cls, names) == []


@pytest.mark.parametrize("module", [
  "rand_engine.main.data_generator",
  "rand_engine.main.spark_generator",
  "rand_engine.file_handlers.writer",
  "rand_engine.file_handlers._writer_batch",
  "rand_engine.file_handlers._writer_stream",
  "rand_engine.examples.common_rand_specs",
])
def test_module_docstring_examples_run(module, tmp_path, monkeypatch):
  """The module has examples; they run under a temporary directory, size at most 10^4 rows, and Spark ones are +SKIP."""
  tests = [t for t in doctest.DocTestFinder().find(importlib.import_module(module)) if t.examples]
  examples = [e for t in tests for e in t.examples]
  assert examples
  assert [e.source for e in examples if "spark" in e.source.lower() and doctest.SKIP not in e.options] == []
  assert [n for e in examples for n in re.findall(r"\.size\((\d[\d_]*)\)", e.source) if int(n.replace("_", "")) > 10_000] == []
  monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))  # examples' mkdtemp dirs land under tmp_path, which pytest cleans
  cwd = tmp_path / "cwd"
  cwd.mkdir()
  monkeypatch.chdir(cwd)
  runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
  report = io.StringIO()
  for t in tests:
    runner.run(t, out=report.write)
  assert runner.failures == 0, report.getvalue()
  assert sorted(p.name for p in cwd.iterdir()) == []  # examples write only inside a directory they create themselves


def _directives(path: Path) -> list[str]:
  return re.findall(r"^::: (\S+)\s*$", path.read_text(encoding="utf-8"), re.M)


def _resolve(dotted: str):
  parts = dotted.split(".")
  obj = importlib.import_module(parts[0])
  for part in parts[1:]:
    obj = getattr(obj, part)
  return obj


@pytest.mark.parametrize("path", [
  pytest.param(p, id=p)
  for p in _directives(DOCS / "reference.md")])
def test_reference_directive_names_the_canonical_documented_object(path):
  """A `:::` directive names the object's defining path, not a re-export or alias, and the object carries a docstring."""
  obj = _resolve(path)
  assert path == f"{obj.__module__}.{obj.__qualname__}"
  assert inspect.getdoc(obj)


def test_docstrings_of_this_file_carry_no_ac_id():
  """No docstring in this file names an acceptance-criterion id."""
  tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
  docs = [ast.get_docstring(n) for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))]
  assert [d for d in docs if d and re.search(r"AC[0-9]", d)] == []


SITE = "https://marcoaureliomenezes.github.io/rand_engine/"
README = ROOT / "README.md"
ISO = r"\d{4}-\d{2}-\d{2}"


def _text(path: Path) -> str:
  return path.read_text(encoding="utf-8")


def _readme_landing():
  text = _text(README)
  title = re.search(r"^# .*$", text, re.M).end()
  pitch = re.search(r"^(?!\s*$)(?!#)(?!\[?!\[).+$", text[title:], re.M).start() + title
  at = lambda pattern: (m.start() if (m := re.search(pattern, text, re.M | re.I)) else -1)
  order = [("pitch", pitch), ("badges", at(r"img\.shields\.io")), ("install", at(r"^## .*install")),
           ("30-second example", at(r"^## .*30")), ("when to use it", at(r"^## .*when to use")),
           ("cases", at(r"^## .*get-started")), ("docs link", text.rfind(SITE))]
  assert min(pos for _, pos in order) >= 0
  assert [name for name, pos in sorted(order, key=lambda o: o[1])] == [name for name, _ in order]
  badges = set(re.findall(r"https://img\.shields\.io/(pypi/v|pypi/pyversions|pypi/l|github/actions)/", text))
  assert badges == {"pypi/v", "pypi/pyversions", "pypi/l", "github/actions"}
  assert [slug for slug in CASES if f"`{slug}`" not in text[order[-2][1]:]] == []
  assert SITE in text and "skills/rand-engine/SKILL.md" in text
  assert "derived-from" not in text
  assert re.findall(r"^\|\s*Method\s*\|", text, re.M) == []


def _pip_installs():
  """Every `pip install` target in README, docs pages and SKILL.md that is not the third-party Kafka client."""
  extras = set(tomllib.loads(_text(ROOT / "pyproject.toml")).get("project", {}).get("optional-dependencies", {}))
  docs = [README, SKILL, *DOCS.glob("**/*.md")]
  found = [(p.name, m) for p in docs for m in re.findall(r"pip install (.+?)(?:`|\s{2,}#|$)", _text(p), re.M)]
  bad = [(n, m) for n, m in found if m.strip() != "kafka-python"
         and not re.fullmatch(rf'"?rand-engine(\[({"|".join(extras)})\])?"?', m.strip())]
  assert bad == []


def _changelog():
  text = _text(ROOT / "CHANGELOG.md")
  headers = re.findall(r"^## \[(\d+\.\d+\.\d+)\](.*)$", text, re.M)
  assert [v for v, rest in headers if not re.fullmatch(rf" - {ISO}", rest)] == []
  assert "## [0.7.0] - 2026-10-14" in text
  section = re.search(rf"^## \[0\.8\.0\] - {ISO}\n(.*?)(?=^## \[)", text, re.M | re.S).group(1)
  added, fixed = (re.search(rf"^### {h}\n(.*?)(?=^###|\Z)", section, re.M | re.S) for h in ("Added", "Fixed"))
  assert fixed is not None
  assert 'pip install "rand-engine[faker]"' in added.group(1)


def _llms():
  text = _text(ROOT / "llms.txt")
  links = LINK.findall(text)
  pages = [u[len(SITE):] for u in links if u.startswith(SITE)]
  assert pages and [u for u in links if u.startswith(REPO_BLOB) and "/docs/" in u] == []
  assert [p for p in pages if not (DOCS / (p.removesuffix("/").removesuffix(".md") or "index")).with_suffix(".md").is_file()] == []
  assert f"{REPO_BLOB}{PRINCIPAL}/skills/rand-engine/SKILL.md" in links
  assert [s for s in CASES if f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{s}.py.txt" not in links] == []


@pytest.mark.parametrize("check", [
  pytest.param(_readme_landing, id="README.md"),
  pytest.param(_pip_installs, id="pip-install",
               marks=pytest.mark.xfail(strict=True, reason="J1.T3 moves extras to project.optional-dependencies")),
  pytest.param(_changelog, id="CHANGELOG.md"),
  pytest.param(_llms, id="llms.txt"),
])
def test_landing_contract(check):
  """Each landing file (README, install lines, CHANGELOG, llms.txt) meets its release contract."""
  check()
