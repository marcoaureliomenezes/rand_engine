# Job 3 — Run the isolated observation in Actions

**Wave:** 3
**Waits on:** Job 2
**W:** `.github/workflows/comparison.yml`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J3.T1 | sr | AC3.1–AC3.4 | `.github/workflows/comparison.yml` | Add one non-required, unscheduled observational workflow. It runs only on comparison-owned path changes pushed to canonical `wt/**` refs and supports `workflow_dispatch` once on the default branch. In a fresh Ubuntu runner, create the pinned dedicated environment, install the actual public `rand-engine==0.8.0` wheel, run both harness contracts, write the Markdown summary and upload JSON/Markdown artifacts with `always()` behavior for controlled harness/validation failures. Record setup and measurement durations, artifact size and explicit status. Do not edit existing workflows, declare a required check, schedule, threshold or PR comment. The E2E test is the first reviewed canonical job-branch Actions run; no YAML-text-mirroring test is added. |

After the reviewed Job 3 tree is merged, the main thread may push its canonical
job branch to trigger the first observation. It validates the Actions artifact,
summary and terminal state before allowing Job 4. A comparator failure remains
an honestly retained observation and does not propagate into the internal
benchmark or another required check.
