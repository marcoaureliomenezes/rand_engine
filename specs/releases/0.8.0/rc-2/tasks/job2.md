# Job 2 — FR2 the five CI matrices test Python 3.13

**Wave:** 1 · **Waits on:** —

Workflow YAML has no seam in the suite (rc-1 ruling 9): CI is the check, and every commit body quotes the sweep below at zero stale hits.

- The matrix list is the one decider: `['3.10', '3.11', '3.12', '3.13']` in `auto_tag_publish_master.yml:77`, `auto_tag_publish_development.yml:86`, `pr_to_master.yml:34`, `pr_to_development.yml:158`, `test_on_push.yml:45`.
- `auto_tag_publish_master.yml:237` names `3.10, 3.11, 3.12, 3.13`. In `test_on_push.yml` the per-cell grid at `:143-158` (fixed ✅ rows for 3 OS × 3 Python, "9 combinations") and the comment at `:46` stop naming versions: the grid becomes one `| Tests | ${{ needs.test.result }} |` line and the total reads 12 combinations (3 OS × 4 Python). This deletes lines (PLAN §1 DELETE).
- Build-version envs (`PYTHON_VERSION: "3.12"`, `python-version: '3.12'` on non-matrix jobs) stay: they are not the tested set.
- Sweep for the commit body: `grep -n "3\.10, 3\.11, 3\.12\|Python 3\.10 |" .github/workflows/*.yml` prints nothing.
- Evidence (not a test): the candidate's push CI, every leg green; the main thread cites the run id at review. A Spark failure on a 3.13 leg goes to Job 3.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC2.1 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml` | the five matrices with 3.13; the master summary literal; the `test_on_push.yml` grid replaced by one result line. No test (workflow YAML; evidence = the sweep at zero hits and the push CI). Owner test: none |
