# Job 4 — RandSpecs schema and Faker helpers

**Status:** Approved
**done:** true

## Stage J4.S1 — RED

- Contract: exit helper/public tests fail by assertion under strict xfail markers; envelope `tests/test_4_rand_specs_helpers.py tests/integrations/test_public_api.py`; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S1.T1 — schema/Faker helper RED · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · exact schema mapping/override/refusal and local Faker state literals; missing import is faked at the import seam.
- J4.S1.T2 — public/dependency RED · AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · three-name export stays; ordinary install has no Faker import.

## Stage J4.S2 — omitted helper contract RED

- Contract: exit `tests/test_4_rand_specs_helpers.py` fails by final assertions under strict xfail markers for omitted existing AC5.3, AC6.2 and AC6.3 cases; envelope `tests/test_4_rand_specs_helpers.py`; ACs AC5.3, AC6.2–AC6.3.
- J4.S2.T1 — extension/refusal/override RED · AC5.3, AC6.2–AC6.3 · `W:` `tests/test_4_rand_specs_helpers.py` · owner `tests/test_4_rand_specs_helpers.py` · require explicit refusal for installed Arrow extension types `pa.uuid()` and `pa.json_()`, a kwargs-only override whose merged result is semantically invalid and therefore reaches normal validation, and negative plus non-integer `pool_size` classes in addition to the preserved zero/bool cases; no source or packaging change.

## Stage J4.S3 — implement helpers

- Contract: exit helper/public tests GREEN, lock/requirements agree and no network/data read occurs; remaining source and test ownership follows the current two-gate tasks below; ACs AC5.1–AC5.4, AC6.1–AC6.4, AC9.4.
- J4.S3.T1 — implement existing `RandSpecs` helpers · AC5.1–AC5.4, AC6.1–AC6.4 · `W:` `rand_engine/examples/common_rand_specs.py` · owner `tests/test_4_rand_specs_helpers.py` · source-only implementation returning plain column-spec/RandSpec dicts, copying inputs and using local optional Faker only.
- J4.S3.T2 — package optional Faker without widening public surface · AC5.3, AC9.4 · `W:` `pyproject.toml` `poetry.lock` `requirements.txt` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · use already approved dependency/version; no mandatory import.

The executed RED and packaging rows above remain the historical record. The following fresh tasks own the still-pending work; their write sets are exact and disjoint:

| task | AC | `W:` | outcome |
|---|---|---|---|
| J4.T1 | AC6.1 | `tests/test_0_np_core.py` | Date-bound parsing RED; owner `tests/test_0_np_core.py`. Assertion-first RED, without xfail, proves general ISO date-only bounds can be used with timestamp output formatting while legacy endpoint/refusal behavior, custom-formatted bounds and seeded output stay compatible. |
| J4.T2 | AC6.1 | `rand_engine/core/_np_core.py` | Canonical date-bound parser; owner `tests/test_0_np_core.py`. Source-only correction separates input-bound parsing from output formatting in the existing core seam, with no helper special case or public API. |
| J4.T3 | AC5.1–AC5.4, AC6.1–AC6.4 | `tests/test_4_rand_specs_helpers.py` | Retire satisfied helper markers; owner `tests/test_4_rand_specs_helpers.py`. A `test(...)` commit deletes only strict markers satisfied by the helper and core implementations, changes no assertion, and reuses the original helper integration case for AC6.1. |
| J4.T4 | AC5.1–AC5.4, AC6.1–AC6.4, AC9.4 | `specs/releases/0.7.0/rc-2/tasks/job4-helpers.md` | Close helper job; owner `tests/test_4_rand_specs_helpers.py`. After J4.S3.T1, J4.T1–J4.T3 and the already-executed package task are green, write terminal `done` exactly once. |

Order: merge the source-only helper task first, then J4.T1 → J4.T2 → J4.T3 → J4.T4. The input parser accepts the established custom bound format and the general date-only ISO boundary; `date_format` continues to control emitted values. It must not hard-code the approved example dates or consume extra RNG draws.
