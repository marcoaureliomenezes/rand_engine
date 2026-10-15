# Job 4 — FR3.1 and FR3.2 package metadata: __version__, py.typed, package skeleton

**Wave:** 2 · **Waits on:** Job 2

- `__version__` comes from `importlib.metadata.version("rand-engine")` with a short fallback so `import rand_engine` never fails from a source tree (`verify:` installs with `--no-root`); a wheel test proves the real value (ruling 3). It stays out of `__all__` (invariant 1).
- Four package directories are namespace packages today (`main`, `file_handlers`, `core`, `utils`): the docs API reference cannot build without `__init__.py` there. They are empty files.
- Consumers: `test_every_shipped_module_imports` (`rglob`), `__all__` asserts stay green; three workflow summaries print `__version__` and become true.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J4.T1 | sr | AC3.1, AC3.2, AC5.9 | `tests/integrations/test_public_api.py` | RED: build the wheel; the four `__init__.py` exist (mkdocstrings resolves the package); `__version__` equals the version in the extracted wheel's METADATA and pyproject; wheel holds `rand_engine/py.typed` no `skills/` path and no module outside `rand_engine/`; `__all__` unchanged. Owner: tests/integrations/test_public_api.py |
| J4.T2 | jr | AC3.1, AC3.2, AC5.9 | `rand_engine/__init__.py`, `rand_engine/main/__init__.py`, `rand_engine/file_handlers/__init__.py`, `rand_engine/core/__init__.py`, `rand_engine/utils/__init__.py`, `rand_engine/py.typed`, `tests/integrations/test_public_api.py` | `__version__` via importlib.metadata with fallback, module docstring, four empty `__init__.py`, empty `py.typed`. Owner: tests/integrations/test_public_api.py |
