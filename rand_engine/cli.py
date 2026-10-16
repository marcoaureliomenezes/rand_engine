import argparse
import sys
from importlib import resources
from pathlib import Path

CASES = {
  "test-data": "a DataFrame for pipeline tests with null_rate and anomaly_rate",
  "lake": "pk/fk related tables written to a Parquet lake",
  "kafka": "an event stream for Kafka: JSON lines to stdout by default, a producer block ready",
  "databricks": "a Spark/Databricks notebook on native SparkGenerator",
  "faker": "Faker pools sampled at NumPy speed through RandSpecs.faker_pool",
}


def _parser():
  parser = argparse.ArgumentParser(prog="rand-engine", description="rand-engine onboarding: scaffold a runnable example. Slugs: " + ", ".join(CASES))
  commands = parser.add_subparsers(dest="command", required=True)
  commands.add_parser("list", help="print the available slugs and what each teaches")
  get = commands.add_parser("get-started", help="write the example for a slug to a file")
  get.add_argument("slug", choices=list(CASES), help="slug of the example to write: " + ", ".join(CASES))
  get.add_argument("--out", default=".", help="directory to write <slug>-example.py into, created if missing (default: current directory)")
  return parser


def main(argv=None) -> int:
  args = _parser().parse_args(argv)
  if args.command == "list":
    for slug, description in CASES.items():
      print(f"{slug}  {description}")
    return 0
  target = Path(args.out) / f"{args.slug}-example.py"
  if target.exists():
    print(f"error: {target} already exists, not overwriting", file=sys.stderr)
    return 1
  data = (resources.files("rand_engine") / "cases" / f"{args.slug}.py.txt").read_bytes()
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_bytes(data)
  print(target)
  return 0
