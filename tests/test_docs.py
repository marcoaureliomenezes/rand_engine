import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
DOCS = ROOT / "docs"
REPO_BLOB = "https://github.com/marcoaureliomenezes/rand_engine/blob/"
GITFLOW = re.search(r"^gitflow: (.*)$", (ROOT / "specs" / "constitution.md").read_text(encoding="utf-8"), re.M)
PRINCIPAL = json.loads(GITFLOW.group(1))["principal"]
LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"^```((?:python|py)[^\n]*)\n(.*?)^```", re.M | re.S)


def python_blocks(path: Path) -> list[tuple[str, str]]:
  return [(info.strip(), body) for info, body in FENCE.findall(path.read_text(encoding="utf-8"))]


@pytest.mark.parametrize("doc", sorted(DOCS.glob("*.md")), ids=lambda p: p.name)
def test_doc_python_blocks_execute_in_order(doc, tmp_path, monkeypatch, request):
  """AC8.3: every `python` block runs, in file order, in one namespace."""
  blocks = [body for info, body in python_blocks(doc) if info == "python"]
  if any("pyspark" in body for body in blocks):
    request.getfixturevalue("spark_session")  # the doc's getOrCreate() reuses it; skips where Spark cannot run
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__docs__"}
  for i, body in enumerate(blocks):
    exec(compile(body, f"{doc.name}[{i}]", "exec"), namespace)


def test_no_run_is_only_the_kafka_producer():
  """AC8.3: `python no-run` only for a client outside the test dependencies (a Kafka producer)."""
  infos = {info for doc in DOCS.glob("*.md") for info, _ in python_blocks(doc)}
  assert infos <= {"python", "python no-run"}
  no_run = {(doc.name, body) for doc in DOCS.glob("*.md") for info, body in python_blocks(doc) if info == "python no-run"}
  assert {name for name, _ in no_run} == {"5_RECIPES.md"}
  assert all("from kafka import" in body for _, body in no_run)



def test_readme_python_blocks_execute_in_order(tmp_path, monkeypatch):
  """AC7.2: every README `python` block runs, in order, in one namespace; only {python, python no-run} fences."""
  blocks = python_blocks(ROOT / "README.md")
  assert {info for info, _ in blocks} <= {"python", "python no-run"}
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__readme__"}
  for i, (info, body) in enumerate(blocks):
    if info == "python":
      exec(compile(body, f"README.md[{i}]", "exec"), namespace)


@pytest.mark.parametrize("name", ["README.md", "llms.txt"])
def test_links_resolve(name):
  """AC7.4, AC8.4: no relative link (PyPI breaks them); a link into this repo targets the principal branch and a file that exists."""
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
  """Run a doc's python blocks and return every spec a generator was constructed with."""
  from rand_engine import DataGenerator
  seen = []
  init = DataGenerator.__init__

  def record(self, spec, *args, **kwargs):
    seen.append(spec() if callable(spec) else spec)
    init(self, spec, *args, **kwargs)

  monkeypatch.setattr(DataGenerator, "__init__", record)
  monkeypatch.chdir(tmp_path)
  namespace = {"__name__": "__docs__"}
  for i, body in enumerate(b for info, b in python_blocks(DOCS / name) if info == "python"):
    exec(compile(body, f"{name}[{i}]", "exec"), namespace)
  return seen


def test_data_generator_doc_runs_every_new_method_and_modifier(tmp_path, monkeypatch):
  """AC9.2: 1_DATA_GENERATOR.md builds a generator with each 0.7.0 method and modifier (blocks run at light sizes)."""
  columns = [c for spec in documented_specs("1_DATA_GENERATOR.md", tmp_path, monkeypatch) for c in spec.values()]
  assert NEW_METHODS - {c["method"] for c in columns} == set()
  assert MODIFIERS - {key for c in columns for key in c} == set()


@pytest.mark.parametrize("token", [r"\b308\b", r"2\^53|2\*\*53", r"\binf\b", r"float64", r"10\^6|10\*\*6|1_000_000"])
def test_data_generator_doc_states_the_float_rules(token):
  """AC9.2: decimals limit, fine grids, float64 bound comparison, finite rounding / documented inf, poisson lam cap."""
  assert re.search(token, (DOCS / "1_DATA_GENERATOR.md").read_text(encoding="utf-8"))


def test_data_generator_doc_migrates_args_to_kwargs():
  """AC9.4: the guide says kwargs is the only parameter key and which legacy column keys are refused."""
  text = (DOCS / "1_DATA_GENERATOR.md").read_text(encoding="utf-8")
  assert all(key in text for key in ("args", "splitable", "sep"))


def test_spark_doc_runs_the_refusal_of_new_methods():
  """AC9.2: 2_SPARK_GENERATOR.md shows (in an executed block) SparkGenerator refusing a 0.7.0 method and pointing at DataGenerator."""
  code = block_text("2_SPARK_GENERATOR.md")
  assert "SpecValidationError" in code and "DataGenerator" in code
  assert any(method in code for method in NEW_METHODS - {"constant"})


def test_writing_doc_runs_row_batches_and_append():
  """AC9.2: 3_WRITING_FILES.md executes maxRowsPerBatch and mode("append") (new parts beside the old ones)."""
  code = block_text("3_WRITING_FILES.md")
  assert "maxRowsPerBatch" in code and 'mode("append")' in code


def test_recipes_run_the_helpers():
  """AC9.2: 5_RECIPES.md builds specs with RandSpecs.faker_pool and RandSpecs.from_schema."""
  code = block_text("5_RECIPES.md")
  assert "faker_pool(" in code and "from_schema(" in code


@pytest.mark.parametrize("token", ["exponential", "lognormal", "poisson", "zipf", "constant", "null_rate", "anomaly_rate",
                                   "maxRowsPerBatch", "splitable", "faker_pool", "from_schema"])
def test_changelog_0_7_0_lists_the_new_surface_and_migration(token):
  """AC9.2: the 0.7.0 section names each addition and the legacy key migration."""
  text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
  section = text.split("## [0.7.0]", 1)[1].split("\n## [", 1)[0]
  assert token in section
