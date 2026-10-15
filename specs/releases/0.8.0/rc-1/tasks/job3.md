# Job 3 — FR2.2 and FR2.3 workflow permissions and SHA pins

**Wave:** 1 · **Waits on:** —

CI config has no seam in this repo (ruling 9): no test and no YAML-parser dependency. Every commit body quotes the bug's repro grep at zero hits.

- Token scope sweep (every `gh` or API caller in `.github/workflows`, grep `gh |GH_TOKEN|github.token`): `test_on_push.yml` `check_pr` (:20-23, `gh pr list`) declares no scopes and gains job-level `permissions: pull-requests: read`, because top-level `contents: read` would otherwise zero it; `create_github_release` in the master and development publish files (`gh release create`) already hold `contents: write`; `benchmarks.yml` (`gh pr comment`) declares `pull-requests: write` at the top. Evidence: J3's push CI shows the `test_on_push` `test` matrix ran (it needs `check_pr`).
- Permissions: `for f in .github/workflows/*.yml; do grep -q '^permissions:' $f || echo $f; done` prints nothing. Jobs that declare their own scopes keep them; `id-token: write` stays only on the two publish jobs.
- Pins: 6 mutable refs in 4 files (premise corrected from 2): `codecov/codecov-action@v4` x3 (pr_to_master:79, pr_to_development:219, auto_tag_publish_development:119), `pypa/gh-action-pypi-publish@release/v1` x2 (auto_tag_publish_master:156, auto_tag_publish_development:260), `aquasecurity/trivy-action@master` x1 (pr_to_development:108). Sweep: `grep -nE 'uses: *[^ ]+@' .github/workflows/*.yml | grep -vE 'uses: *(actions|github)/' | grep -vE '@[0-9a-f]{40}'` prints nothing. The release tag stays in a trailing comment.
- File names are unchanged (the PyPI Trusted Publisher is bound to them). A reusable-workflow REBUILD is out of scope (ruling 10).
- Bugs closed: `workflow-missing-top-level-permissions`, `workflow-actions-mutable-refs`.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | jr | AC2.2 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml` | top-level `permissions: contents: read` in the four files lacking it, plus job-level `pull-requests: read` on `test_on_push.yml` `check_pr`. No test (CI config). Owner test: none, repro grep at zero hits quoted in the commit body |
| J3.T2 | jr | AC2.3 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml` | pin the 6 refs to full 40-hex SHAs with the tag as trailing comment. No test (CI config). Owner test: none, repro grep at zero hits quoted in the commit body |
