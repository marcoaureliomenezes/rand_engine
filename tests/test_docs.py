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
