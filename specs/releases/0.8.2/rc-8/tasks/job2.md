# Job 2 — one loader for scripts loaded by path (wave 1)

Runs beside Jobs 1 and 3. Every assert is unchanged. One task: the loader and its four callers land together, or the tree holds both deciders.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC52.1, AC52.2 | `tests/conftest.py`, `tests/integrations/test_eval_tasks.py`, `tests/integrations/test_public_api.py`, `tests/integrations/test_eval_check.py`, `tests/integrations/test_eval_gate.py` | add `load_by_path(name, path)` to `tests/conftest.py` (a one-line docstring; `spec_from_file_location`, `module_from_spec`, `exec_module`; returns the module); the four blocks (`test_eval_tasks.py:19-23`, `test_public_api.py:686-692`, `test_eval_check.py:42-46`, `test_eval_gate.py:16-20`) call it through `from tests.conftest import load_by_path` and keep their wrapper names (`_load_eval_run`, `_load_run`, the `check` fixture, `load_gate`); the three `import importlib.util` lines of those files go; `test_public_api.py:920-922` becomes the one line `@pytest.mark.parametrize("k", ["4", "0", "-1", "abc", "", "2.5"], ids=["k4", "k0", "k-1", "kabc", "kempty", "k2.5"])`, the POSIX `skipif` and the body unchanged. No file added. Net -6 (+22/-28) |

Done when: `verify:`; `tests/integrations` passes with `JAVA_HOME` set (the spark-generator trial needs it); `git grep -nE -e spec_from_file_location -e module_from_spec -- tests` prints hits in `tests/conftest.py` only; `git grep -n 'importlib.util' -- tests/integrations` prints nothing; `git diff --numstat <base>...HEAD -- tests/conftest.py tests/integrations` deletes more lines than it adds.
