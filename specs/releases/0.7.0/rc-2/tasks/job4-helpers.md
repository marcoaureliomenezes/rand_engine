# Job 4 — RandSpecs schema and Faker helpers

**Status:** Approved

## Stage J4.S1 — RED

- Contract: exit helper/public tests fail by assertion under strict xfail markers; envelope `tests/test_4_rand_specs_helpers.py tests/integrations/test_public_api.py`; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S1.T1 — schema/Faker helper RED · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · exact schema mapping/override/refusal and local Faker state literals; missing import is faked at the import seam.
- J4.S1.T2 — public/dependency RED · AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · three-name export stays; ordinary install has no Faker import.

## Stage J4.S2 — omitted helper contract RED

- Contract: exit `tests/test_4_rand_specs_helpers.py` fails by final assertions under strict xfail markers for omitted existing AC5.3, AC6.2 and AC6.3 cases; envelope `tests/test_4_rand_specs_helpers.py`; ACs AC5.3, AC6.2–AC6.3.
- J4.S2.T1 — extension/refusal/override RED · AC5.3, AC6.2–AC6.3 · `W:` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · require explicit refusal for installed Arrow extension types `pa.uuid()` and `pa.json_()`, a kwargs-only override whose merged result is semantically invalid and therefore reaches normal validation, and negative plus non-integer `pool_size` classes in addition to the preserved zero/bool cases; no source or packaging change.

## Stage J4.S3 — implement helpers

- Contract: exit helper/public tests GREEN by marker deletion only, lock/requirements agree and no network/data read occurs, then write this job file's terminal `done` once; envelope `rand_engine/examples/** pyproject.toml poetry.lock requirements.txt tests/test_4_rand_specs_helpers.py tests/integrations/test_public_api.py specs/releases/0.7.0/rc-2/tasks/job4-helpers.md`; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S3.T1 — implement existing `RandSpecs` helpers · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `rand_engine/examples/common_rand_specs.py` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · return plain column-spec/RandSpec dicts, copy inputs, local optional Faker only.
- J4.S3.T2 — package optional Faker without widening public surface · AC5.3, AC9.4 · `W:` `pyproject.toml` `poetry.lock` `requirements.txt` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · use already approved dependency/version; no mandatory import.
- J4.S3.T3 — close helper job · AC5.1–AC5.4, AC6.1–AC6.4, AC9.4 · `W:` `specs/releases/0.7.0/rc-2/tasks/job4-helpers.md` · owner `tests/test_4_rand_specs_helpers.py` · after the stage contract is green, write terminal `done` exactly once and commit `chore(tasks): done job4-helpers`.
