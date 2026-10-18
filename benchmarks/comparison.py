"""Run the bounded, observational cross-library comparison in CI."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable


PYTHON_ROWS = 100_000
SPARK_ROWS = 1_000_000
SPARK_PARTITIONS = 8
PYTHON_SIDES = ("rand-engine", "faker")
SPARK_SIDES = ("rand-engine", "dbldatagen")
PYTHON_ORDER = ("rand-engine", "faker", "faker", "rand-engine", "rand-engine", "faker")
SPARK_ORDER = ("rand-engine", "dbldatagen", "dbldatagen", "rand-engine", "rand-engine", "dbldatagen")
FORBIDDEN_ARTIFACT_FIELDS = {"winner", "score", "threshold", "ranking"}


def validate_python_records(records: Any) -> None:
  """Validate the fully materialized Python comparison result."""
  if not isinstance(records, list) or len(records) != PYTHON_ROWS:
    raise ValueError("Python result must be a list of 100000 records")
  for record in records:
    if not isinstance(record, dict) or set(record) != {"value", "tier", "active"}:
      raise ValueError("Python records must have exactly value, tier and active")
    value = record["value"]
    if type(value) is not int or not 0 <= value <= 999_999:
      raise ValueError("Python value must be an integer in the approved range")
    if type(record["tier"]) is not str or record["tier"] not in {"bronze", "silver", "gold"}:
      raise ValueError("Python tier must use the approved domain")
    if type(record["active"]) is not bool:
      raise ValueError("Python active must be a bool")


def validate_spark_observation(observation: Any) -> None:
  """Validate evidence collected outside a Spark sample clock."""
  if not isinstance(observation, dict):
    raise ValueError("Spark observation must be a mapping")
  if observation.get("count") != SPARK_ROWS or observation.get("partitions") != SPARK_PARTITIONS:
    raise ValueError("Spark row count and partition count must match the workload")
  schema = observation.get("schema")
  if not isinstance(schema, list) or len(schema) != 3:
    raise ValueError("Spark schema must have exactly three columns")
  expected_names = ("ordinal", "value", "tier")
  for index, name in enumerate(expected_names):
    field = schema[index]
    if not isinstance(field, (list, tuple)) or len(field) != 3 or field[0] != name or type(field[2]) is not bool:
      raise ValueError("Spark schema does not retain the observed payload metadata")
  if schema[0][1] not in {"long", "bigint"} or schema[1][1] != "int" or schema[2][1] != "string":
    raise ValueError("Spark schema does not match the approved types")
  ordinal = observation.get("ordinal")
  if ordinal != {"minimum": 0, "maximum": SPARK_ROWS - 1, "distinct_count": SPARK_ROWS}:
    raise ValueError("Spark ordinal evidence does not match the workload")
  value = observation.get("value")
  if not isinstance(value, dict) or not 0 <= value.get("minimum", -1) <= value.get("maximum", SPARK_ROWS) <= 999_999:
    raise ValueError("Spark value evidence does not match the workload")
  tier = observation.get("tier")
  if not isinstance(tier, dict) or set(tier.get("values", ())) != {"bronze", "silver", "gold"}:
    raise ValueError("Spark tier evidence does not match the workload")
  if observation.get("nulls") != {"ordinal": 0, "value": 0, "tier": 0}:
    raise ValueError("Spark observations must record no null payload values")
  aggregate = observation.get("aggregate")
  if not isinstance(aggregate, dict) or aggregate.get("count") != SPARK_ROWS or aggregate.get("sum") is None:
    raise ValueError("Spark aggregate must retain the fully evaluated payload")
  if not _plan_hashes_payload(observation.get("physical_plan"), expected_names):
    raise ValueError("Spark physical plan must retain every payload expression")


def _plan_hashes_payload(plan: Any, names: tuple[str, ...]) -> bool:
  """Return whether one physical-plan hash call includes every payload name."""
  if not isinstance(plan, str):
    return False
  lowered = plan.lower()
  start = lowered.find("xxhash64(")
  if start < 0:
    return False
  depth = 0
  for index in range(start + len("xxhash64"), len(lowered)):
    character = lowered[index]
    if character == "(":
      depth += 1
    elif character == ")":
      depth -= 1
      if depth == 0:
        arguments = lowered[start:index + 1]
        return all(name in arguments for name in names)
  return False


def _timed(callable_: Callable[[], Any], clock: Callable[[], float]) -> tuple[float, Any]:
  started = clock()
  result = callable_()
  return clock() - started, result


def _validate_result(workload: str, result: Any) -> dict[str, Any]:
  if workload == "python":
    validate_python_records(result)
    return {"status": "passed"}
  observation = result.get("observation", result) if isinstance(result, dict) else result
  validator = result.get("validator") if isinstance(result, dict) else None
  if validator is not None:
    validator()
  validate_spark_observation(observation)
  return {"status": "passed", "observation": observation}


def _workload_definition(workload: str) -> dict[str, Any]:
  if workload == "python":
    return {"rows": PYTHON_ROWS, "fields": ["value", "tier", "active"]}
  return {"rows": SPARK_ROWS, "partitions": SPARK_PARTITIONS, "fields": ["ordinal", "value", "tier"]}


def run_comparison(
    factories: dict[str, dict[str, Callable[[], Any]]], *, clock: Callable[[], float] = time.perf_counter,
    provenance: dict[str, Any], setup_seconds: dict[str, float] | None = None,
) -> dict[str, Any]:
  """Collect warm-ups, alternating samples and validations for both contracts."""
  workloads: dict[str, Any] = {}
  for workload, sides, order in (("python", PYTHON_SIDES, PYTHON_ORDER), ("spark", SPARK_SIDES, SPARK_ORDER)):
    if set(factories.get(workload, ())) != set(sides):
      raise ValueError(f"{workload} factories must contain both approved sides")
    warmups: list[str] = []
    warmup_seconds: dict[str, float] = {}
    validation_seconds = 0.0
    schemas: dict[str, Any] = {}
    plans: dict[str, str] = {}
    observations: dict[str, Any] = {}
    for side in sides:
      factory = factories[workload][side]
      warmup_started = time.perf_counter()
      result = factory()
      warmup_seconds[side] = time.perf_counter() - warmup_started
      validation_started = time.perf_counter()
      validation = _validate_result(workload, result)
      validation_seconds += time.perf_counter() - validation_started
      if workload == "spark":
        observation = validation["observation"]
        schemas[side] = observation["schema"]
        plans[side] = observation["physical_plan"]
        observations[side] = observation
      warmups.append(side)
    samples = {side: [] for side in sides}
    for side in order:
      seconds, result = _timed(factories[workload][side], clock)
      validation_started = time.perf_counter()
      validation = _validate_result(workload, result)
      validation_seconds += time.perf_counter() - validation_started
      if workload == "spark":
        observation = validation["observation"]
        schemas[side] = observation["schema"]
        plans[side] = observation["physical_plan"]
        observations[side] = observation
      samples[side].append(seconds)
    entry: dict[str, Any] = {
        "definition": _workload_definition(workload),
        "warmups": warmups,
        "warmup_seconds": warmup_seconds,
        "sample_order": list(order),
        "samples": samples,
        "medians": {side: statistics.median(samples[side]) for side in sides},
        "validation": {"status": "passed"},
        "setup_seconds": None if setup_seconds is None else setup_seconds[workload],
        "validation_seconds": validation_seconds,
    }
    if workload == "spark":
      entry["schemas"] = schemas
      entry["physical_plans"] = plans
      entry["validation_observations"] = observations
    workloads[workload] = entry
  return {"artifact_version": 1, "status": "success", "provenance": provenance, "workloads": workloads}


def _has_forbidden_field(value: Any) -> bool:
  if isinstance(value, dict):
    return any(key.lower() in FORBIDDEN_ARTIFACT_FIELDS or _has_forbidden_field(item) for key, item in value.items())
  if isinstance(value, list):
    return any(_has_forbidden_field(item) for item in value)
  return False


def validate_artifact(artifact: Any) -> None:
  """Validate the durable observational artifact before publication."""
  if not isinstance(artifact, dict) or _has_forbidden_field(artifact):
    raise ValueError("Artifact has an unsupported field")
  if type(artifact.get("artifact_version")) is not int or artifact["artifact_version"] != 1 or artifact.get("status") != "success":
    raise ValueError("Artifact must be a successful versioned observation")
  provenance = artifact.get("provenance")
  if not isinstance(provenance, dict):
    raise ValueError("Artifact must retain provenance")
  distribution = provenance.get("rand_engine")
  if not isinstance(distribution, dict) or distribution.get("version") != "0.8.0" or distribution.get("editable") is not False:
    raise ValueError("Artifact must identify the installed public distribution")
  wheel_sha256 = distribution.get("wheel_sha256")
  if not isinstance(wheel_sha256, str) or len(wheel_sha256) != 64:
    raise ValueError("Artifact must retain the wheel hash")
  for key in ("pip_report", "harness_sha", "python", "java", "spark", "os", "runner", "versions"):
    if not provenance.get(key):
      raise ValueError(f"Artifact lacks {key} provenance")
  if not isinstance(provenance["harness_sha"], str) or len(provenance["harness_sha"]) != 40:
    raise ValueError("Artifact harness SHA is invalid")
  workloads = artifact.get("workloads")
  if not isinstance(workloads, dict) or set(workloads) != {"python", "spark"}:
    raise ValueError("Artifact must retain both workloads")
  for workload, sides, order in (("python", PYTHON_SIDES, PYTHON_ORDER), ("spark", SPARK_SIDES, SPARK_ORDER)):
    entry = workloads[workload]
    if entry.get("definition") != _workload_definition(workload) or entry.get("warmups") != list(sides):
      raise ValueError(f"Artifact {workload} definition is invalid")
    if entry.get("sample_order") != list(order) or set(entry.get("samples", ())) != set(sides):
      raise ValueError(f"Artifact {workload} samples are invalid")
    for side in sides:
      values = entry["samples"][side]
      if not isinstance(values, list) or len(values) != 3 or entry.get("medians", {}).get(side) != statistics.median(values):
        raise ValueError(f"Artifact {workload} medians are invalid")
    if entry.get("validation", {}).get("status") != "passed":
      raise ValueError(f"Artifact {workload} validation did not pass")
  spark = workloads["spark"]
  if set(spark.get("schemas", ())) != set(SPARK_SIDES) or set(spark.get("physical_plans", ())) != set(SPARK_SIDES):
    raise ValueError("Artifact must retain Spark schemas and plans")


def _python_factories() -> dict[str, Callable[[], list[dict[str, Any]]]]:
  from faker import Faker
  from rand_engine import DataGenerator

  spec = {
      "value": {"method": "integers", "kwargs": {"min": 0, "max": 999_999}},
      "tier": {"method": "distincts", "kwargs": {"distincts": ["bronze", "silver", "gold"]}},
      "active": {"method": "booleans", "kwargs": {"true_prob": 0.5}},
  }

  def rand_engine() -> list[dict[str, Any]]:
    rows = DataGenerator(spec, seed=42).size(PYTHON_ROWS).get_df().to_dict("records")
    return [{"value": int(row["value"]), "tier": str(row["tier"]), "active": bool(row["active"])} for row in rows]

  def faker() -> list[dict[str, Any]]:
    fake = Faker()
    fake.seed_instance(42)
    return [
        {"value": int(fake.random_int(0, 999_999)), "tier": str(fake.random_element(("bronze", "silver", "gold"))), "active": bool(fake.pybool())}
        for _ in range(PYTHON_ROWS)
    ]

  return {"rand-engine": rand_engine, "faker": faker}


def _spark_factories(spark: Any) -> dict[str, Callable[[], dict[str, Any]]]:
  import dbldatagen as dg
  from pyspark.sql import functions as F
  from rand_engine import SparkGenerator

  spec = {
      "ordinal": {"method": "pk", "kwargs": {"start": 0}},
      "value": {"method": "integers", "kwargs": {"min": 0, "max": 999_999}},
      "tier": {"method": "distincts", "kwargs": {"distincts": ["bronze", "silver", "gold"]}},
  }

  def observe(frame: Any) -> dict[str, Any]:
    frame = frame.select(
        F.col("ordinal").cast("long").alias("ordinal"),
        F.col("value").cast("int").alias("value"),
        F.col("tier").cast("string").alias("tier"),
    )
    hashed = frame.select(F.xxhash64("ordinal", "value", "tier").alias("payload_hash"))
    aggregate = hashed.agg(F.count("*").alias("count"), F.sum("payload_hash").alias("sum"))
    aggregate_result = aggregate.collect()[0].asDict(recursive=True)
    observation: dict[str, Any] = {}

    def validate() -> None:
      summary = frame.agg(
          F.count("*").alias("count"), F.countDistinct("ordinal").alias("distinct_count"),
          F.min("ordinal").alias("ordinal_min"), F.max("ordinal").alias("ordinal_max"),
          F.min("value").alias("value_min"), F.max("value").alias("value_max"),
          F.sum(F.col("ordinal").isNull().cast("int")).alias("ordinal_nulls"),
          F.sum(F.col("value").isNull().cast("int")).alias("value_nulls"),
          F.sum(F.col("tier").isNull().cast("int")).alias("tier_nulls"),
          F.sort_array(F.collect_set("tier")).alias("tiers"),
      ).collect()[0].asDict(recursive=True)
      observation.update({
          "count": summary["count"],
          "partitions": frame.rdd.getNumPartitions(),
          "schema": [
              (field.name, field.dataType.simpleString(), field.nullable)
              for field in frame.schema
          ],
          "ordinal": {
              "minimum": summary["ordinal_min"],
              "maximum": summary["ordinal_max"],
              "distinct_count": summary["distinct_count"],
          },
          "value": {"minimum": summary["value_min"], "maximum": summary["value_max"]},
          "tier": {"values": summary["tiers"]},
          "nulls": {
              "ordinal": summary["ordinal_nulls"],
              "value": summary["value_nulls"],
              "tier": summary["tier_nulls"],
          },
          "aggregate": aggregate_result,
          "physical_plan": aggregate._jdf.queryExecution().executedPlan().toString(),
      })

    return {"observation": observation, "validator": validate}

  def rand_engine() -> dict[str, Any]:
    return observe(SparkGenerator(spark, F, spec, seed=42).size(SPARK_ROWS).get_df())

  def dbldatagen() -> dict[str, Any]:
    frame = (
        dg.DataGenerator(sparkSession=spark, name="comparison", rows=SPARK_ROWS, partitions=SPARK_PARTITIONS,
                         randomSeedMethod="hash_fieldname", randomSeed=42, seedColumnName="ordinal")
        .withIdOutput()
        .withColumn("value", "int", minValue=0, maxValue=999_999, random=True)
        .withColumn("tier", "string", values=["bronze", "silver", "gold"], random=True)
        .build()
    )
    return observe(frame)

  return {"rand-engine": rand_engine, "dbldatagen": dbldatagen}


def _package_versions() -> dict[str, str]:
  names = ("Faker", "dbldatagen", "pyspark", "numpy", "pandas", "pyarrow", "setuptools")
  return {name: importlib.metadata.version(name) for name in names}


def _verify_pip_report(path: str, wheel_sha256: str) -> None:
  report = json.loads(Path(path).read_text(encoding="utf-8"))
  installs = report.get("install", []) if isinstance(report, dict) else []
  for item in installs:
    metadata = item.get("metadata", {})
    if metadata.get("name", "").lower() != "rand-engine":
      continue
    download = item.get("download_info", {})
    hashes = download.get("archive_info", {}).get("hashes", {})
    if metadata.get("version") == "0.8.0" and hashes.get("sha256") == wheel_sha256:
      return
  raise RuntimeError("pip report does not identify the published rand-engine wheel")


def _provenance(args: argparse.Namespace) -> dict[str, Any]:
  version = importlib.metadata.version("rand-engine")
  if version != "0.8.0":
    raise RuntimeError("comparison requires the published rand-engine 0.8.0 distribution")
  _verify_pip_report(args.pip_report, args.wheel_sha256)
  direct_url = importlib.metadata.distribution("rand-engine").read_text("direct_url.json")
  if direct_url and json.loads(direct_url).get("dir_info", {}).get("editable"):
    raise RuntimeError("comparison refuses an editable rand-engine distribution")
  return {
      "rand_engine": {"version": version, "editable": False, "wheel_sha256": args.wheel_sha256,
                      "distribution_metadata": {"name": "rand-engine", "version": version}},
      "pip_report": args.pip_report,
      "harness_sha": args.harness_sha,
      "python": platform.python_version(),
      "java": subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True).splitlines()[0],
      "spark": importlib.metadata.version("pyspark"),
      "os": platform.platform(),
      "runner": args.runner,
      "versions": _package_versions(),
      "environment": {key: os.environ[key] for key in ("RUNNER_OS", "RUNNER_ARCH") if key in os.environ},
  }


def markdown(artifact: dict[str, Any]) -> str:
  """Render the artifact's retained samples as a short Actions summary."""
  lines = ["# Observational comparison", "", f"Status: `{artifact['status']}`", ""]
  for workload, entry in artifact.get("workloads", {}).items():
    lines.extend([f"## {workload}", "", "| implementation | samples (seconds) | median (seconds) |", "|---|---:|---:|"])
    for side, samples in entry.get("samples", {}).items():
      lines.append(f"| {side} | {', '.join(f'{sample:.6f}' for sample in samples)} | {entry['medians'][side]:.6f} |")
    lines.append("")
  return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
  """Write JSON and Markdown evidence for one observational CI invocation."""
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--output-dir", type=Path, required=True)
  parser.add_argument("--pip-report", required=True)
  parser.add_argument("--wheel-sha256", required=True)
  parser.add_argument("--harness-sha", required=True)
  parser.add_argument("--runner", default=os.environ.get("RUNNER_NAME", "unknown"))
  args = parser.parse_args(argv)
  if len(args.wheel_sha256) != 64 or len(args.harness_sha) != 40:
    parser.error("wheel and harness hashes must be SHA-256 and Git SHA values")
  args.output_dir.mkdir(parents=True, exist_ok=True)
  try:
    python_setup_started = time.perf_counter()
    python_factories = _python_factories()
    python_setup_seconds = time.perf_counter() - python_setup_started
    spark_setup_started = time.perf_counter()
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.master("local[8]").appName("rand-engine-comparison").config("spark.sql.shuffle.partitions", "8").config("spark.ui.enabled", "false").getOrCreate()
    try:
      provenance = _provenance(args)
      spark_factories = _spark_factories(spark)
      spark_setup_seconds = time.perf_counter() - spark_setup_started
      artifact = run_comparison(
          {"python": python_factories, "spark": spark_factories},
          provenance=provenance,
          setup_seconds={"python": python_setup_seconds, "spark": spark_setup_seconds},
      )
      validate_artifact(artifact)
    finally:
      spark.stop()
  except Exception as error:
    artifact = {"artifact_version": 1, "status": "controlled_failure", "errors": [f"{type(error).__name__}: {error}"]}
  (args.output_dir / "comparison.json").write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
  (args.output_dir / "comparison.md").write_text(markdown(artifact), encoding="utf-8")
  return 0 if artifact["status"] == "success" else 1


if __name__ == "__main__":
  raise SystemExit(main())
