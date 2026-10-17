# Job 1 — Documentation semantic contracts

**Wave:** 1
**Waits on:** —
**W:** `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.2–AC1.4, AC2.1, AC2.4, AC3.3, AC4.1–AC4.3 | `tests/test_docs.py` | RED, strict-xfail semantic contracts derived from writers/errors, `METHOD_CATALOG` plus live Spark validation, builders/factories, `CASES`, navigation and link targets; the existing `__all__` reference case remains unchanged. |

The RED cases assert inventories, executable outcomes and resolvable destinations,
never editorial wording. They introduce no runtime assertion and do not execute a
new docs build.

