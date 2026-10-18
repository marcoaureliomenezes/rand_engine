# Contributing to rand-engine

## Set up

From a clean checkout, use Python 3.11 or later and Poetry 2.5.1. The full suite starts
Spark, so install Java 17 and make its `java` executable available on `PATH` (or set
`JAVA_HOME` to its JDK directory). The [compatibility guide](docs/compatibility.md) lists
the tested Spark, Python and platform partitions. Install the test and docs groups:

```bash
poetry install --with test,docs --no-interaction
poetry run pytest -q -p no:cacheprovider tests/
```

The docs site's home page is the README. Before a strict local build, prepare that generated
page with the command for your shell:

```bash
# POSIX shells
cp README.md docs/index.md
poetry run zensical build --strict
```

```powershell
# Windows PowerShell
poetry run python -c "from shutil import copyfile; copyfile('README.md', 'docs/index.md')"
poetry run zensical build --strict
```

`docs/index.md` is generated and ignored. Use the existing tests and strict documentation build
for changes. Before opening a pull request, keep the change focused and include a test or runnable
documentation example when behavior changes.

## Check an adoption path

Run a small, repeatable sample before asking others to try a change:

```bash
poetry run rand-engine list
poetry run rand-engine get-started test-data --out example
poetry run python example/test-data-example.py
poetry run rand-engine get-started agent --out agent-context
```

The first sample creates a DataFrame example; the second writes package-use context for a
project. The existing test suite and docs build verify the broader contracts.

## Ask for help or report a bug

Use [GitHub Issues](https://github.com/marcoaureliomenezes/rand_engine/issues) for questions,
bugs and feature proposals. Include the rand-engine version, Python version and platform, a
minimal synthetic RandSpec or command, the expected and actual result, and a redacted traceback
or reproduction. Do not include credentials, personal data or production data.

For a potential vulnerability, follow [SECURITY.md](https://github.com/marcoaureliomenezes/rand_engine/blob/master/SECURITY.md) instead of opening a public issue.
