import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


PYTHON_ROWS = 100_000
SPARK_ROWS = 1_000_000
SPARK_PARTITIONS = 8
SAMPLE_ORDER = ["rand-engine", "faker", "faker", "rand-engine", "rand-engine", "faker"]


def comparison():
  return importlib.import_module("benchmarks.comparison")


def python_records():
  return [{"value": 42, "tier": "bronze", "active": True}] * PYTHON_ROWS


def spark_observation():
  return {
    "count": SPARK_ROWS,
    "partitions": SPARK_PARTITIONS,
    "schema": [
      ("ordinal", "long", False),
      ("value", "int", False),
      ("tier", "string", False),
    ],
    "ordinal": {"minimum": 0, "maximum": SPARK_ROWS - 1, "distinct_count": SPARK_ROWS},
    "value": {"minimum": 0, "maximum": 999_999},
    "tier": {"values": ["bronze", "silver", "gold"]},
    "nulls": {"ordinal": 0, "value": 0, "tier": 0},
    "aggregate": {"count": SPARK_ROWS, "sum": 123},
    "physical_plan": "HashAggregate(xxhash64(ordinal, value, tier))",
  }


class StepClock:
  def __init__(self):
    self.calls = 0

  def __call__(self):
    self.calls += 1
    return float(self.calls)


class TestPythonContract(unittest.TestCase):
  def test_python_validator_accepts_exactly_materialized_three_field_records(self):
    comparison().validate_python_records(python_records())

  def test_python_validator_rejects_wrong_shape_types_and_domains(self):
    invalid = [
      {"value": True, "tier": "bronze", "active": True},
      {"value": None, "tier": "bronze", "active": True},
      {"value": 1_000_000, "tier": "bronze", "active": True},
      {"value": 42, "tier": "platinum", "active": True},
      {"value": 42, "tier": "bronze", "active": 1},
      {"value": 42, "tier": "bronze"},
      {"value": 42, "tier": "bronze", "active": True, "extra": "no"},
    ]
    for record in invalid:
      with self.subTest(record=record):
        records = python_records()
        records[0] = record
        with self.assertRaises(ValueError):
          comparison().validate_python_records(records)

  def test_python_validator_rejects_a_non_materialized_or_wrong_row_count_result(self):
    with self.assertRaises(ValueError):
      comparison().validate_python_records(iter(python_records()))
    with self.assertRaises(ValueError):
      comparison().validate_python_records(python_records()[:-1])


class TestSparkContract(unittest.TestCase):
  def test_spark_validator_requires_full_evaluation_and_exact_workload_observation(self):
    comparison().validate_spark_observation(spark_observation())

  def test_spark_validator_accepts_nullable_schema_when_observed_payload_has_no_nulls(self):
    observation = spark_observation()
    observation["schema"] = [
      ("ordinal", "long", True),
      ("value", "int", True),
      ("tier", "string", True),
    ]
    comparison().validate_spark_observation(observation)

  def test_spark_validator_rejects_missing_payload_or_contract_evidence(self):
    cases = []
    for key, value in [
        ("count", SPARK_ROWS - 1),
        ("partitions", SPARK_PARTITIONS - 1),
        ("schema", [("ordinal", "long", False), ("value", "long", False)]),
        ("ordinal", {"minimum": 0, "maximum": SPARK_ROWS - 1, "distinct_count": SPARK_ROWS - 1}),
        ("value", {"minimum": 0, "maximum": 1_000_000}),
        ("tier", {"values": ["bronze", "silver"]}),
        ("nulls", {"ordinal": 0, "value": 1, "tier": 0}),
        ("aggregate", {"count": SPARK_ROWS}),
        ("physical_plan", "HashAggregate(xxhash64(ordinal, value))"),
        ("physical_plan", "HashAggregate(xxhash64(ordinal, value)) Scan [ordinal, value, tier]"),
    ]:
      observation = spark_observation()
      observation[key] = value
      cases.append(observation)
    for observation in cases:
      with self.subTest(observation=observation):
        with self.assertRaises(ValueError):
          comparison().validate_spark_observation(observation)


class TestComparisonArtifact(unittest.TestCase):
  def test_spark_validator_callback_populates_observation_before_validation(self):
    records = python_records()
    callback_calls = []

    def python_factory():
      return records

    def spark_factory():
      observation = {}

      def validate():
        callback_calls.append(observation)
        observation.update(spark_observation())

      return {"observation": observation, "validator": validate}

    comparison().run_comparison(
      {
        "python": {"rand-engine": python_factory, "faker": python_factory},
        "spark": {"rand-engine": spark_factory, "dbldatagen": spark_factory},
      },
      provenance={"rand_engine": {"version": "0.8.0", "editable": False}},
    )

    self.assertEqual(len(callback_calls), 8)

  def test_runner_warms_each_side_once_then_keeps_ab_ba_ab_raw_samples_and_medians(self):
    calls = []
    records = python_records()
    spark = spark_observation()

    def factory(workload, side, result):
      def run():
        calls.append((workload, side))
        return result
      return run

    factories = {
      "python": {
        "rand-engine": factory("python", "rand-engine", records),
        "faker": factory("python", "faker", records),
      },
      "spark": {
        "rand-engine": factory("spark", "rand-engine", spark),
        "dbldatagen": factory("spark", "dbldatagen", spark),
      },
    }
    clock = StepClock()
    artifact = comparison().run_comparison(
      factories,
      clock=clock,
      provenance={"rand_engine": {"version": "0.8.0", "editable": False}},
    )

    expected_python = [("python", side) for side in ["rand-engine", "faker"] + SAMPLE_ORDER]
    expected_spark = [("spark", side) for side in ["rand-engine", "dbldatagen", "rand-engine", "dbldatagen", "dbldatagen", "rand-engine", "rand-engine", "dbldatagen"]]
    self.assertEqual(calls, expected_python + expected_spark)
    self.assertEqual(artifact["workloads"]["python"]["warmups"], ["rand-engine", "faker"])
    self.assertEqual(artifact["workloads"]["spark"]["warmups"], ["rand-engine", "dbldatagen"])
    self.assertEqual(artifact["workloads"]["python"]["sample_order"], SAMPLE_ORDER)
    self.assertEqual(artifact["workloads"]["spark"]["sample_order"], ["rand-engine", "dbldatagen", "dbldatagen", "rand-engine", "rand-engine", "dbldatagen"])
    self.assertEqual(artifact["workloads"]["python"]["samples"], {"rand-engine": [1.0, 1.0, 1.0], "faker": [1.0, 1.0, 1.0]})
    self.assertEqual(artifact["workloads"]["python"]["medians"], {"rand-engine": 1.0, "faker": 1.0})
    self.assertEqual(clock.calls, 24)

  def test_artifact_requires_provenance_validation_schemas_and_physical_plans_without_a_ranking(self):
    artifact = {
      "artifact_version": 1,
      "status": "success",
      "provenance": {
        "rand_engine": {"version": "0.8.0", "editable": False, "wheel_sha256": "a" * 64},
        "pip_report": "pip-report.json",
        "harness_sha": "b" * 40,
        "python": "3.12",
        "java": "17",
        "spark": "3.5.8",
        "os": "ubuntu",
        "runner": "ubuntu-latest",
        "versions": {"Faker": "28.4.1", "dbldatagen": "0.4.0.post1", "pyspark": "3.5.8"},
      },
      "workloads": {
        "python": {
          "definition": {"rows": PYTHON_ROWS, "fields": ["value", "tier", "active"]},
          "warmups": ["rand-engine", "faker"],
          "sample_order": SAMPLE_ORDER,
          "samples": {"rand-engine": [1.0, 2.0, 3.0], "faker": [2.0, 3.0, 4.0]},
          "medians": {"rand-engine": 2.0, "faker": 3.0},
          "validation": {"status": "passed"},
          "setup_seconds": 4.0,
          "validation_seconds": 5.0,
        },
        "spark": {
          "definition": {"rows": SPARK_ROWS, "partitions": SPARK_PARTITIONS, "fields": ["ordinal", "value", "tier"]},
          "warmups": ["rand-engine", "dbldatagen"],
          "sample_order": ["rand-engine", "dbldatagen", "dbldatagen", "rand-engine", "rand-engine", "dbldatagen"],
          "samples": {"rand-engine": [1.0, 2.0, 3.0], "dbldatagen": [2.0, 3.0, 4.0]},
          "medians": {"rand-engine": 2.0, "dbldatagen": 3.0},
          "validation": {"status": "passed"},
          "schemas": {"rand-engine": spark_observation()["schema"], "dbldatagen": spark_observation()["schema"]},
          "physical_plans": {"rand-engine": spark_observation()["physical_plan"], "dbldatagen": spark_observation()["physical_plan"]},
          "setup_seconds": 4.0,
          "validation_seconds": 5.0,
        },
      },
    }
    comparison().validate_artifact(artifact)
    versionless = dict(artifact)
    versionless.pop("artifact_version")
    with self.assertRaises(ValueError):
      comparison().validate_artifact(versionless)
    for forbidden in ("winner", "score", "threshold", "ranking"):
      with self.subTest(forbidden=forbidden):
        rejected = {**artifact, forbidden: "no"}
        with self.assertRaises(ValueError):
          comparison().validate_artifact(rejected)


class TestControlledFailure(unittest.TestCase):
  def test_main_writes_controlled_failure_artifacts_and_returns_nonzero(self):
    class FailingBuilder:
      def master(self, _master):
        return self

      def appName(self, _name):
        return self

      def config(self, _key, _value):
        return self

      def getOrCreate(self):
        raise RuntimeError("setup failed")

    fake_sql = types.ModuleType("pyspark.sql")
    fake_sql.SparkSession = type("SparkSession", (), {"builder": FailingBuilder()})
    fake_pyspark = types.ModuleType("pyspark")
    fake_pyspark.sql = fake_sql
    with tempfile.TemporaryDirectory() as temporary:
      output = Path(temporary)
      original_modules = {name: sys.modules.get(name) for name in ("pyspark", "pyspark.sql")}
      try:
        sys.modules.update({"pyspark": fake_pyspark, "pyspark.sql": fake_sql})
        result = comparison().main([
          "--output-dir", str(output),
          "--pip-report", str(output / "pip-report.json"),
          "--wheel-sha256", "a" * 64,
          "--harness-sha", "b" * 40,
        ])
      finally:
        for name, module in original_modules.items():
          if module is None:
            sys.modules.pop(name, None)
          else:
            sys.modules[name] = module

      self.assertNotEqual(result, 0)
      for filename in ("comparison.json", "comparison.md"):
        self.assertTrue((output / filename).is_file())
      artifact = json.loads((output / "comparison.json").read_text(encoding="utf-8"))
      self.assertEqual(artifact["status"], "controlled_failure")
      self.assertEqual(artifact["errors"], ["RuntimeError: setup failed"])
