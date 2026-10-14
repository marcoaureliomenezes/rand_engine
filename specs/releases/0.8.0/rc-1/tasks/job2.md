# Job 2 — FR2.1 dependency pins, docs and lint groups, version 0.8.0

**Wave:** 1 · **Waits on:** —

Dev-loop dependencies only: no runtime dependency changes (invariant 10). One writer for `poetry.lock` in the rc.

- pyspark 3.5.8 fits `^3.5.0` (lock bump); setuptools 83.0.0 does not fit `^78.1.1` (manifest line changes).
- Zensical is pinned exactly in a docs group and built only in the docs workflow; ruff goes in the test group; `[tool.ruff]` selects `D` with `convention = "numpy"`.
- Version `0.8.0` (SPEC §4 Terms: the new public surface makes this a minor).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC2.1 | `pyproject.toml`, `poetry.lock` | pyspark lock bump to >= 3.5.8; setuptools constraint `^83.0.0` and lock >= 83.0.0; no test (dependency pins; evidence = lock diff and Dependabot alerts #17/#18 reading fixed after push). Owner test: none, the CI matrix on the bumped lock |
| J2.T2 | jr | AC3.3, AC5.1 | `pyproject.toml`, `poetry.lock` | ruff in the test group; docs group with zensical (exact pin) and mkdocstrings-python; `[tool.ruff]` numpy `D` config; `version = "0.8.0"`. No test (dependency and config lines; the verify: lines of J5.T6 and the docs workflow exercise them). Owner test: none |
