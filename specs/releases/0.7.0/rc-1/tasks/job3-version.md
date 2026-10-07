# Job 3 — version 0.7.0

**Status:** Approved

## Stage J3.S1 — RED

- Contract: exit package metadata version assertion RED; envelope `tests/integrations/test_public_api.py`; ACs AC9.4
- J3.S1.T1 — AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · strict-xfail assertion that project metadata reports 0.7.0

## Stage J3.S2 — version

- Contract: exit J3.S1 green and build metadata names 0.7.0; envelope `pyproject.toml`, `tests/integrations/test_public_api.py`; ACs AC9.4
- J3.S2.T1 — AC9.4 · `W:` `pyproject.toml`, `tests/integrations/test_public_api.py` (RED marker line only) · owner `tests/integrations/test_public_api.py`

## Stage J3.S3 — close

- Contract: exit package metadata test and build validation green; envelope this file; ACs AC9.4
- J3.S3.T1 — AC9.4 · `W:` this file (`done`) · owner `tests/integrations/test_public_api.py`
