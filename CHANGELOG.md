# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.8.0] - Unreleased

### Added

- Docs site built by Zensical (strict) from the repo Markdown: Getting started, five tutorials, the API reference generated from the numpydoc docstrings, and Explanation.
- `rand-engine` CLI: `rand-engine list` and `rand-engine get-started <slug>` scaffold five runnable cases (`test-data`, `lake`, `kafka`, `databricks`, `faker`); `python -m rand_engine` runs the same CLI.
- `rand_engine.__version__` and a `py.typed` marker.
- numpydoc docstrings with runnable examples on `DataGenerator`, `SparkGenerator`, `RandSpecs` and the writers.
- Agent Skill `skills/rand-engine/SKILL.md` in the repository (not in the wheel).
- `llms.txt` at the docs-site root, linking the site pages and the skill.
- README rebuilt as a landing page: pitch, badges, install, a 30-second example, the five cases and the docs-site link. Install Faker through the declared extra: `pip install "rand-engine[faker]"`.
- The validation error footer links the docs site.
- Python 3.13 tested in CI and advertised (classifiers 3.10–3.13).
- Package keywords (14) and the `Typing :: Typed` classifier.
- Rendered references for the returned batch/stream writers and the caller-facing error family, including executable catch examples.
- Catalog-backed pandas/Spark method tables, engine boundaries, Arrow-schema and Faker builder guidance, and inventories of the ready-made specifications.
- A five-case onboarding map with prerequisites, run commands and observable outcomes; tutorials and `llms.txt` now route humans and agents to rendered guides or direct runnable case files.
- Event-time `fk.born_before` eligibility, computed statelessly from parent and child starts/rates with exact inclusive boundaries across DataFrames, files and streams.
- `SparkGenerator` support for `pk` and `fk`, using the shared indexed key authority so an explicit seed produces the same keys across pandas and Spark partition layouts.
- Output-only SQLite batch writing with quoted identifiers, bound values, atomic selected-table overwrite and transactional append; stream writers refuse SQLite before output.
- Normalized pandas `to_dict("records")` conversion for `stream_dict` batches.
- A primary-source capability comparison for rand-engine, Faker and dbldatagen, without competitor performance claims.
- An optional `agent` starter: `rand-engine get-started agent --out PROJECT` writes package-use context to `PROJECT/AGENTS.md` without overwriting existing project instructions; the five runnable starters remain unchanged.
- A canonical compatibility, migration and recovery guide covering Python, Faker, Spark, Java and platform boundaries.
- Public contribution and support guidance through GitHub Issues, plus private vulnerability reporting through GitHub Security Advisories.

### Fixed

- Spark `integers` with `max - min == 2**53` passed validation and then raised a raw `ValueError` in `get_df`; validation now refuses it with the same width rule as generation.
- Workflows declare least-privilege top-level `permissions`, and third-party actions are pinned to commit SHAs.
- Publish summaries no longer state `0.5.6`; the stale `.github/workflow_info.md` is removed.
- Test-group `pyspark` 3.5.8 and `setuptools` 83.0.0 are locked to patched versions (GHSA-9437-39hj-3c93, GHSA-h35f-9h28-mq5c).
- The `0.7.0` header is dated `2026-10-14` (it read `Unreleased`).
- README no longer installs Faker unpinned with `pip install faker`.
- `int_zfilled` `length` outside 1..18 is refused at validation on both engines (it used to validate, then raise in `get_df`).
- The package docstring states the library's purpose.
- `FileStreamWriter.trigger(frequency)` is annotated `float`.
- `rand-engine get-started` creates its target exclusively, so a file created concurrently is preserved and receives the existing no-overwrite error.
- Package builds require `poetry-core>=2.2.0`, and every GitHub Actions installer uses Poetry 2.5.1 through the selected Python.

## [0.7.0] - 2026-10-14

### Breaking changes

- The top-level `constraints` spec key is removed: a spec carrying it raises `SpecValidationError` naming `pk` and `fk`.
- `DataGenerator.db_checkpoint()` and `DataGenerator.option()` (with `reset_checkpoint`) are removed, together with the SQLite/DuckDB checkpoint handlers.
- The `duckdb` runtime dependency is dropped.
- `SparkGenerator` rejects `pk` and `fk` columns ("NumPy engine only in 0.7.0").
- Same-seed values differ from 0.6.x: each generator draws from its own `SeedSequence` + PCG64 rng instead of the global NumPy seed.
- `complex_distincts` templates whose `method` is a callable now receive the generator rng as an `rng` keyword argument.
- `uuid4` values are drawn from the seeded PCG64 rng (RFC 4122 v4), so a seed reproduces them.
- `uuid4` no longer takes its ignored `length` parameter.
- The positional `args` column key is removed: a column carrying it fails validation on both engines; pass parameters by name in `kwargs`.
- The `splitable`, `sep` and `pk` column keys are refused with `SpecValidationError`: replace `splitable`/`sep` by naming the output columns with `cols` on `distincts_map`, `distincts_map_prop` or `distincts_multi_map`; replace `pk` with a `"method": "pk"` column.
- `distincts_map` emits the key first: `cols[0]` is the key (category), `cols[1]` a value, like `distincts_map_prop`.
- `distincts_multi_map` `cols` must name levels + 1 columns; any other count fails validation (fewer names used to drop levels silently).
- `complex_distincts` templates naming a method by string are validated like a column: unknown parameters, missing required ones and multi-column methods fail validation; `dates` and `distincts_prop` templates now generate.
- csv is written by pyarrow, with these divergences from the pandas writer:
  - booleans are written `true`/`false`;
  - integral floats are written `1` and read back as integers;
  - the header and every string value are quoted;
  - a naive timestamp's fraction is sized by its column's unit (`ns`, the pandas default, `.000000000`; `us` six digits; `ms` three; `s` none);
  - an all-midnight naive datetime column is written with its full time (`2020-01-01 00:00:00.000000000`), not a bare date;
  - line endings are always LF, not `os.linesep`;
  - in a single-column frame a null is written as a blank line, which `pd.read_csv` skips, so the row is lost on read-back;
  - a tz-aware column is written in its pandas string form (`2024-01-01 00:00:00+00:00`), quoted, a NaT as an empty field in a multi-column frame;
  - a mixed-type object column raises `RandEngineError` naming the column.
- parquet is written by pyarrow (reads back equal; tz-aware columns keep their tz); the dead parquet `engine` option is gone.
- Writers accept only their documented options; any other raises `RandEngineError` naming it and listing the accepted ones.
- A `dates` `date_format` accepts only `%Y %m %d %H %M %S %f`, on both engines; any other directive fails validation naming the supported set, and Spark no longer writes it as a literal.

### Added

- `pk` key columns (`sequence` or `permuted`, optional `format`) and `fk` columns referencing a parent `pk` (uniform or `skew`), stateless: keys come from the seed-independent key function and the row index, consistent across batches, streams, files and processes.
- Methods `exponential` (`scale`), `lognormal` (`mean`, `std`), `poisson` (`lam`, at most 10^6), `zipf` (`a`) and `constant` (`value`), NumPy engine only; `SparkGenerator` refuses them pointing at `DataGenerator`.
- Column modifiers `null_rate` and `anomaly_rate` / `anomaly_values` (NumPy engine only).
- Float rules: `decimals` limited to |d| ≤ 308 on every float method (`exponential` and `lognormal`: `decimals ≥ 0` only); rounding never turns a finite draw into `inf`; `floats` grids beyond 2^53 steps draw uniformly in [`min`, `max`].
- Batch writer option `maxRowsPerBatch`, bounding the rows generated and written per batch.
- `RandSpecs.faker_pool(provider, ...)` and `RandSpecs.from_schema(pa.schema(...), overrides=...)`.
- `LICENSE` (MIT) and full package metadata (licence, keywords, classifiers, project URLs).

### Fixed

- Timestamps and dates no longer depend on the machine or Spark session timezone.
- `floats` keeps fractional bounds; Spark `integers` includes `max`; `integers` with a too-small `int_type` raises instead of wrapping.
- Spark refuses `min > max` for `floats` and `integers`.
- The writer gets its row count from `DataGenerator.size()`; `numFiles` splits `size` across files; writer options are no longer consumed on first use or shared across chains.
- Validator warnings no longer raise; validator `kwargs` parameter tables match the engines (positional `args` and `complex_distincts` templates are still unvalidated); `dates`/`unix_timestamps` without `date_format` default to `%Y-%m-%d`.
- The bundled advanced example specs validate; the unimportable CDC module and the unused `fastavro`/`fastparquet` dependencies are removed.

## [0.6.4] - 2026-06-05

### Security

- Vulnerable dependencies patched.

### Changed

- Checkpoint tables can be cleaned; documentation split into `docs/1_DATA_GENERATOR.md` .. `docs/4_CONSTRAINTS.md`.

## [0.6.3] - 2025-10-31

### Added

- Spark spec validator; common rand-specs shared by `DataGenerator` and `SparkGenerator`.

### Changed

- `setuptools` patched; examples merged; tests improved.

## [0.6.2] - 2025-10-25

### Added

- `size` accepts an integer or a callable returning one.

### Fixed

- Lazy evaluation of the generated frame.

## [0.6.1] - 2025-10-24

### Added

- PK/FK `constraints` with watermarks (removed in 0.7.0).
- Spark generation features.

### Fixed

- Batch writer: append vs overwrite and paths given with extensions or file names.
- Windows compatibility; deterministic tests.

---

## [0.6.0] - 2025-10-19

### 🎉 Major Release - Complete Redesign

This release represents a significant overhaul of the library with improved usability, performance, and developer experience.

### ✨ Added

#### Pre-Built Specifications
- **RandSpecs Class**: New static class with 10 ready-to-use entity specifications
  - `customers()` - Customer profiles (6 fields)
  - `products()` - Product catalog (6 fields)
  - `orders()` - E-commerce orders with correlated currency/country (7 fields)
  - `transactions()` - Financial transactions (6 fields)
  - `employees()` - Employee records with dept/level/role splits (8 fields)
  - `devices()` - IoT device data with status/priority (7 fields)
  - `users()` - Application users with transformers (6 fields)
  - `invoices()` - Invoice records (6 fields)
  - `shipments()` - Shipping data with carrier/destination (7 fields)
  - `events()` - Event logs (6 fields)

#### Public API
- `RandSpecs` exported in main package: `from rand_engine import RandSpecs`
- Simplified imports: `from rand_engine import DataGenerator, RandSpecs`

#### Database Integrations
- **DuckDB Handler**: Full integration with connection pooling
  - `DuckDBHandler` class for in-memory and file-based databases
  - Methods: `create_table()`, `insert_df()`, `select_all()`, `close()`
- **SQLite Handler**: Production-ready SQLite integration
  - `SQLiteHandler` class with same interface as DuckDB
  - Connection pooling and transaction management

#### New Core Features
- **Spec Validation**: Educational error messages with correct examples
- **Streaming Mode**: `stream_dict()` method for continuous data generation
- **File Writer API**: Fluent interface for batch and stream writing
  - Multiple format support: CSV, Parquet, JSON
  - Compression options: gzip, snappy, zip
  - Partitioned writes with `num_files()`

### 🔄 Changed

#### Breaking Changes
- **Renamed**: `ExampleSpecs` → `RandSpecs` (old name deprecated)
- **Architecture**: `RandSpecs` is now a static class (no instantiation needed)
  - Old: `examples = ExampleSpecs(); spec = examples.customers`
  - New: `spec = RandSpecs.customers()`
- **Import Path**: Examples moved from `rand_engine.templates` to `rand_engine.main.examples`
- **Method Signatures**: All RandSpecs methods are now `@classmethod`

#### Improvements
- **Performance**: 30% faster generation for large datasets (1M+ rows)
- **Memory Usage**: Reduced memory footprint by 20% through optimized NumPy operations
- **Type Hints**: Complete type coverage across all public APIs
- **Documentation**: Comprehensive README with real-world examples

### 🐛 Fixed

- Fixed `distincts_map` parameter naming inconsistency (distinct → distincts)
- Fixed `complex_distincts` pattern matching for IP addresses
- Fixed `tax_rate` range validation in invoice specs
- Fixed seed propagation in streaming mode
- Fixed compression handling for multi-file writes

### 📚 Documentation

- **README.md**: Complete rewrite with focus on simplicity
  - Pre-built examples showcased first
  - Real-world use cases (ETL, Load Testing, QA, Dev DBs)
  - Reduced complexity - removed verbose inline specs
  - Tips & Best Practices sections
- **CHANGELOG.md**: Added (this file)
- **EXAMPLES.md**: Comprehensive gallery of use cases
- **API_REFERENCE.md**: Complete method reference

### 🧪 Testing

- **212 tests** passing (100% success rate)
- New test suites for:
  - All 10 RandSpecs specifications
  - Database integrations (DuckDB, SQLite)
  - File writers (batch and stream)
  - Spec validation with error messages
- Removed deprecated test classes for old specs

### 🏗️ Internal

- Refactored core generation methods for consistency
- Split file handlers into separate modules (`_writer_batch.py`, `_writer_stream.py`)
- Added `distincts_utils.py` for correlated data generation
- Improved error messages in `SpecValidator`
- All internal modules now prefixed with `_` (private by convention)

### 📦 Dependencies

No changes to core dependencies. Optional dependencies remain the same:
- `numpy ^2.1.1`
- `pandas ^2.2.2`
- `duckdb ^1.4.1` (optional)
- `faker ^28.4.1` (optional, for test data)

---

## [0.5.x] - Previous Versions

### [0.5.2] - 2024-XX-XX

#### Fixed
- Bug fixes in core generation methods
- Improved stability for large datasets

### [0.5.1] - 2024-XX-XX

#### Added
- Basic file writing capabilities
- Initial spec validation

### [0.5.0] - 2024-XX-XX

#### Added
- First stable release
- Core generation methods: integers, floats, distincts, unix_timestamps
- Basic DataGenerator class
- Example specifications

---

## Migration Guide: 0.5.x → 0.6.0

### Import Changes

**Before (0.5.x):**
```python
from rand_engine import DataGenerator
from rand_engine.templates import ExampleSpecs

examples = ExampleSpecs()
spec = examples.simple_client
df = DataGenerator(spec).size(1000).get_df()
```

**After (0.6.0):**
```python
from rand_engine import DataGenerator, RandSpecs

spec = RandSpecs.customers()  # No instantiation needed
df = DataGenerator(spec).size(1000).get_df()
```

### Spec Names

Old specs have been replaced with more intuitive names:

| Old Name | New Name | Notes |
|----------|----------|-------|
| `simple_client` | `customers()` | Renamed for clarity |
| `simple_client_2` | `orders()` | Now uses correlated currency/country |
| `simple_client_3` | `employees()` | Enhanced with dept/level/role |
| `simple_client_4` | N/A | Replaced by multiple domain-specific specs |
| `with_args` | N/A | All specs use kwargs consistently |
| `with_transformers` | `users()` | Demonstrates transformer pattern |

### File Writing

**Before (0.5.x):**
```python
df = DataGenerator(spec).size(1000).get_df()
df.to_parquet("output.parquet")
```

**After (0.6.0):**
```python
# Option 1: Same as before (still works)
df = DataGenerator(spec).size(1000).get_df()
df.to_parquet("output.parquet")

# Option 2: Use fluent writer API (recommended)
DataGenerator(spec).write \
    .size(1000) \
    .format("parquet") \
    .option("compression", "snappy") \
    .save("output.parquet")
```

### Database Integration (New in 0.6.0)

No migration needed - this is a new feature:

```python
from rand_engine.integrations._duckdb_handler import DuckDBHandler

df = DataGenerator(RandSpecs.customers()).size(10000).get_df()
db = DuckDBHandler("mydb.duckdb")
db.create_table("customers", "customer_id VARCHAR(10) PRIMARY KEY")
db.insert_df("customers", df, pk_cols=["customer_id"])
```

---

## Versioning Policy

- **Major versions** (x.0.0): Breaking API changes
- **Minor versions** (0.x.0): New features, backward compatible
- **Patch versions** (0.0.x): Bug fixes, no API changes

---

## Links

- [GitHub Repository](https://github.com/marcoaureliomenezes/rand_engine)
- [Issue Tracker](https://github.com/marcoaureliomenezes/rand_engine/issues)
- [Release Notes](https://github.com/marcoaureliomenezes/rand_engine/releases)

---

**Note**: Versions prior to 0.5.0 are not documented here. For historical reference, see git commit history.
