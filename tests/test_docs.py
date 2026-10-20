import ast
import doctest
import importlib
import importlib.util
import io
import inspect
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import warnings
from pathlib import Path

try:
  import tomllib as TEST_TOML
except ModuleNotFoundError:
  import tomli as TEST_TOML

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


def run_python_blocks(doc: Path, tmp_path, monkeypatch) -> dict:
  """Run a documentation page's runnable blocks in their shared namespace."""
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__docs__"}
  for i, body in enumerate(body for info, body in python_blocks(doc) if info == "python"):
    exec(compile(body, f"{doc.name}[{i}]", "exec"), namespace)
  return namespace


SKILL = ROOT / "skills" / "rand-engine" / "SKILL.md"
RUNNABLE_SLUGS = {"test-data", "lake", "kafka", "databricks", "faker"}


def runnable_cases():
  return {slug: case for slug, case in CASES.items() if case.kind == "runnable"}


def agent_case():
  cases = [case for case in CASES.values() if case.kind == "agent"]
  assert len(cases) == 1
  return cases[0]


@pytest.mark.parametrize("doc", [*(pytest.param(p, id=p.relative_to(DOCS).as_posix()) for p in sorted(DOCS.glob("**/*.md"))),
                                 pytest.param(SKILL, id="SKILL.md")])
def test_doc_python_blocks_execute_in_order(doc, tmp_path, monkeypatch, request):
  """Every `python` block runs, in file order, in one namespace."""
  blocks = [body for info, body in python_blocks(doc) if info == "python"]
  if any("pyspark" in body for body in blocks):
    request.getfixturevalue("spark_session")  # the doc's getOrCreate() reuses it; skips where Spark cannot run
  run_python_blocks(doc, tmp_path, monkeypatch)


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


def _table_rows(path: Path, headers: tuple[str, ...]) -> list[list[str]]:
  """Return cells from a documentation table with this exact semantic header."""
  heading = "| " + " | ".join(headers) + " |"
  match = re.search(rf"^{re.escape(heading)}\n\|[-| ]+\n((?:\|.*\n)+)", _text(path), re.M)
  assert match is not None
  return [[cell.strip() for cell in row.strip("|").split("|")] for row in match.group(1).splitlines()]


def _parameter_names(cell: str) -> frozenset[str]:
  """Read parameter identifiers, excluding parenthesized literal/default detail."""
  return frozenset(re.findall(r"`([A-Za-z_]\w*)`", re.sub(r"\([^()]*\)", "", cell)))


def method_parameter_rows(path: Path, headers: tuple[str, ...]) -> dict[str, tuple[frozenset[str], frozenset[str], frozenset[str]]]:
  """Method -> exact required kwargs, optional kwargs, and top-level column fields."""
  rows = _table_rows(path, headers)
  return {
      method: (_parameter_names(cells[1]), _parameter_names(cells[2]), _parameter_names(cells[3]))
      for cells in rows
      for method in re.findall(r"`(\w+)`", cells[0])
  }


def skill_method_table() -> dict[str, str]:
  """Method name -> the Spark column's text, for every row of SKILL.md's method table."""
  rows = _table_rows(SKILL, ("Method", "Required kwargs", "Optional kwargs", "Column fields", "Produces", "Spark"))
  return {name: cells[-1] for cells in rows for name in re.findall(r"`(\w+)`", cells[0])}


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


@pytest.mark.parametrize("slug", runnable_cases())
def test_tutorial_includes_its_case_file(slug):
  """Each tutorial holds one `python no-run` fence whose body is the snippet include of its own case file, which exists."""
  case = CASES[slug]
  assert case.resource == f"{slug}.py.txt"
  blocks = python_blocks(DOCS / "tutorials" / f"{slug}.md")
  assert [(info, _include_of(body)) for info, body in blocks if info == "python no-run"] == [
    ("python no-run", f"rand_engine/cases/{case.resource}")]
  assert (ROOT / f"rand_engine/cases/{case.resource}").is_file()


def test_tutorial_no_run_fences_are_only_case_includes():
  """A `no-run` fence under docs/tutorials/ is exactly one snippet-include line of an existing case file."""
  bodies = [body for doc in DOCS.glob("tutorials/*.md") for info, body in python_blocks(doc) if info == "python no-run"]
  assert [b for b in bodies if _include_of(b) is None or not (ROOT / _include_of(b)).is_file()] == []


def test_getting_started_maps_each_packaged_scaffold():
  """Getting started puts each CLI scaffold's command, file, run command, prerequisite, outcome and guide in one map."""
  rows = _table_rows(DOCS / "getting-started.md", ("Use case", "Command", "File", "Run", "Prerequisite", "Outcome", "Guide"))
  by_slug = {re.search(r"`([^`]+)`", row[0]).group(1): row for row in rows}
  cases = runnable_cases()
  assert set(cases) == RUNNABLE_SLUGS
  assert set(by_slug) == set(cases)
  prerequisites = {
      "test-data": "rand-engine",
      "lake": "rand-engine",
      "kafka": "kafka-python",
      "databricks": "PySpark",
      "faker": "rand-engine[faker]",
  }
  for slug, row in by_slug.items():
    case = cases[slug]
    use_case, command, filename, run, prerequisite, outcome, guide = row
    assert f"`{slug}`" in use_case
    assert command == f"`rand-engine get-started {slug}`"
    assert case.filename == f"{slug}-example.py"
    assert filename == f"`{case.filename}`"
    assert run == f"`python {case.filename}`"
    assert prerequisites[slug] in prerequisite
    assert outcome
    assert LINK.findall(guide) == [f"tutorials/{slug}.md"]


def test_agent_context_is_linked_from_every_agent_onboarding_authority():
  """The optional context scaffold is discoverable separately from the five runnable tutorials."""
  case = agent_case()
  assert set(runnable_cases()) == RUNNABLE_SLUGS
  assert case.resource == "agent.md.txt"
  assert case.filename == "AGENTS.md"
  authorities = [README, DOCS / "getting-started.md", ROOT / "llms.txt", SKILL]
  for authority in authorities:
    text = _text(authority)
    assert "rand-engine get-started agent" in text
    assert "AGENTS.md" in text
  links = set(LINK.findall(_text(ROOT / "llms.txt")))
  assert f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{case.resource}" in links
  assert set(CASES) == RUNNABLE_SLUGS | {"agent"}


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


def test_published_docs_name_no_release_candidate_version():
  """No release-candidate version string in what docs_site.py publishes: docs/ (data files too), README.md, llms.txt, skills/."""
  files = [p for top in (DOCS, ROOT / "skills") for p in top.rglob("*") if p.is_file()] + [ROOT / "README.md", ROOT / "llms.txt"]
  rc = re.compile(r"\d+\.\d+\.\d+rc\d+")
  hits = [f"{p.relative_to(ROOT)}:{n}" for p in files for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if rc.search(line)]
  assert hits == []


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


def test_human_and_skill_method_inventories_match_the_catalog_parameters():
  """Both method tables separate the catalog's kwargs from top-level column fields."""
  from rand_engine.validators.method_specs import METHOD_CATALOG

  expected = {
      method: (frozenset(entry.required), frozenset(entry.optional), frozenset({"cols"}) if entry.requires_cols else frozenset())
      for method, entry in METHOD_CATALOG.items()
  }
  human = method_parameter_rows(
      DOCS / "1_DATA_GENERATOR.md",
      ("Method", "Required kwargs", "Optional kwargs", "Column fields"),
  )
  skill = method_parameter_rows(
      SKILL,
      ("Method", "Required kwargs", "Optional kwargs", "Column fields", "Produces", "Spark"),
  )
  assert human == expected
  assert skill == expected


def test_spark_method_inventory_matches_live_validation():
  """The human Spark table records every catalog method's current validation outcome."""
  from rand_engine.validators.method_specs import METHOD_CATALOG

  match = re.search(
      r"^\| Method \| Spark \|\n\|[-| ]+\n((?:\|.*\n)+)",
      _text(DOCS / "2_SPARK_GENERATOR.md"),
      re.M,
  )
  assert match is not None
  table = match.group(1)
  rows = {
      method: cells[-1]
      for row in table.splitlines()
      for cells in [[cell.strip() for cell in row.strip("|").split("|")]]
      for method in re.findall(r"`(\w+)`", cells[0])
  }
  assert set(rows) == set(METHOD_CATALOG)
  assert {name: (rows[name], spark_outcome(spec.example)) for name, spec in METHOD_CATALOG.items()
          if rows[name] != spark_outcome(spec.example)} == {}


def documented_spark_specs(name, tmp_path, monkeypatch):
  """Run a guide and return each Spark spec with whether construction refused it."""
  from rand_engine import SparkGenerator
  from rand_engine.validators.exceptions import SpecValidationError

  seen = []
  init = SparkGenerator.__init__

  def record(self, spark, functions, spec, *args, **kwargs):
    try:
      init(self, spark, functions, spec, *args, **kwargs)
    except SpecValidationError:
      seen.append((spec, True))
      raise
    seen.append((spec, False))

  monkeypatch.setattr(SparkGenerator, "__init__", record)
  run_python_blocks(DOCS / name, tmp_path, monkeypatch)
  return seen


def test_data_generator_doc_executes_int_zfilled_boundaries(tmp_path, monkeypatch):
  """The pandas guide executes both accepted and refused int_zfilled lengths."""
  outcomes = {
      column["kwargs"]["length"]: refused
      for spec, refused in documented_specs("1_DATA_GENERATOR.md", tmp_path, monkeypatch)
      for column in spec.values()
      if column["method"] == "int_zfilled"
  }
  assert {length: outcomes.get(length) for length in (1, 18, 0, 19)} == {
      1: False, 18: False, 0: True, 19: True,
  }


def test_spark_doc_executes_integer_boundaries(tmp_path, monkeypatch, spark_session):
  """The Spark guide executes its exact digit, carrier and width partitions."""
  outcomes = [
      (column, refused)
      for spec, refused in documented_spark_specs("2_SPARK_GENERATOR.md", tmp_path, monkeypatch)
      for column in spec.values()
  ]
  assert {
      (column["method"], tuple(sorted(column["kwargs"].items()))): refused
      for column, refused in outcomes
      if column["method"] == "int_zfilled"
  }.items() >= {
      ("int_zfilled", (("length", 15),)): False,
      ("int_zfilled", (("length", 16),)): True,
  }.items()
  integers = [(column["kwargs"], refused) for column, refused in outcomes if column["method"] == "integers"]
  assert any(kwargs.get("int_type") == "uint64" and refused for kwargs, refused in integers)
  assert any(
      kwargs.get("int_type") == "int64"
      and kwargs.get("max", 0) - kwargs.get("min", 0) + 1 > 2**53
      and refused
      for kwargs, refused in integers
  )


def documented_correlated_spark_frames(tmp_path, monkeypatch):
  """Run the Spark guide and retain real DataFrames made from correlated specs."""
  from rand_engine import SparkGenerator
  from rand_engine.validators.method_specs import CORRELATED, METHOD_CATALOG

  frames = []
  get_df = SparkGenerator.get_df

  def record(self):
    dataframe = get_df(self)
    methods = {column["method"] for column in self.metadata.values()}
    if any(METHOD_CATALOG[method].kind == CORRELATED for method in methods):
      frames.append((self.metadata, dataframe))
    return dataframe

  monkeypatch.setattr(SparkGenerator, "get_df", record)
  with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    run_python_blocks(DOCS / "2_SPARK_GENERATOR.md", tmp_path, monkeypatch)
  return frames, caught


def test_spark_doc_executes_correlated_methods_as_null_strings(tmp_path, monkeypatch, spark_session):
  """The Spark guide runs all correlated methods as warned NULL string columns."""
  from rand_engine.validators.method_specs import CORRELATED, METHOD_CATALOG

  frames, caught = documented_correlated_spark_frames(tmp_path, monkeypatch)
  expected = {name for name, entry in METHOD_CATALOG.items() if entry.kind == CORRELATED}
  observed = {
      column["method"]
      for metadata, _ in frames
      for column in metadata.values()
      if column["method"] in expected
  }
  assert observed == expected
  assert {method for method in expected if any(method in str(item.message) for item in caught)} == expected
  for metadata, dataframe in frames:
    assert 0 < dataframe.count() <= 10_000
    for name, column in metadata.items():
      if column["method"] in expected:
        field = dataframe.schema[name]
        assert field.dataType.typeName() == "string"
        assert dataframe.where(dataframe[name].isNotNull()).count() == 0


def documented_builder_calls(tmp_path, monkeypatch):
  """Run recipe blocks while recording the builder outputs and refusal partitions they show."""
  from rand_engine import RandSpecs
  from rand_engine.validators.exceptions import RandEngineError, SpecValidationError

  calls = []
  faker_pool, from_schema = RandSpecs.faker_pool, RandSpecs.from_schema

  def record_faker(*args, **kwargs):
    try:
      result = faker_pool(*args, **kwargs)
    except RandEngineError as error:
      calls.append(("faker_pool", args, kwargs, type(error)))
      raise
    calls.append(("faker_pool", args, kwargs, result))
    return result

  def record_schema(*args, **kwargs):
    try:
      result = from_schema(*args, **kwargs)
    except SpecValidationError as error:
      calls.append(("from_schema", args, kwargs, type(error)))
      raise
    calls.append(("from_schema", args, kwargs, result))
    return result

  monkeypatch.setattr(RandSpecs, "faker_pool", record_faker)
  monkeypatch.setattr(RandSpecs, "from_schema", record_schema)
  run_python_blocks(DOCS / "5_RECIPES.md", tmp_path, monkeypatch)
  return calls


def test_recipes_execute_builder_defaults_overrides_and_refusals(tmp_path, monkeypatch):
  """Recipes exercise the real builder recipes, override modes and error partitions."""
  import pyarrow as pa
  from rand_engine.validators.exceptions import RandEngineError, SpecValidationError

  calls = documented_builder_calls(tmp_path, monkeypatch)
  faker = [entry for entry in calls if entry[0] == "faker_pool"]
  assert any(isinstance(entry[-1], dict) and entry[-1]["method"] == "distincts" for entry in faker)
  assert any(entry[-1] is RandEngineError for entry in faker)
  schemas = [entry for entry in calls if entry[0] == "from_schema"]
  families = {
      name
      for _, args, _, result in schemas
      if isinstance(result, dict)
      for field in args[0]
      for name, predicate in {
          "boolean": pa.types.is_boolean,
          "integer": pa.types.is_integer,
          "floating": pa.types.is_floating,
          "string": lambda value: pa.types.is_string(value) or pa.types.is_large_string(value),
          "date": pa.types.is_date,
          "timestamp": lambda value: pa.types.is_timestamp(value) and value.tz is None,
          "null": pa.types.is_null,
      }.items()
      if predicate(field.type)
  }
  assert families == {"boolean", "integer", "floating", "string", "date", "timestamp", "null"}
  overrides = [
      (entry[2]["overrides"], entry[-1])
      for entry in schemas
      if isinstance(entry[-1], dict) and entry[2].get("overrides")
  ]
  assert any(
      "method" not in override
      and set(override.get("kwargs", {})) < set(result[name]["kwargs"])
      and all(result[name]["kwargs"][key] == value for key, value in override.get("kwargs", {}).items())
      for values, result in overrides
      for name, override in values.items()
  )
  assert any(
      "method" in override and result[name] == override
      for values, result in overrides
      for name, override in values.items()
  )
  assert any(entry[-1] is SpecValidationError for entry in schemas)


def test_recipes_render_the_current_common_and_advanced_factory_surfaces():
  """The recipe reference renders both supported factory families from their defining classes."""
  from rand_engine.examples import AdvancedRandSpecs, CommonRandSpecs

  factories = lambda cls: {
      name for name, member in inspect.getmembers(cls)
      if not name.startswith("_") and callable(member)
  }
  common = factories(CommonRandSpecs) - {"faker_pool", "from_schema"}
  advanced = factories(AdvancedRandSpecs)
  assert len(common) == len(advanced) == 10
  assert set(_directives(DOCS / "5_RECIPES.md")) >= {
      f"{CommonRandSpecs.__module__}.{CommonRandSpecs.__qualname__}",
      f"{AdvancedRandSpecs.__module__}.{AdvancedRandSpecs.__qualname__}",
  }


@pytest.mark.parametrize("relative_staging", [False, True], ids=["absolute-staging", "relative-staging"])
def test_writing_doc_runs_row_batches_and_append(tmp_path, monkeypatch, relative_staging):
  """3_WRITING_FILES.md executes maxRowsPerBatch and mode("append") (new parts beside the old ones)."""
  from rand_engine.file_handlers._writer_batch import FileBatchWriter
  from rand_engine.file_handlers._writer_stream import FileStreamWriter

  code = block_text("3_WRITING_FILES.md")
  assert "maxRowsPerBatch" in code and 'mode("append")' in code

  batch, stream, stream_attempts, staged = [], [], [], []
  save, start, stage_files = FileBatchWriter.save, FileStreamWriter.start, FileBatchWriter._stage_files
  mkdtemp = tempfile.mkdtemp

  def return_requested_staging_shape(*args, **kwargs):
    staging = mkdtemp(*args, **kwargs)
    return os.path.relpath(staging) if relative_staging else str(Path(staging).resolve())

  def record_save(self, path):
    batch.append((self.write_format, self.write_mode, dict(self.write_options), Path(path)))
    return save(self, path)

  def record_start(self, path):
    stream_attempts.append((self.write_format, self.write_mode, self.freq, dict(self.write_options)))
    result = start(self, path)
    stream.append((self.write_format, self.write_mode, self.freq, dict(self.write_options)))
    return result

  def record_stage(self, staging, *args, **kwargs):
    staged.append(staging.resolve())
    return stage_files(self, staging, *args, **kwargs)

  monkeypatch.setattr(FileBatchWriter, "save", record_save)
  monkeypatch.setattr(FileStreamWriter, "start", record_start)
  monkeypatch.setattr(FileBatchWriter, "_stage_files", record_stage)
  monkeypatch.setattr(tempfile, "mkdtemp", return_requested_staging_shape)
  run_python_blocks(DOCS / "3_WRITING_FILES.md", tmp_path, monkeypatch)

  assert {format for format, _, _, _ in batch} == {"csv", "json", "parquet", "sqlite"}
  assert {mode for _, mode, _, _ in batch} == {"append", "overwrite"}
  assert any(not options for _, mode, options, _ in batch if mode == "overwrite")
  assert {options.get("numFiles") for _, _, options, _ in batch if "numFiles" in options} == {2, 3, 4}
  assert any(options.get("maxRowsPerBatch") == 100 for _, _, options, _ in batch)
  assert stream == [("json", "overwrite", 0.1, {"timeout": 0.3})]
  assert any(format == "sqlite" for format, _, _, _ in stream_attempts)
  assert staged and all(path.parent == tmp_path / "out" and path.name.endswith(".staging") for path in staged)
  assert not [path for path in staged if path.exists()]
  assert len(list((tmp_path / "out" / "clients_json").iterdir())) == 4
  assert len(list((tmp_path / "out" / "log").iterdir())) == 4
  assert len(list((tmp_path / "out" / "stream").iterdir())) >= 2
  sqlite_outputs = [(options, tmp_path / path) for format, _, options, path in batch if format == "sqlite"]
  assert sqlite_outputs
  for options, path in sqlite_outputs:
    with sqlite3.connect(path) as database:
      table = options["table"].replace('"', '""')
      assert database.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] > 0


def _writer_option_table() -> dict[str, str]:
  """The writing guide's format and writer option rows."""
  text = _text(DOCS / "3_WRITING_FILES.md")
  table = re.search(r"^\| Format \| Options \|\n\|[-| ]+\n((?:\|.*\n)+)", text, re.M).group(1)
  return {cells[0].replace("`", ""): cells[1] for row in table.splitlines()
          for cells in [[cell.strip() for cell in row.strip("|").split("|")]]}


def test_writing_doc_inventory_matches_the_accepted_writer_options():
  """The writer guide lists every accepted format option, including defaults and codecs."""
  from rand_engine import DataGenerator

  rows = _writer_option_table()
  files = set(DataGenerator({"value": {"method": "integers", "kwargs": {"min": 0, "max": 1}}}).size(0).write.writer_method)
  assert set(rows) == files | {"sqlite", "write (batch)", "writeStream"}
  assert "sep" in rows["csv"] and {"gzip", "bz2", "xz", "zip"} <= set(re.findall(r"`(gzip|bz2|xz|zip)`", rows["csv"]))
  assert {"compression", "snappy", "gzip", "zstd", "brotli", "lz4"} <= set(re.findall(r"`(\w+)`", rows["parquet"]))
  assert {"force_ascii", "indent", "orient"} <= {name for name in ("force_ascii", "indent", "orient") if name in rows["json"]}
  assert {"gzip", "bz2", "xz", "zip"} <= set(re.findall(r"`(gzip|bz2|xz|zip)`", rows["json"]))
  assert "numFiles" in rows["write (batch)"] and "maxRowsPerBatch" in rows["write (batch)"]
  assert "timeout" in rows["writeStream"]
  assert {"table", "overwrite", "append"} <= set(re.findall(r"`(\w+)`", rows["sqlite"]))
  assert "numFiles" not in rows["sqlite"] and "maxRowsPerBatch" not in rows["sqlite"]


def test_key_guides_execute_the_event_time_fk_mapping_and_zero_eligible_refusal(tmp_path, monkeypatch):
  """The human and agent key examples execute valid and zero-eligible event-time foreign keys."""
  required = {"born_before", "parent_start", "parent_rate", "child_start", "child_rate"}
  for guide in (DOCS / "4_CONSTRAINTS.md", SKILL):
    guide_tmp = tmp_path / guide.stem
    guide_tmp.mkdir()
    namespace = run_python_blocks(guide, guide_tmp, monkeypatch)
    bound = namespace["event_time_born_before"]
    assert set(bound) == required - {"born_before"}
    assert all(type(value) in {int, float} for value in bound.values())
    assert namespace["event_time_orders"]["customer_id"].isin(
        namespace["event_time_parents"]["customer_id"]
    ).all()
    assert namespace["event_time_zero_eligible"] is True


def test_stream_guidance_executes_scalar_and_nested_records(tmp_path, monkeypatch):
  """The stream guide exposes real scalar and nested-value records from its examples."""
  namespace = run_python_blocks(DOCS / "1_DATA_GENERATOR.md", tmp_path, monkeypatch)
  assert namespace["scalar_records"] and namespace["nested_records"]
  assert all(isinstance(record, dict) for record in namespace["scalar_records"])
  assert any(any(isinstance(value, (dict, list, tuple)) for value in record.values())
             for record in namespace["nested_records"])


def test_comparison_route_is_sourced_and_marks_benchmarks_as_internal_only():
  """The capability comparison has primary sources and does not present rand-engine measurements as competitor timings."""
  page = DOCS / "comparison.md"
  text = _text(page)
  urls = set(re.findall(r"https://[^)\s]+", text))
  assert {
      "https://faker.readthedocs.io/en/stable/",
      "https://github.com/databrickslabs/dbldatagen",
      "https://databrickslabs.github.io/dbldatagen/public_docs/reference/api/dbldatagen.data_generator.html",
  } <= urls
  links = LINK.findall(text)
  assert "BENCHMARKS.md" in links
  assert any("benchmarks/speed.py" in link for link in links)
  nav = _text(ROOT / "mkdocs.yml")
  llms = _text(ROOT / "llms.txt")
  assert "comparison.md" in nav
  assert f"{SITE}comparison/" in llms


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


def test_reference_directive_names_the_canonical_documented_object():
  """reference.md's `:::` directives are exactly the defining paths of the `rand_engine.__all__` objects, each with a docstring."""
  import rand_engine
  objs = [getattr(rand_engine, n) for n in rand_engine.__all__]
  directives = re.findall(r"^::: (\S+)\s*$", (DOCS / "reference.md").read_text(encoding="utf-8"), re.M)
  assert sorted(directives) == sorted(f"{o.__module__}.{o.__qualname__}" for o in objs)
  assert [o for o in objs if not inspect.getdoc(o)] == []


def _directives(path: Path) -> list[str]:
  return re.findall(r"^::: (\S+)\s*$", path.read_text(encoding="utf-8"), re.M)


def _writer_reference_surface():
  from rand_engine.file_handlers._writer_batch import FileBatchWriter
  from rand_engine.file_handlers._writer_stream import FileStreamWriter
  from rand_engine.file_handlers.writer import FileWriter
  classes = (FileWriter, FileBatchWriter, FileStreamWriter)
  return {
    f"{cls.__module__}.{cls.__qualname__}": {
      name for name, member in inspect.getmembers(cls)
      if not name.startswith("_") and callable(member)
    }
    for cls in classes
  }


def test_returned_writer_reference_resolves_the_live_class_and_callable_inventory():
  """The writing guide renders the classes returned by write and writeStream, with their chain and terminal calls."""
  expected = {
    "rand_engine.file_handlers.writer.FileWriter": {"format", "mode", "option", "options"},
    "rand_engine.file_handlers._writer_batch.FileBatchWriter": {"format", "mode", "option", "options", "save"},
    "rand_engine.file_handlers._writer_stream.FileStreamWriter": {"format", "mode", "option", "options", "trigger", "start"},
  }
  assert _writer_reference_surface() == expected
  assert _directives(DOCS / "3_WRITING_FILES.md") == list(expected)


def test_error_reference_resolves_the_caller_facing_family():
  """The error reference renders every library exception a caller can catch, including its common base."""
  from rand_engine.validators import exceptions
  expected = [
    exceptions.RandEngineError,
    exceptions.SpecValidationError,
    exceptions.ColumnGenerationError,
    exceptions.TransformerError,
    exceptions.FileWriterError,
  ]
  assert all(issubclass(error, exceptions.RandEngineError) for error in expected)
  assert _directives(DOCS / "errors.md") == [f"{error.__module__}.{error.__qualname__}" for error in expected]


def test_reference_navigation_exposes_the_main_writer_and_error_destinations():
  """The docs navigation links to the main API and to separate returned-writer and error references."""
  nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
  assert [path for path in ("reference.md", "3_WRITING_FILES.md", "errors.md") if path not in nav] == []
  reference = re.search(r"^  - Reference:\n((?:^      - .+\n)+)", nav, re.M)
  children = re.findall(r"^      - (.*): (.*)$", reference.group(1), re.M)
  assert children == [
    ("Main API", "reference.md"),
    ("Returned writers", "3_WRITING_FILES.md"),
    ("Errors", "errors.md"),
  ]


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
  extras = set(TEST_TOML.loads(_text(ROOT / "pyproject.toml")).get("project", {}).get("optional-dependencies", {}))
  docs = [README, SKILL, *DOCS.glob("**/*.md")]
  found = [(p.name, m) for p in docs for m in re.findall(r"pip install (.+?)(?:`|\s{2,}#|$)", _text(p), re.M)]
  bad = [(n, m) for n, m in found if m.strip() != "kafka-python"
         and not re.fullmatch(rf'"?rand-engine(\[({"|".join(extras)})\])?"?', m.strip())]
  assert bad == []


def _changelog():
  text = _text(ROOT / "CHANGELOG.md")
  headers = re.findall(r"^## \[(\d+\.\d+\.\d+)\](.*)$", text, re.M)
  assert [rest for v, rest in headers if v == "0.8.0"] == [" - 2026-10-18"]
  assert [v for v, rest in headers if v != "0.8.0" and not re.fullmatch(rf" - {ISO}", rest)] == []
  assert "## [0.7.0] - 2026-10-14" in text
  section = re.search(r"^## \[0\.8\.0\] - 2026-10-18\n(.*?)(?=^## \[)", text, re.M | re.S).group(1)
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
  cases = runnable_cases()
  assert set(cases) == RUNNABLE_SLUGS
  assert [slug for slug, case in cases.items()
          if f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{case.resource}" not in links] == []
  assert f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{agent_case().resource}" in links


def test_llms_points_agents_at_the_api_writer_error_builder_domain_and_case_destinations():
  """llms.txt advertises rendered destinations for each discovery route and every runnable case file."""
  links = set(LINK.findall(_text(ROOT / "llms.txt")))
  assert {
      f"{SITE}reference/",
      f"{SITE}3_WRITING_FILES/",
      f"{SITE}errors/",
      f"{SITE}5_RECIPES/",
      f"{SITE}1_DATA_GENERATOR/",
      f"{SITE}2_SPARK_GENERATOR/",
  } <= links
  cases = runnable_cases()
  assert set(cases) == RUNNABLE_SLUGS
  assert {f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{case.resource}" for case in cases.values()} <= links
  assert f"{REPO_BLOB}{PRINCIPAL}/rand_engine/cases/{agent_case().resource}" in links


@pytest.mark.parametrize("check", [
  pytest.param(_readme_landing, id="README.md"),
  pytest.param(_pip_installs, id="pip-install"),
  pytest.param(_changelog, id="CHANGELOG.md"),
  pytest.param(_llms, id="llms.txt"),
])
def test_landing_contract(check):
  """Each landing file (README, install lines, CHANGELOG, llms.txt) meets its release contract."""
  check()


REPO_MASTER = f"{REPO_BLOB}{PRINCIPAL}/"


def _prepare_docs(tmp_path):
  """Prepare one isolated documentation input and its public raw resources."""
  output = tmp_path / "prepared"
  result = subprocess.run(
      [sys.executable, str(ROOT / "scripts" / "docs_site.py"), "--output", str(output)],
      cwd=ROOT,
      capture_output=True,
      text=True,
      env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
  )
  assert result.returncode == 0, result.stderr
  return output / "input", output / "public"


def _prepared_texts(input_root: Path, public_root: Path) -> dict[str, str]:
  paths = [*sorted((input_root / "docs").glob("**/*.md")), public_root / "llms.txt",
           *sorted((public_root / "docs").glob("**/*.md")),
           public_root / "skills" / "rand-engine" / "SKILL.md"]
  assert all(path.is_file() for path in paths)
  return {path.relative_to(input_root if path.is_relative_to(input_root) else public_root).as_posix(): _text(path)
          for path in paths}


def test_docs_preparation_stable_keeps_ordinary_install_and_principal_routes(tmp_path):
  """Stable preparation retains ordinary package installation and the principal source authority."""
  source_paths = [README, ROOT / "llms.txt", SKILL, ROOT / "mkdocs.yml", *sorted(DOCS.glob("**/*.md"))]
  before = {path: path.read_bytes() for path in source_paths}
  input_root, public_root = _prepare_docs(tmp_path)
  assert {path: path.read_bytes() for path in source_paths} == before
  texts = _prepared_texts(input_root, public_root)
  assert {path.name for path in (public_root / "rand_engine" / "cases").glob("*")} == {
      case.resource for case in CASES.values()}
  assert any("pip install rand-engine" in text for text in texts.values())
  assert any(REPO_MASTER in text for text in texts.values())
  mirror = public_root / "skills" / "rand-engine" / "SKILL.md"
  assert mirror.read_bytes() == SKILL.read_bytes()


def _docs_site_module():
  """Load the documentation preparation authority without a network boundary."""
  spec = importlib.util.spec_from_file_location("docs_site", ROOT / "scripts" / "docs_site.py")
  assert spec is not None and spec.loader is not None
  module = importlib.util.module_from_spec(spec)
  sys.modules[spec.name] = module
  spec.loader.exec_module(module)
  return module


def test_docs_site_preparation_works_without_tomllib_or_tomli(tmp_path):
  """Preparation is standard-library-only when a Python 3.10 process has no TOML parser."""
  output = tmp_path / "prepared"
  script = textwrap.dedent(f"""
      import builtins
      import runpy
      from pathlib import Path

      original_import = builtins.__import__
      def without_toml_parser(name, *args, **kwargs):
          if name in {{"tomllib", "tomli"}}:
              raise ModuleNotFoundError(name)
          return original_import(name, *args, **kwargs)
      builtins.__import__ = without_toml_parser
      module = runpy.run_path({str(ROOT / "scripts" / "docs_site.py")!r})
      target = Path({str(output)!r})
      module["prepare"](target)
      assert (target / "input" / "mkdocs.yml").is_file()
  """)
  result = subprocess.run(
      [sys.executable, "-S", "-c", script], cwd=ROOT, capture_output=True, text=True, check=False)
  assert result.returncode == 0, result.stderr


def test_docs_workflow_deploys_pages_from_master_only():
  """The deploy job's gate and the whole workflow name master as the only deploying branch."""
  text = _text(ROOT / ".github" / "workflows" / "docs.yml")
  deploy = re.search(r"^  deploy:\n(?:    .*\n|\n)*", text, re.M).group(0)
  gate = re.search(r"^    if: (.*)$", deploy, re.M).group(1)
  assert gate == "github.event_name == 'push' && github.ref == 'refs/heads/master'"
  assert set(re.findall(r"refs/heads/[\w./-]+", text)) == {"refs/heads/master"}
