# Job 1 — Restore one normalized pandas stream-record path

**Wave:** 2
**Waits on:** Job 2 for remaining J1.T4 and J1.T3
**W:** `rand_engine/main/data_generator.py`, `tests/test_6_stream_objects.py`,
`tests/test_docs.py`, `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`,
`docs/explanation.md`, `docs/compatibility.md`, `skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.2–AC1.3 | `tests/test_6_stream_objects.py` | Apply the operator-authorized test ruling in a `test(J1.T1):` commit. Delete only `_record_arrow_boundary` and assertions for Arrow invocation/call counts, Arrow-path exclusion, Arrow representation fallback, and unrelated Arrow conversion-error propagation. Retain or rewrite every public assertion for size/callable size, normalized `None`, values, exact Python types, key order, datetime strings, continuous offsets, `timestamp_created`, and sleep cadence. These behavior assertions may remain GREEN against the parent because the public contract does not change; do not invent a pandas implementation mock or new performance gate. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_6_stream_objects.py`. |
| J1.T2 | sr | AC1.1–AC1.2 | `rand_engine/main/data_generator.py` | REBUILD the record-conversion unit after J1.T1: remove `_stream_records_are_arrow_compatible`, the import used only by it, the conditional Arrow conversion and the narrow fallback. After the existing datetime/missing-value normalization, use exactly `DataFrame.to_dict("records")`. Preserve public values, exact types, record/key order, timestamps, continuous offsets and cadence; do not touch `StreamHandler`, protected `gen_*` functions, signatures, benchmark code or limits. Run the same focused stream-contract test. |
| J1.T4 | sr | AC1.4 | `tests/test_docs.py` | RED first for the remaining consumer wording. Rename only the guide-execution namespace keys `arrow_records` and `fallback_records` to the approved neutral names, preserving every assertion and expected value. The parent guide still defines the old names, so the renamed assertion must fail before J1.T3. This operator ruling authorizes the equivalent existing-test variable rename only; do not add aliases, product assertions or a gate. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_docs.py` and record the focused RED result. |
| J1.T3 | jr | AC1.4 | `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/compatibility.md`, `skills/rand-engine/SKILL.md` | After J1.T4, replace only obsolete Arrow-or-pandas stream-record claims and its two guide example names with one truthful normalized pandas record path and neutral names. Keep every public behavior assertion, unrelated Arrow/schema guidance and the renamed consumer assertion intact; do not add aliases. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_docs.py` and show J1.T4 GREEN. |

J1.T1 merges before J1.T2; they completed under the original disjoint
allocation. J1.T4 then J1.T3 run after Job 2's official merge, because both
jobs otherwise own `tests/test_docs.py`. The existing CI benchmark is the only
performance authority and runs after candidate-head push; this job neither
changes nor reruns it locally.
