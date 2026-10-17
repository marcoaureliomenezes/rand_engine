# Job 1 — Documentation semantic contracts

**Wave:** 1
**Waits on:** —
**W:** `tests/test_docs.py`, `docs/3_WRITING_FILES.md`, `docs/errors.md`, `mkdocs.yml`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.3, AC1.5, AC2.4 | `tests/test_docs.py` | RED semantic contracts for returned writers and caller-facing errors, including class/callable inventories, accepted writer boundaries and navigation; the existing `__all__` reference case remains unchanged. |
| J1.T2 | jr | AC1.1–AC1.3, AC1.5, AC2.4 | `docs/3_WRITING_FILES.md`, `docs/errors.md`, `mkdocs.yml` | Implement the returned-writer and error reference destinations in established pages/navigation so J1.T1 becomes green; writer/error classes remain non-exported. |

`docs/3_WRITING_FILES.md` owns returned-writer reference; `docs/errors.md` owns
the caller-facing error reference. `docs/reference.md` stays unchanged with its
three `rand_engine.__all__` directives. The RED cases assert inventories and
resolvable destinations, never editorial wording. They introduce no runtime
assertion and do not execute a new docs build.

