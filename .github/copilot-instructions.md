# Rand Engine - AI Agent Instructions

## Project Overview
`rand-engine` is a Python library for generating random test data using numpy, pandas, and faker. It's built around a declarative spec-based architecture where data generation is configured via metadata dictionaries rather than imperative code.

## Core Architecture

### 1. Three-Layer Design
- **Core Layer** (`rand_engine/core/`): Stateless generator classes - `NumericCore`, `DistinctCore`, `DatetimeCore`. ALL methods are `@classmethod` and use numpy for performance.
- **Main Layer** (`rand_engine/main/`): Orchestration - `RandGenerator` (spec → DataFrame), `FileWriter` (fluent API for exports), `StreamHandle` (generator for streaming).
- **Integration Layer** (`rand_engine/spark/`): Optional PySpark extensions (lazy imports to avoid hard dependency).

### 2. Random Spec Pattern
Data generation is driven by declarative specs:
```python
spec = {
    "column_name": {
        "method": NumericCore.gen_ints,      # Core class method
        "parms": {"min": 0, "max": 100}      # Kwargs passed to method
    }
}
```
**Critical:** Use `parms` (not `params`) - this is the established convention. See `tests/fixtures/fixtures_random_spec.py` for real examples.

### 3. Splitable Pattern for Correlated Columns
When multiple columns are correlated, generate as single string then split:
```python
{
    "campos_correlacionados": {
        "method": DistinctCore.gen_distincts,
        "splitable": True,                    # Enables splitting
        "cols": ["category", "type"],         # Target column names
        "sep": ";",                           # Delimiter
        "parms": {"distinct": ["A;X", "B;Y"]} # Pre-joined values
    }
}
```
See `RandGenerator.handle_splitable()` for implementation.

## Code Conventions

### Naming Patterns
- Core classes: `{Purpose}Core` (NumericCore, DatetimeCore)
- Generators: `{Purpose}Generator` (RandGenerator, CDCGenerator)
- Handlers: `{Purpose}Handler` (LocalFSHandler, DBFSHandler)
- Utils: `{Purpose}Utils` (DistinctUtils, FSUtils)

### Method Signatures
- Core methods: Return `np.ndarray`, accept `size: int` as first param
- All optional params have defaults (e.g., `round: int = 2`)
- Use type hints consistently: `Optional[Callable]`, `List[str]`, `Dict[str, Any]`

### Seed Management
Seeds are applied at the `RandGenerator` level, NOT in Core classes:
```python
generator = RandGenerator(spec, seed=42)  # ✓ Correct
np.random.seed(42)                        # For direct Core usage
```

## Developer Workflows

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_1_core.py -v

# Tests use fixtures from tests/fixtures/
```

### Release Process
**DO NOT manually update version in pyproject.toml**. Version is managed by git tags:
```bash
git tag 0.4.6               # Semantic version
git push origin --tags      # Triggers GitHub Actions
```
Workflow automatically: checks PyPI version, builds package, publishes to PyPI, creates GitHub release.

### File Writer Fluent API
Chain methods to configure exports:
```python
generator.write()
    .mode("overwrite")         # or "append"
    .format("parquet")         # csv, parquet, json
    .option("compression", "gzip")
    .load("/path/to/output")
```

## Integration Points

### PySpark (Optional Dependency)
- Import PySpark types only when needed (lazy imports)
- `RandGenerator.generate_spark_df()` wraps pandas generation
- Spark extensions in `rand_engine/spark/` use monkey patching

### File Formats
- **CSV**: Uses pandas `to_csv()`, supports compression via options
- **JSON**: Uses `to_json()` with `force_ascii=False` for Unicode, `indent=2` for arrays
- **Parquet**: Uses fastparquet, engine set via options

### Faker Integration
For realistic data (names, addresses, jobs), faker is used in test fixtures:
```python
fake = faker.Faker(locale="pt_BR")
fake.seed_instance(42)  # Instance-level seed
jobs = [fake.job() for _ in range(100)]
```

## Common Patterns

### Proportional Distributions
Use `DistinctUtils.handle_distincts_lvl_1()` for weighted sampling:
```python
{"Junior": 70, "Pleno": 35, "Senior": 12}  # Weights, not exact counts
```

### Complex Patterns (e.g., IP addresses)
Use `gen_complex_distincts()` with template replacement:
```python
{
    "method": DistinctCore.gen_complex_distincts,
    "parms": {
        "pattern": "x.x.x.x",
        "replacement": "x",
        "templates": [
            {"method": DistinctCore.gen_distincts, "parms": {"distinct": ["172", "192"]}},
            {"method": NumericCore.gen_ints, "parms": {"min": 0, "max": 255}},
            # ... one template per 'x'
        ]
    }
}
```

### Streaming Generation
For continuous data generation:
```python
for record in generator.stream_dict(min_throughput=1, max_throughput=10):
    # Each record gets a timestamp_created field
    process(record)
```

## Key Files Reference
- `rand_engine/main/data_generator.py` - Orchestration entry point
- `tests/fixtures/fixtures_random_spec.py` - Real-world spec examples
- `rand_engine/core/distinct_utils.py` - Proportional/correlated data helpers
- `.github/workflows/test_build_and_publish.yml` - CI/CD pipeline

## Testing Philosophy
- Use fixtures in `tests/fixtures/` for complex specs
- Tests validate output shape, types, and ranges, NOT exact values (randomness)
- Seed tests when reproducibility is required
- Core tests in `tests/test_1_core.py` are unit-level; integration tests use `RandGenerator`

## Avoid Common Pitfalls
- ❌ Don't instantiate Core classes (they're all classmethods)
- ❌ Don't use `params` in specs (it's `parms`)
- ❌ Don't update pyproject.toml version manually (use git tags)
- ❌ Don't import PySpark globally (lazy load in methods)
- ❌ Don't forget `force_ascii=False` when writing JSON with Unicode
