---
slug: public-api
title: Public API
tldr: "rand_engine exports DataGenerator, SparkGenerator, RandSpecs and __version__, is typed and ships the rand-engine CLI; every other module is internal."
summary: "The supported import surface is the three names in rand_engine.__all__, the RandEngineError exception family a caller catches, the __version__ string read from installed metadata and the rand-engine console script; the wheel ships only the rand_engine package, typed, with its get-started scaffolds."
tags: [api, package, exceptions]
sources:
  - rand_engine/__init__.py
  - rand_engine/py.typed
  - rand_engine/validators/exceptions.py
  - pyproject.toml
---

## Surface

- `from rand_engine import DataGenerator, SparkGenerator, RandSpecs` is the public surface (`__all__`) — [[data-generator]], [[spark-generator]], [[templates-and-examples]].
- `rand_engine.examples` also exposes `CommonRandSpecs` and `AdvancedRandSpecs`; `RandSpecs` is `CommonRandSpecs`, whose helpers `faker_pool` and `from_schema` build specs ([[templates-and-examples]]).
- Every public class and method of that surface, and of the writer objects `write` and `writeStream` return, carries a numpy-style docstring whose examples run as doctests, Spark ones skipped; the docs site's API reference renders them ([[documentation]]).
- Cores, validators and writers are internal modules, importable but not part of the contract.
- The surface hands back DataFrames, record dicts and files — never a sink client; the caller forwards them to any platform.
- `rand_engine.__version__` is a string read from the installed distribution's metadata, outside `__all__`; where the distribution is not installed, `import rand_engine` still succeeds with a fixed placeholder. `pyproject.toml` holds the one version literal.

```python
rand_engine.__version__  # the installed rand-engine version, else "0.0.0+unknown"
```

- The `rand-engine` console script and `python -m rand_engine` scaffold runnable examples ([[get-started-cli]]).

## Errors

- The library's own exceptions derive from `RandEngineError` (`rand_engine.validators.exceptions`).
- `SpecValidationError` — the spec failed validation at generator construction or in `from_schema`; the validators collect every issue into one error whose footer links the docs site ([[rand-spec-grammar]]).
- `ColumnGenerationError` — a method raised while building a named column.
- `TransformerError` — a per-column transformer raised; the message names the column and the transformer index.
- Plain `RandEngineError` — a missing `.size(n)`, an invalid writer option, an unwritable schema, an anomaly value that cannot keep its column dtype, or a global transformer that changes the row count ([[writers-and-streaming]], [[data-generator]]).
- `FileWriterError` — declared; no module raises it.

## Distribution

- PyPI distribution `rand-engine`, import package `rand_engine`; the wheel holds only `rand_engine/` — the `py.typed` marker and the `cases/*.py.txt` scaffolds included, the agent skill excluded — and declares the `rand-engine` console script.
- The package metadata's `documentation` URL is the docs site, the same URL the validators' error footer names ([[documentation]]).
- Mandatory dependencies are NumPy, pandas and PyArrow. Faker is the optional extra `rand-engine[faker]`; without it only `RandSpecs.faker_pool` fails, with a `RandEngineError` naming the extra.
