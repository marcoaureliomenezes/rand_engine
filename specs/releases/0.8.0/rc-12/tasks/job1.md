# Job 1 — Record the observed stable publication date

**Wave:** 1
**Waits on:** independently verified stable 0.8.0 publication evidence from the
main thread
**W:** `CHANGELOG.md`, `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.2 | `tests/test_docs.py` | RED first, after the main thread records one official PyPI or GitHub Release UTC timestamp and URL. Replace only `_changelog`'s 0.8.0 `Unreleased` expectation and section matcher with that exact ISO date; retain every numeric-header assertion, the fixed 0.7.0 date and all 0.8 Added/Fixed assertions. The commit names the grill-recorded main-thread ruling. Demonstrate RED against the unchanged header; do not add a date fallback, weaken, delete or skip an assertion. |
| J1.T2 | jr | AC1.1–AC1.3 | `CHANGELOG.md` | GREEN after J1.T1. Change only the 0.8.0 header to the exact observed UTC date supplied with the official publication evidence. Preserve every release version, tag/artifact reference, section body and historical date. Run the focused documentation contract and show J1.T1 GREEN. |

The fully stated GREEN task is assigned to `jr`; the known unavailable junior
runtime permits the documented senior fallback without a configuration change.
Neither task may open before the named public evidence exists.
