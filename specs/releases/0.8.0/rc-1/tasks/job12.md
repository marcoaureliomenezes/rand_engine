# Job 12 — Reconciliation: memory pass and closure

**Wave:** 7 · **Waits on:** Job 7, Job 11

Last job (`reconcile` tree). Ruling 4: the Tech Stack update is a `pe` task here; `dd-release-implementation`'s `MEMORY-UPDATE.md` governs the pass.

- Constitution invariant 11: `ARCHITECTURE.md` `## Tech Stack` gains Zensical, mkdocstrings (numpydoc), MkDocs-Material fallback, ruff; `QUALITY.md` `## Gates` drops "No lint or type checker is configured" and states the ruff D and docstring gates (costs in PLAN §3).
- Atoms touched: the public-API, validation, writer, packaging, docs and CI atoms the diff changes; the README carries no derived markers, so the pass does not rewrite it.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J12.T1 | pe | SPEC §6 invariant 11 | `specs/memory/**` | Tech Stack and Gates update, feature atoms from the code diff, catalog regenerated. Owner test: none (memory; `memory.py check` is the check) |
| J12.T2 | pe | SPEC §6 invariant 11 | `specs/releases/0.8.0/_RELEASE.json` | closure entries through `release.py` verbs only (`memory`, `phase`). Owner test: none (ledger; `release.py check` is the check) |
