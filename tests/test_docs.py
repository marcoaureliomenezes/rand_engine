import re
from pathlib import Path

import pytest

DOCS = Path(__file__).parents[1] / "docs"
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

