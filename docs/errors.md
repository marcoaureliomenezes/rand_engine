---
description: Exception reference covering which library errors come from construction and which from generation, the wrapper errors, and a catch example.
---
# Errors

Import errors from `rand_engine.validators.exceptions` and catch
`RandEngineError` when one recovery path covers the library's errors. More
specific classes identify where the operation failed.

- `SpecValidationError` reports a fault that static validation or the one-row
  check finds, at construction, before generation starts.
- `RandEngineError` is raised at generation for size faults, a foreign key with
  no eligible parent, a pk outside its domain or past int64, a global transformer
  that changes the row count or drops a modifier column, anomaly values that
  cannot keep their dtype after embedded transformers, and the writers.
- `ColumnGenerationError` wraps the method call, conversion and multi-column unpack.
- `TransformerError` wraps an exception from a per-column transformer and names
  its column and position.
- `FileWriterError` is declared for callers that need the exception taxonomy.

```python
from rand_engine import DataGenerator
from rand_engine.validators.exceptions import RandEngineError, SpecValidationError

bad_spec = {"age": {"method": "not-a-method", "kwargs": {}}}
try:
    DataGenerator(bad_spec)
except SpecValidationError as error:
    assert "age" in str(error)
else:
    raise AssertionError("expected SpecValidationError")

spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
try:
    DataGenerator(spec).size(1).write.format("csv").option("engine", "fast").save("out/ages.csv")
except RandEngineError as error:
    assert "engine" in str(error)
else:
    raise AssertionError("expected RandEngineError")
```

## Exception reference

::: rand_engine.validators.exceptions.RandEngineError

::: rand_engine.validators.exceptions.SpecValidationError
    options:
      show_docstring_description: false
      show_docstring_examples: false
      show_source: false

::: rand_engine.validators.exceptions.ColumnGenerationError
    options:
      show_docstring_description: false
      show_docstring_examples: false
      show_source: false

::: rand_engine.validators.exceptions.TransformerError
    options:
      show_docstring_description: false
      show_docstring_examples: false
      show_source: false

::: rand_engine.validators.exceptions.FileWriterError
    options:
      show_docstring_description: false
      show_docstring_examples: false
      show_source: false
