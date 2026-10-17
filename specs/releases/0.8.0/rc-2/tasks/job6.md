# Job 6 — FR3.4 the reference page test is tied to the public surface (REBUILD)

**Wave:** 2 · **Waits on:** Job 1

Bug closed: `reference-test-self-referential`. The test's case source is the page it checks, so deleting a `:::` block deletes its own case. REBUILD the test: one test over `rand_engine.__all__`; `_resolve` leaves with the parametrization if no other caller remains (`grep -n _resolve tests/test_docs.py`: its only caller is this test); net lines ≤ 0.

- The test: the set of `:::` directives in `docs/reference.md` equals `{f"{o.__module__}.{o.__qualname__}" for o in <the __all__ objects>}` and each object has a docstring (`inspect.getdoc`). Literals only come from the public surface, not from the page.
- Revert check (the bug is in the test): the commit body records the mutation, deleting the `SparkGenerator` `:::` line turns the test red and restoring it turns it green. This is the RED evidence; no xfail can precede a test that passes on the correct page.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J6.T1 | sr | AC3.4 | `tests/test_docs.py` | REBUILD `test_reference_directive_names_the_canonical_documented_object` as above; commit `refactor(J6.T1): REBUILD reference directive test — cases from __all__`, mutation evidence in the body; then the `resolve` ledger commit. Owner: tests/test_docs.py |
