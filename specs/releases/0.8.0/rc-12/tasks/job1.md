# Job 1 — Publish bounded post-stable comparison evidence

**Wave:** 1
**Waits on:** independently verified stable 0.8.0 publication evidence from the
main thread
**W:** `CHANGELOG.md`, `tests/test_docs.py`, `benchmarks/comparison.py`,
`benchmarks/comparison-requirements.txt`, `tests/test_comparison.py`,
`.github/workflows/comparison.yml`, `docs/comparison.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.2 | `tests/test_docs.py` | RED first, after the main thread records one official PyPI or GitHub Release UTC timestamp and URL. Replace only `_changelog`'s 0.8.0 `Unreleased` expectation and section matcher with that exact ISO date; retain every numeric-header assertion, the fixed 0.7.0 date and all 0.8 Added/Fixed assertions. The commit names the grill-recorded main-thread ruling. Demonstrate RED against the unchanged header; do not add a date fallback, weaken, delete or skip an assertion. |
| J1.T2 | jr | AC1.1–AC1.3 | `CHANGELOG.md` | GREEN after J1.T1. Change only the 0.8.0 header to the exact observed UTC date supplied with the official publication evidence. Preserve every release version, tag/artifact reference, section body and historical date. Run the focused documentation contract and show J1.T1 GREEN. |
| J1.T3 | sr | AC2.1–AC2.6 | `tests/test_comparison.py` | RED first. Add focused behavior tests for a missing comparison runner using only standard-library module imports and explicit factories. Prove both literal workload definitions, one warm-up per side, exact AB/BA/AB order, full Python and Spark contract validation, median derivation from raw samples, separate setup/validation timing, required provenance/plan/artifact fields, and rejection of winner/score/threshold fields. No timing target, comparator import at collection time, editable-package assumption, YAML-text mirror, version-control/hash assertion or test of exact random values. |
| J1.T4 | sr | AC2.1–AC2.6 | `benchmarks/comparison.py`, `benchmarks/comparison-requirements.txt` | GREEN after J1.T3. Implement the sole runner and a dedicated direct-pin requirements authority: Faker 28.4.1, dbldatagen 0.4.0.post1, PySpark 3.5.8, setuptools 83.0.0, jmespath 1.0.1 and pyparsing 3.2.5. Generate versioned JSON and derived Markdown for exactly the approved 100,000-record Python and 1,000,000-row/eight-partition Spark contracts; install/import/session setup and validation remain outside timed samples. Require an installed public `rand-engine==0.8.0` wheel identity, report pip/wheel/distribution/runner/Java/Spark metadata, raw samples, medians, schemas, validations and physical plans. Do not edit the protected benchmark paths, runtime dependencies or lockfile. Run J1.T3 GREEN. |
| J1.T5 | sr | AC3.1–AC3.4 | `.github/workflows/comparison.yml` | Add one non-required, unscheduled observational workflow. It runs only on comparison-owned path changes pushed to canonical `wt/**` refs and supports `workflow_dispatch` once on the default branch. In a fresh Ubuntu runner, configure Java 17 with immutable `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961`, create the pinned dedicated environment, install the actual public `rand-engine==0.8.0` wheel, run both harness contracts, write the Markdown summary and upload JSON/Markdown artifacts with `always()` behavior for controlled harness/validation failures. Record setup and measurement durations, artifact size and explicit status. Do not edit existing workflows, declare a required check, schedule, threshold or PR comment. |
| J1.T6 | jr | AC4.1–AC4.3 | `docs/comparison.md` | Only after the main thread validates the first Actions artifact, add one bounded observations section from its actual run/artifact URL, raw samples, medians, runner, versions, validation status and setup-cost evidence. Identify only the approved workloads and environment, distinguish setup from timed generation samples and retain the factual capability table and internal-regression disclaimer. Do not claim a winner, universal speed, ranking, adoption or production throughput. Semantic review against the artifact plus the existing strict documentation build are evidence; no prose-mirroring test is added. |

Tasks are sequential, and every RED/implementation pair opens in separate task
trees. The fully stated `jr` tasks permit the known senior fallback without a
configuration change. After J1.T5 merges into the still-live Job 1 branch, the
main thread first inspects the workflow and task handoff, then pushes that
canonical job branch for the one real Actions observation. This checkpoint is
not an additional code-review merge verdict: the one job review happens after
J1.T6, before the official Job 1 merge removes the job branch. J1.T6 cannot
open from local-pilot values or an unvalidated run. The final job review and
unchanged official verify run once for this job; the separate candidate review
and official rc merge checks still apply.
