import argparse
import sys
from typing import NamedTuple
from importlib import resources
from pathlib import Path


class Case(NamedTuple):
  """One get-started starter's user-facing contract."""

  description: str
  resource: str
  filename: str
  kind: str


CASES = {
  "test-data": Case("a DataFrame for pipeline tests with null_rate and anomaly_rate", "test-data.py.txt", "test-data-example.py", "runnable"),
  "lake": Case("pk/fk related tables written to a Parquet lake", "lake.py.txt", "lake-example.py", "runnable"),
  "kafka": Case("an event stream for Kafka: JSON lines to stdout by default, a producer block ready", "kafka.py.txt", "kafka-example.py", "runnable"),
  "databricks": Case("a Spark/Databricks notebook on native SparkGenerator", "databricks.py.txt", "databricks-example.py", "runnable"),
  "faker": Case("Faker pools sampled at NumPy speed through RandSpecs.faker_pool", "faker.py.txt", "faker-example.py", "runnable"),
  "agent": Case("a project AGENTS.md with rand-engine package-use guidance", "agent.md.txt", "AGENTS.md", "agent"),
}


def _parser():
  parser = argparse.ArgumentParser(prog="rand-engine", description="rand-engine onboarding: scaffold a starter. Slugs: " + ", ".join(CASES))
  commands = parser.add_subparsers(dest="command", required=True)
  commands.add_parser("list", help="print the available slugs and what each teaches")
  get = commands.add_parser("get-started", help="write the example for a slug to a file")
  get.add_argument("slug", choices=list(CASES), help="slug of the starter to write: " + ", ".join(CASES))
  get.add_argument("--out", default=".", help="directory to write the starter into, created if missing (default: current directory)")
  return parser


def main(argv=None) -> int:
  args = _parser().parse_args(argv)
  if args.command == "list":
    for slug, case in CASES.items():
      print(f"{slug}  {case.description}")
    return 0
  case = CASES[args.slug]
  target = Path(args.out) / case.filename
  data = (resources.files("rand_engine") / "cases" / case.resource).read_bytes()
  target.parent.mkdir(parents=True, exist_ok=True)
  try:
    with target.open("xb") as scaffold:
      scaffold.write(data)
  except FileExistsError:
    print(f"error: {target} already exists, not overwriting", file=sys.stderr)
    return 1
  print(target)
  return 0
