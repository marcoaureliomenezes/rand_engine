# Job 2 — FR2 the five CI matrices test Python 3.13

**Wave:** 1 · **Waits on:** —

Workflow YAML has no seam in the suite (rc-1 ruling 9): CI is the check, and the commit body quotes the sweep below.

- The matrix list is the one decider: `['3.10', '3.11', '3.12', '3.13']` in `auto_tag_publish_master.yml:77`, `auto_tag_publish_development.yml:86`, `pr_to_master.yml:34`, `pr_to_development.yml:158`, `test_on_push.yml:45`.
- No summary names a Python version or a combinations count. `auto_tag_publish_master.yml:237` keeps only the test result (`| 2️⃣ Tests | <result> |`). In `test_on_push.yml` the per-cell grid at `:143-158` (header, three OS rows, "9 combinations") becomes one `| Tests | ${{ needs.test.result }} |` line with no count, and the comment at `:46` is reworded to name no version (e.g. "Spark tests skip where the fixture says"), so the sweep shows no stray hit. This deletes lines.
- Build-version settings stay: `PYTHON_VERSION: "3.12"`, `python-version: '3.12'` on non-matrix jobs, `matrix.python-version == '3.12'` coverage conditions. They are not the tested set.
- Sweep for the commit body: `git grep -n "3\.1[0-3]" .github/workflows` prints only the five matrix lists and those build-version settings.
- Evidence (not a test): the candidate's push CI, every leg green; the main thread cites the run id at review. A Spark failure on a 3.13 leg goes to Job 3.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | jr | AC2.1 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`, `.github/workflows/pr_to_development.yml` | the five matrices with 3.13; the master summary line reduced to the result; the `test_on_push.yml` grid replaced by one result line without a count and its `:46` comment reworded. No test (workflow YAML; evidence = the sweep above and the push CI). Owner test: none |
