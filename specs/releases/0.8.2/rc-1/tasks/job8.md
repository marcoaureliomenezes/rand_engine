# Job 8 — version and changelog (wave 7)

Last behaviour-free job: it waits for every other job so the CHANGELOG states what shipped. The RED literal and its implementation are separate tasks (`WT merge` refuses an implementation commit that touches `tests/`); T3 is free. R7: the header is `## [0.8.2] - <closure date>`, the date read from the clock when written; rc-2 adds its entries and re-dates it.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J8.T1 | jr | AC9.1 | `tests/integrations/test_public_api.py` | RED: the built-wheel version literal (`:558`) reads `0.8.2`; no other line changes |
| J8.T2 | jr | AC9.1 | `pyproject.toml` | `version = "0.8.2"` (`:3`); no other line changes. Owner test: `tests/integrations/test_public_api.py` |
| J8.T3 | jr | AC9.2 | `CHANGELOG.md` | `## [0.8.2] - <closure date>` above `[0.8.1]`, three groups. **Fixed**: the five Origin bugs by name; the Windows drive-relative stream target that landed on the work branch. **Changed**: did-you-mean lines, size refused at resolution, the newly refused specs. **Removed**: `validate_with_warnings`, `validate_spark_with_warnings`. Owner test: `tests/test_docs.py` (`_changelog`, a dated header) |

Done when: `verify:`; `tests/test_docs.py` and `tests/integrations/test_public_api.py` pass.
