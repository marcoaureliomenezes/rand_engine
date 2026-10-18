# Job 1 — Restore one normalized pandas stream-record path

**Wave:** 1
**Waits on:** —
**W:** `rand_engine/main/data_generator.py`, `tests/test_6_stream_objects.py`,
`docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`, `docs/explanation.md`,
`docs/compatibility.md`, `skills/rand-engine/SKILL.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.2–AC1.3 | `tests/test_6_stream_objects.py` | Apply the operator-authorized test ruling in a `test(J1.T1):` commit. Delete only `_record_arrow_boundary` and assertions for Arrow invocation/call counts, Arrow-path exclusion, Arrow representation fallback, and unrelated Arrow conversion-error propagation. Retain or rewrite every public assertion for size/callable size, normalized `None`, values, exact Python types, key order, datetime strings, continuous offsets, `timestamp_created`, and sleep cadence. These behavior assertions may remain GREEN against the parent because the public contract does not change; do not invent a pandas implementation mock or new performance gate. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_6_stream_objects.py`. |
| J1.T2 | sr | AC1.1–AC1.2 | `rand_engine/main/data_generator.py` | REBUILD the record-conversion unit after J1.T1: remove `_stream_records_are_arrow_compatible`, the import used only by it, the conditional Arrow conversion and the narrow fallback. After the existing datetime/missing-value normalization, use exactly `DataFrame.to_dict("records")`. Preserve public values, exact types, record/key order, timestamps, continuous offsets and cadence; do not touch `StreamHandler`, protected `gen_*` functions, signatures, benchmark code or limits. Run the same focused stream-contract test. |
| J1.T3 | jr | AC1.4 | `docs/1_DATA_GENERATOR.md`, `docs/5_RECIPES.md`, `docs/explanation.md`, `docs/compatibility.md`, `skills/rand-engine/SKILL.md` | Replace only the obsolete Arrow-or-pandas stream-record claims with one truthful normalized pandas record path. Keep the public behavior, neutral record examples and unrelated Arrow/schema guidance accurate. Run `poetry run python -m pytest -q -p no:cacheprovider tests/test_docs.py`. |

J1.T1 merges before J1.T2; J1.T3 follows J1.T2 so consumer wording describes
the reviewed implementation. The existing CI benchmark is the only performance
authority and runs after candidate-head push; this job neither changes nor
reruns it locally.
