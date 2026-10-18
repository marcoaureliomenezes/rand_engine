# PLAN — Release: 0.8.0, candidate 12 (post-stable comparison evidence)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-12/SPEC.md`
**Approval:** The approved SPEC records the mandatory grill and the operator's
approval of the two exact observational workloads. Every task remains blocked
until the main thread independently verifies stable 0.8.0 publication from an
official PyPI or GitHub Release record, including its UTC timestamp.

## 1. As-is review

This is Arm A. The read-only evidence is the approved SPEC's as-is authority
`2026-10-18T164351Z-dd-sw-engineer-sr-comparison-ci-as-is-refresh.handoff.json`,
the earlier comparative-CI as-is report
`2026-10-18T054316Z-dd-sw-engineer-sr-comparative-ci-as-is.html`, and the
protocol and cost-pilot reports named by the SPEC. The refresh handoff has
already been consumed by the product-engineer definition; this PLAN preserves
its stated authorities. The bug ledger has zero open records. The active
`outreach` intake remains open and is neither a job nor a candidate exit.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `CHANGELOG.md` 0.8.0 header | correctly says `Unreleased`; `tests/test_docs.py::_changelog` requires that literal | 0 open | UPDATE | Publication makes this one temporary lifecycle statement false. The observed official UTC date is the only new literal; the existing content and all other date assertions stay. |
| `tests/test_docs.py::_changelog` | protects the current 0.8.0 content and every other numeric release date | 0 open | UPDATE | It is the one release-document contract home. Its RED change narrows no assertion: it replaces only the pre-publication literal with the independently observed published date and retains all existing section/date checks. |
| `benchmarks/speed.py`, `tests/test_benchmarks.py`, `.github/workflows/benchmarks.yml`, `docs/benchmarks.json`, `docs/BENCHMARKS.md` | internal same-runner base/head regression authority, with its committed base and 1.3 limit | 0 open | KEEP | The two cross-library contracts have different dependencies and questions. Any edit would conflate observational evidence with the required internal regression gate. |
| `benchmarks/comparison.py` | absent | 0 open | ADD | No existing unit can own both output contracts, validation, alternating samples and a self-describing observational artifact without changing the internal benchmark schema. |
| `benchmarks/comparison-requirements.txt` | absent | 0 open | ADD | The isolated harness needs one pinned, CI-only direct-dependency authority. It prevents a comparator dependency from entering runtime dependencies or `poetry.lock`. |
| `tests/test_comparison.py` | absent | 0 open | ADD | The runner needs one contract-test home that exercises shape, ordering, validation, median and artifact semantics without a time target or imports of comparator packages during normal collection. |
| `.github/workflows/comparison.yml` | absent | 0 open | ADD | A separate non-required workflow is the smallest way to run and retain the observation without adding it to the existing required benchmark job. Its first canonical job-branch push solves the default-branch dispatch limitation. |
| `docs/comparison.md` | factual capability scope plus a clear internal-regression disclaimer | 0 open | UPDATE | After a validated real-runner artifact exists, this is the public authority for the two bounded observations. It keeps its capability comparison and does not become a ranking page. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| 0.8.0 publication date | official PyPI 0.8.0 upload time or GitHub Release `published_at`, in UTC | `CHANGELOG.md`, `tests/test_docs.py` | the temporary `Unreleased` literal after publication only |
| internal rand-engine regression | `benchmarks/speed.py` and its existing workflow/tests | `docs/benchmarks.json`, `docs/BENCHMARKS.md` | none |
| cross-library protocol, validation and machine artifact | new `benchmarks/comparison.py` | `tests/test_comparison.py`, pinned requirements | none |
| comparison environment pins | new `benchmarks/comparison-requirements.txt` | workflow installation report and wheel metadata | no comparator package in `pyproject.toml` or `poetry.lock` |
| observation trigger, retention and non-gating behavior | new `.github/workflows/comparison.yml` | `benchmarks/comparison.py` | no comparator steps in `benchmarks.yml` |
| public comparison explanation | `docs/comparison.md` | validated Actions artifact and current capability sources | no universal winner, score, threshold or adoption claim |

## 2. Decisions and verification

- The publication test transition is a RED/GREEN pair. It opens only after the
  main thread gives the exact observed UTC date and its official evidence URL;
  no task guesses a calendar date or modifies a release artifact.
- The comparison runner is a standard-library-importable harness boundary. It
  imports Faker, Spark and dbldatagen only within explicit runner factories, so
  the ordinary pytest matrix never acquires comparator dependencies.
- `benchmarks/comparison-requirements.txt` pins the dedicated comparison
  environment. The workflow installs the public `rand-engine==0.8.0` wheel
  without an editable checkout, records pip's report and the installed wheel
  hash/metadata, and keeps all setup/import/session cost separate from timed
  sample cost.
- The runner performs the two approved contracts only: 100,000 materialized
  three-field Python dictionaries, and one million fully evaluated three-field
  Spark rows at eight partitions. It warms each side once, records exactly
  AB/BA/AB samples and medians, validates outside clocks, records executed
  plans, and cannot emit winner, score or threshold fields.
- The new workflow is push-triggered only for comparison-owned changes on
  canonical `wt/**` branches, plus `workflow_dispatch` after it reaches the
  default branch. The main thread may push the reviewed Job 3 branch to obtain
  the first real-runner run. Existing benchmarks do not trigger on that push;
  no existing benchmark file changes and no new required check or schedule is
  introduced.
- Actual Actions execution is the E2E test for the workflow. The workflow has
  no local YAML-text mirror: its correctness evidence is a real job that
  preserves its JSON/Markdown artifacts and summary even on controlled harness
  or validation failure. Its duration, artifact size and terminal status are
  measurements, not targets.
- Documentation updates only after the main thread validates that real Actions
  artifact. The guide change is checked semantically against the artifact and
  with the existing strict documentation build; a prose-mirroring test would
  not protect the factual observation.
- The repository `verify:` line is unchanged and runs only at the official
  merge points. No job repeats it locally. The existing Java 17/Zah environment
  remains the main thread's gate environment.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | stable-publication evidence | 1 | `CHANGELOG.md`, `tests/test_docs.py` |
| Job 2 | stable-publication evidence | 2 | `benchmarks/comparison.py`, `benchmarks/comparison-requirements.txt`, `tests/test_comparison.py` |
| Job 3 | Job 2 | 3 | `.github/workflows/comparison.yml` |
| Job 4 | Job 3 and validated first Actions artifact | 4 | `docs/comparison.md` |

## 3. Requirement trace and post-merge boundary

| acceptance criteria | owner and evidence |
|---|---|
| AC1.1–AC1.3 | Job 1 RED/GREEN pair, named official publication evidence and exact header-only semantic review. |
| AC2.1–AC2.7 | Job 2 contract tests and implementation review, including base-byte comparison of every protected internal benchmark path. |
| AC3.1–AC3.4 | Job 3 workflow review, then the main thread's first reviewed job-branch push and retained Actions JSON/Markdown/summary evidence. The real run is observational and never a required PR condition. |
| AC4.1–AC4.3 | Job 4 artifact-grounded guide update, semantic comparison against the validated Actions output, strict site build and the unchanged official merge verification. |

## 4. Reconciliation (after all runnable jobs)

**W:** `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`,
`specs/memory/product/quality/benchmarks.md`,
`specs/memory/product/onboarding/documentation.md`,
`specs/memory/product/catalog.json`, `specs/memory/product/index.md`,
`specs/releases/0.8.0/_RELEASE.json`.

The product engineer reconciles only source truth established by the final
candidate diff and the validated observation. It records the actual
publication/date evidence and Actions artifact separately, regenerates affected
memory indexes/markers, leaves `outreach` active unless its owner can truthfully
close it, and retains the internal benchmark's base/workload/limit as its own
authority.
