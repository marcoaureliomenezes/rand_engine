# Job 2 — 0.8.1 installs on today's stacks (wave 1)

Serial: T1 then T2. The RED test changes literals under the operator's compatibility ruling "Cobrir o que está em uso (Recomendado)"; the `test(` commit body names it.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC1.1, AC1.2 | `tests/integrations/test_public_api.py`, `tests/test_9_cli.py` | RED: the wheel METADATA test expects `Requires-Python >=3.11`, classifiers exactly 3.11-3.14, `Requires-Dist` `numpy>=1.26`, `pandas>=2.2,<4`, `pyarrow>=19.0.0` (no caps), faker extra `>=28.4.1` (no cap); `test_pyproject_declares_open_python_and_the_four_dependencies` expects `requires-python == ">=3.11"` and the same bounds in `tool.poetry.dependencies` (its dependency-dict literal follows AC1.1; the commit body says so). Literals replace the old ones; no assert is loosened or removed |
| J2.T2 | jr | AC1.1, AC1.2, AC1.3 | `pyproject.toml`, `poetry.lock` | GREEN: set `requires-python = ">=3.11"`, drop the 3.10 classifier and add 3.14, set the bounds of J2.T1; keep the test group `pyspark ^3.5.0` and `faker ^28.4.1`; `poetry lock` keeps faker 28.4.1, numpy 2.1.1, pandas 2.2.3, pyarrow 23.0.1 and pyspark 3.5.8 (list the five in the commit body); `poetry check --lock` exits 0; owner tests `tests/integrations/test_public_api.py`, `tests/test_9_cli.py` |

Done when: `verify:`; `tests/integrations/test_public_api.py` and `tests/test_9_cli.py` pass; a scratch `uv pip install --dry-run` of the built wheel with `pandas>=3`, `pyarrow>=24` and `faker>=30` resolves (it was unsatisfiable before).
