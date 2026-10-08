# Job 4 — RandSpecs schema and Faker helpers

**Status:** Approved

## Stage J4.S1 — RED

- Contract: exit helper/public tests fail by assertion under strict xfail markers; envelope `tests/test_4_rand_specs_helpers.py tests/integrations/test_public_api.py`; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S1.T1 — schema/Faker helper RED · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · exact schema mapping/override/refusal and local Faker state literals; missing import is faked at the import seam.
- J4.S1.T2 — public/dependency RED · AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · three-name export stays; ordinary install has no Faker import.

## Stage J4.S2 — implement helpers

- Contract: exit helper/public tests GREEN by marker deletion only, lock/requirements agree and no network/data read occurs; envelope `rand_engine/examples/** pyproject.toml poetry.lock requirements.txt tests/test_4_rand_specs_helpers.py tests/integrations/test_public_api.py`; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S2.T1 — implement existing `RandSpecs` helpers · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `rand_engine/examples/common_rand_specs.py` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · return plain column-spec/RandSpec dicts, copy inputs, local optional Faker only.
- J4.S2.T2 — package optional Faker without widening public surface · AC5.3, AC9.4 · `W:` `pyproject.toml` `poetry.lock` `requirements.txt` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · use already approved dependency/version; no mandatory import.
