# Job 7 — FR8 truthful CI summaries

**Wave:** 3 · **Waits on:** Job 3, Job 4

- The `rand_engine.__version__` hint (master :267, pr_to_development :286, development :188) is true once Job 4 lands; the remaining stale text is the `0.5.6` literals (master :277 :335 :336) and `.github/workflow_info.md`.
- `workflow_info.md` (1518 lines, 9 stale hits, 0 readers in the tree) is a prose mirror of the YAML and goes (DELETE); `pipeline_doc.md` has 0 stale hits and stays.
- No test (prose, AC8.1): every commit body quotes the repro, e.g. `grep -rn '0\.5\.6\|rand_engine/integrations' .github` printing nothing. Bug closed: `workflow-summary-text-stale`.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J7.T1 | jr | AC8.1 | `.github/workflows/auto_tag_publish_master.yml` | replace the three `0.5.6` literals with the generic next-version wording. No test (prose). Owner test: none, repro grep at zero hits in the commit body |
| J7.T2 | jr | AC8.1 | `.github/workflow_info.md` | delete the file (DELETE; 0 readers). No test (prose). Owner test: none, repro grep at zero hits in the commit body |
