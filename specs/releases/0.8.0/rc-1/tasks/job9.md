# Job 9 — FR5 error footer and documentation URL

**Wave:** 4 · **Waits on:** Job 1, Job 6

- Only the `_raise` footer (`common_validator.py:275`) points to the docs site, from one base-URL constant (ruling 5); per-method anchors would need structured errors in 52 messages and are out of 0.8.0.
- The `pyproject.toml` `documentation` URL is asserted equal to that constant by one wheel-test assert.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J9.T1 | sr | AC5.6, AC5.8 | `tests/test_1_common_validator.py`, `tests/integrations/test_public_api.py` | RED: a `SpecValidationError` message ends with the site URL; the built wheel's `Project-URL: Documentation` equals the same base URL. Owner: tests/test_1_common_validator.py |
| J9.T2 | sr | AC5.6, AC5.8 | `rand_engine/validators/common_validator.py`, `pyproject.toml`, `tests/test_1_common_validator.py`, `tests/integrations/test_public_api.py` | one base-URL constant used by the `_raise` footer (replaces the repo-root URL); `documentation` = the site. Owner: tests/test_1_common_validator.py |
