# Job 3 — Correct the unreleased changelog contract when authorized

**Wave:** 3
**Waits on:** Job 2 and the operator ruling on SPEC Open question 2
**W:** `CHANGELOG.md`, `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | sr | AC1.7 | `tests/test_docs.py` | Reserved RED task. It may open only when the main thread records the operator's explicit test ruling. Replace the all-numeric-header expectation with literal behavior: one live `0.8.0` header is labelled `Unreleased`; every published numeric header, including fixed `0.7.0`, retains its ISO date; the 0.8 Added/Fixed content remains required. Demonstrate the old dated 0.8 source fails this contract. If the ruling is absent or rejects this change, do not open the task. |
| J3.T2 | sr | AC1.7 | `CHANGELOG.md` | Reserved GREEN task. After J3.T1 and the ruling, change only the `0.8.0` header to `Unreleased`, preserving its section content and every existing published release date. The actual stable date remains a publication-event responsibility outside this candidate. |

This is not a permission workaround: without the specified ruling its tasks stay
unopened and the main thread must decide whether to defer the requirement. No
implementation task edits tests.

