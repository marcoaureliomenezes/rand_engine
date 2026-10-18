# Errors

Import errors from `rand_engine.validators.exceptions` and catch
`RandEngineError` when one recovery path covers the library's errors. More
specific classes identify where the operation failed.

- `SpecValidationError` reports RandSpec problems at construction or in a
  builder, before generation starts.
- `ColumnGenerationError` wraps an exception raised while a validated generator
  method builds a named column.
- `TransformerError` wraps an exception from a per-column transformer and names
  its column and position.
- `RandEngineError` also covers output setup and writer failures such as a
  missing size, invalid writer option, schema mismatch or incompatible modifier.
- `FileWriterError` is declared for callers that need the exception taxonomy,
  but no current library path raises it.

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
