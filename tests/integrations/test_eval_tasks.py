"""Eval coverage guard: the usage task folders under evals/tasks equal the catalog's non-quality slugs."""
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
USAGE_SLUGS = {
    "data-generator", "documentation", "generation-methods", "get-started-cli", "pk-fk-constraints",
    "public-api", "rand-spec-grammar", "spark-generator", "templates-and-examples", "writers-and-streaming",
}


def catalog_usage_slugs():
    features = json.loads((ROOT / "specs/memory/product/catalog.json").read_text(encoding="utf-8"))["features"]
    return {f["slug"] for f in features if f["area"] != "quality"}


def usage_folders():
    return {
        p.parent.name for p in (ROOT / "evals/tasks").glob("*/task.toml")
        if tomllib.loads(p.read_text(encoding="utf-8"))["task"]["round"] == "usage"
    }


def test_catalog_non_quality_slugs_are_the_ten_usage_slugs():
    assert catalog_usage_slugs() == USAGE_SLUGS


def test_usage_task_folders_cover_the_catalog():
    found = usage_folders()
    expected = catalog_usage_slugs()
    assert found == expected, f"missing: {sorted(expected - found)}, extra: {sorted(found - expected)}"
