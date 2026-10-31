# Job 1 — only closed releases reach PyPI (wave 1, waits on nothing)

Law and dev loop: the rc path is deleted, the master workflow is rebuilt, the A/B base becomes a release. Every `test(` commit cites the SPEC's operator approval where it changes a pinned test; none does here. Owner test of the whole job: `tests/test_docs.py`. Serial order: T1 to T6 (T1 before T2; the workflow files are disjoint). The main thread deletes the GitHub environment `development` after T3 merges, and the operator removes the PyPI Trusted Publisher entry for the deleted workflow before the first master merge (PLAN Reconciliation).

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC3.4 | `tests/test_docs.py` | RED: no rc version string (`\d+\.\d+\.\d+rc\d+`) in `docs/`, `README.md`, `llms.txt`, `skills/`; fails on `docs/getting-started.md:53` |
| J1.T2 | jr | AC3.4 | `docs/getting-started.md` | DELETE the rc-wheel clause of line 53 and keep the rest of the paragraph; owner `tests/test_docs.py` |
| J1.T3 | jr | AC3.1, AC3.5 | `.github/workflows/auto_tag_publish_development.yml` | DELETE the file; `grep -rn auto_tag_publish_development .github docs README.md tests` returns 0 hits. AC3.5 is observed at the work to integration merge (Reconciliation) |
| J1.T4 | jr | AC3.2 | `.github/workflows/auto_tag_publish_master.yml` | REBUILD per AC3.2: delete `find_rc`, `latest_rc` and every RC text, keep the no-rc guard, order build, `publish_pypi` (environment `production`), `create_tag`, `create_github_release`; net lines negative; the summary says "Re-run failed jobs only" after a publish-then-tag failure and the publish job is never rerun (no gate added); source review, no test |
| J1.T5 | jr | AC3.3 | `.github/workflows/benchmarks.yml` | UPDATE the A/B base step to the highest bare `M.m.p` tag (`git tag -l`, filtered by `grep -E '^[0-9]+\.[0-9]+\.[0-9]+$'`, then `sort -V`, last line), the job summary names its commit; E2E on CI, observed in the Reconciliation record |
| J1.T6 | pe | AC4.3, AC4.4 | `specs/constitution.md` | ADD invariant 13 verbatim from AC4.3; invariants 6 and 12 are not edited (AC4.4); law text, no test |
