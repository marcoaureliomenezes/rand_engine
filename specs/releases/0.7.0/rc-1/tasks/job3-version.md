# Job 3 — version 0.7.0

**Status:** Approved
**done:** true

## Stage J3.S1 — RED

- Contract: exit package metadata version assertion RED; envelope `tests/integrations/test_public_api.py`; ACs AC9.4
- J3.S1.T1 — AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · strict-xfail assertion that project metadata reports 0.7.0
  Superseded: original T-070-11 explicitly requires no RED pytest. Actual wheel and sdist metadata provide the version evidence; no strict-xfail assertion or mirrored version test was added.

## Stage J3.S2 — version

- Contract: exit J3.S1 green and build metadata names 0.7.0; envelope `pyproject.toml`, `tests/integrations/test_public_api.py`; ACs AC9.4
- [x] J3.S2.T1 — AC9.4 · `W:` `pyproject.toml`, `tests/integrations/test_public_api.py` (RED marker line only) · owner `tests/integrations/test_public_api.py`
  Done: `5886218` changes only `pyproject.toml` version from 0.6.4 to 0.7.0. Tagging and publishing remain the project pipeline's work at promote.

## Stage J3.S3 — close

- Contract: exit package metadata test and build validation green; envelope this file; ACs AC9.4
- [x] J3.S3.T1 — AC9.4 · `W:` this file (`done`) · owner `tests/integrations/test_public_api.py`
  Done: this closure records the build and gate evidence without claiming newly added tests.

## Evidence

- `5886218`: `poetry build` produced `rand_engine-0.7.0-py3-none-any.whl` and `rand_engine-0.7.0.tar.gz`; wheel `METADATA` and sdist `PKG-INFO` both report version 0.7.0 and licence MIT. `twine check` passed for both artifacts; artifacts and caches were redirected to workspace temporary storage.
- Main-thread task gate at `5886218`: 692 passed, 8 deselected in 54.79s.
- Main-thread J3.S2 stage gate at `5886218`: 692 passed, 8 deselected in 56.34s.
