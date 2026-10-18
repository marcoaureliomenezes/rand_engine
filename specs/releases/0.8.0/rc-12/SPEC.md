# SPEC — Release: 0.8.0, candidate 12 (post-stable comparison evidence)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand
**Approval:** The operator approved “Executar os dois cenários em CI
observacional (recomendado)” after receiving the exact Python and Spark
contracts, pinned-environment boundary and non-gating behavior. The standing
instruction to finish the current rand-engine work includes the already-defined
post-publication CHANGELOG bookkeeping. No requirement below may start
implementation or execution before stable 0.8.0 publication is independently
verified.

- Mandatory grill:
  `2026-10-18T164610Z-main-thread-post-stable-comparison-grill.handoff.json`;
  no unanswered question.
- As-is authority:
  `2026-10-18T164351Z-dd-sw-engineer-sr-comparison-ci-as-is-refresh.handoff.json`.
- Protocol evidence:
  `2026-10-18T040056Z-main-thread-comparison-protocol-proposal.html`,
  `2026-10-18T050331Z-dd-sw-engineer-sr-comparison-cost-pilot.html` and
  `2026-10-18T054316Z-dd-sw-engineer-sr-comparative-ci-as-is.html`.

## Bug window review

Rc-11 fixed no bug record and changed only the current release-note wording.
The preceding `preview-faker-install-guidance` fix was inspected and judged KEEP
in rc-11; no child bug followed it. The bug ledger has 0 open records, so this
candidate has no bug-window rebuild.

The active `outreach` backlog entry is provenance for the requested measured
comparison. It remains open because its broader posts, Discussions,
awesome-list outcomes and on-demand packaging are outside this candidate; this
SPEC neither exits nor otherwise dispositions it.

## 1. Problem

The public comparison explains capability differences among rand-engine,
Faker and dbldatagen, but it intentionally has no measured cross-library CI
evidence. The existing benchmark cannot supply that evidence: it compares
rand-engine base and head under a 1.3 regression limit and has different
workloads, dependencies and release duties. Combining the two would weaken the
meaning of the release gate and could present a constrained measurement as a
universal product ranking.

Stable 0.8.0 is also still marked `Unreleased` in `CHANGELOG.md`. That marker is
correct before publication. Once the stable distribution exists, the release
record needs the actual observed UTC publication date, without rebuilding,
retagging or overwriting the distribution.

## 2. Measurable goals

- After independently verified stable publication, record its actual UTC date
  in the 0.8.0 CHANGELOG header through a RED/GREEN contract transition.
- Run two bounded, reproducible observational comparisons in an isolated,
  non-required CI workflow: 100,000 materialized Python dictionaries against
  Faker and 1,000,000 fully evaluated Spark rows against dbldatagen.
- Publish raw samples, validations, environment identity, executed Spark plans,
  derived medians and actual CI cost as one honest artifact and job summary.
- Update the public comparison guide only from a validated real-runner artifact,
  describing the protocol and bounded observations and linking the raw evidence.
- Keep every internal regression benchmark path, workload, committed result and
  threshold byte-for-byte unchanged.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — publication truth | independently verify stable 0.8.0 and replace its temporary CHANGELOG marker with the observed UTC date | AC1.1–AC1.3 |
| 2 — isolated observation | implement and structurally test the two exact comparison contracts and dedicated environment | AC2.1–AC2.7 |
| 3 — CI evidence | execute the first non-required real-runner observation and retain its raw and derived evidence | AC3.1–AC3.4 |
| 4 — public explanation | update the comparison guide from validated evidence without ranking the products | AC4.1–AC4.3 |

## 3. Non-goals

- A universal speed claim, winner, product score, adoption claim or comparison
  across workloads other than the two named contracts.
- A competitor performance threshold, required check, scheduled job or change
  to any current merge gate.
- Any change to `benchmarks/speed.py`, `tests/test_benchmarks.py`,
  `.github/workflows/benchmarks.yml`, `docs/benchmarks.json`,
  `docs/BENCHMARKS.md`, their base, workload, artifact schema or 1.3 limit.
- Runtime dependencies, `poetry.lock`, public APIs, generation behavior,
  random-value equality between libraries or session/package setup inside a
  generation timing.
- Rewriting the stable 0.8.0 version, tag, wheel, source distribution, PyPI
  files or GitHub release; minting a new release id; workspace governance or
  worktree changes.
- Broad outreach, new external posts or messages, awesome-list acceptance or
  indexing, Context7 submission, conda-forge publication, or disposition of the
  active `outreach` entry.

## 4. Requirements

### FR1 — Record the actual stable publication date

- AC1.1 (release integration): implementation is blocked until independent
  evidence confirms the stable `0.8.0` distribution and release were published.
  The literal calendar date comes from the official PyPI upload time or GitHub
  release `published_at` in UTC; the evidence source and timestamp are recorded.
- AC1.2 (unit RED/GREEN): `tests/test_docs.py` first changes its existing
  CHANGELOG contract from literal `Unreleased` to the observed ISO date and
  fails against the unchanged header. It retains the assertions for every
  numeric header, the fixed 0.7.0 date and the 0.8 Added/Fixed content. The test
  commit names the main-thread ruling recorded by the mandatory grill; no
  assertion is deleted, narrowed or skipped.
- AC1.3 (unit and semantic review): only the 0.8.0 header then changes to the
  exact observed date and makes AC1.2 green. No version, tag, artifact or closed
  historical release text changes.

### FR2 — Implement the two bounded comparison contracts

- AC2.1 (unit): one comparison runner owns protocol, validation and artifact
  generation. `tests/test_comparison.py` verifies the workload shapes,
  AB/BA/AB ordering, warm-up exclusion, median derivation, validation failures
  and artifact fields without timing assertions. Its module-level execution
  requires only the standard library; comparator packages are imported inside
  the runner or explicit test factories.
- AC2.2 (integration): the Python workload materializes exactly 100,000
  dictionaries containing only `value: int` in 0..999999, `tier: str` in
  `{bronze, silver, gold}` and `active: bool`. rand-engine uses
  `DataGenerator(...).get_df().to_dict("records")`; Faker uses direct provider
  calls. Scalar normalization needed for the shared dictionary contract is
  inside both timed calls. Validation outside the clock covers all rows, keys,
  exact Python types and domains. `stream_dict` is not used.
- AC2.3 (integration): the Spark workload builds exactly 1,000,000 rows with
  eight partitions and columns `ordinal` 0..999999, `value` in 0..999999 and
  `tier` in `{bronze, silver, gold}` for rand-engine and dbldatagen. Both sides
  use one already-created long-lived `local[8]` Spark session. Each timed call
  includes build plus
  `select(xxhash64(ordinal, value, tier)).agg(count(*), sum(hash)).collect()`.
  Validation outside the clock covers count, exact schema, actual partition
  count, ordinal cardinality/range, value domain, tier set, unexpected nulls,
  aggregate presence and executed physical-plan evidence that all payload
  expressions were evaluated.
- AC2.4 (unit and integration): each side warms once outside its samples and
  records exactly three timed repetitions in AB/BA/AB order for each workload.
  Raw samples and medians are retained. Package installation, imports, Spark
  session creation and output validation are separately measured or reported
  and never included in the generation metric.
- AC2.5 (integration): validation compares the shared contracts, not exact
  random values. The runner and every output omit winner, score, threshold and
  universal-ranking fields or prose.
- AC2.6 (CI integration): the dedicated comparison environment installs the
  actual published `rand-engine==0.8.0` wheel rather than an editable checkout
  and pins every direct comparator dependency, including Faker 28.4.1,
  dbldatagen 0.4.0.post1, PySpark 3.5.8, setuptools 83.0.0, jmespath 1.0.1 and
  pyparsing 3.2.5. The comparison runner stays outside the installed package.
  The artifact retains the pip installation report, wheel hash and distribution
  metadata plus harness SHA, Python, Java, Spark, OS image, runner identity and
  every selected version. These facts bound reproducibility to the recorded
  environment; they do not claim full hermetic reproducibility. Nothing enters
  runtime dependencies or `poetry.lock`.
- AC2.7 (source review): the internal benchmark paths named in the non-goals are
  byte-identical to this candidate's base. Its base, workloads, committed
  artifacts and 1.3 limit remain the sole internal regression authority.

### FR3 — Produce a non-gating real-runner artifact

- AC3.1 (CI integration): a distinct observational workflow triggers on pushes
  to canonical `wt/**` refs only when a comparison-owned path changes, enabling
  the first run from the reviewed job branch. It also exposes
  `workflow_dispatch` for use after the workflow reaches the default branch.
  It is non-required, unscheduled and does not alter existing PR checks.
- AC3.2 (CI integration): the first job-branch run executes both contracts in a
  fresh Ubuntu runner and emits versioned JSON plus derived Markdown. The JSON
  records explicit terminal status, workload definitions, package and runner
  identity, warm-ups, execution order, raw samples, medians, validation
  outcomes, schemas and executed physical plans. The workflow uploads both
  files and writes the derived summary even when a controlled harness or output
  validation fails.
- AC3.3 (CI observation, no threshold): that first run records actual setup and
  measurement step durations, artifact size and terminal state. These are
  observations only; the local 47.02-second execution and 98-second setup pilot
  are feasibility evidence, not CI expectations or pass limits.
- AC3.4 (CI integration): a comparator harness or validation failure is reported
  honestly in its own workflow and artifact. No comparison outcome propagates
  into the required benchmark job or becomes a merge threshold.

### FR4 — Publish only bounded, validated evidence

- AC4.1 (documentation integration): only after AC3 produces a validated actual
  artifact, `docs/comparison.md` identifies the exact two workloads, versions,
  runner, raw samples and medians, validation status and measurement limits. It
  links the durable Actions run/artifact and separates setup cost from generation
  samples.
- AC4.2 (documentation contract): the guide retains its factual capability
  comparison and says the observations apply only to their named workloads and
  environment. It makes no winner, universal-speed, ranking, adoption or
  production-throughput claim.
- AC4.3 (existing documentation and release gates): executable documentation,
  strict site build and the unchanged repository verify line pass with the new
  guide. No new permanent gate repeats the observational run.

## 5. Replaces

- After stable publication is verified, the temporary 0.8.0 `Unreleased`
  header is replaced by the official observed UTC publication date.
- No runtime, benchmark or comparison behavior is removed; the existing factual
  comparison gains bounded real-runner observations while retaining its
  capability authorities and limitations.

## 6. Constraints and risks

| risk | control |
|---|---|
| implementation starts before publication | candidate definition may land, but every task and comparison execution waits for independent stable 0.8.0 verification |
| dissimilar APIs create an unfair comparison | use two explicit output contracts, one per execution model; validate full outputs outside the clocks |
| Spark prunes payload expressions | aggregate a hash over every payload column and retain/assert executed physical plans |
| setup or validation contaminates generation timings | long-lived shared Spark session, separate warm-ups, explicit timing boundaries and separate cost fields |
| a flaky or slow comparator becomes a release gate | isolated non-required workflow, no threshold and no existing workflow edit |
| first workflow cannot be manually dispatched from an unmerged ref | narrow push trigger on canonical `wt/**` job refs; retain manual dispatch for the default branch |
| published numbers outlive their context | preserve raw samples, exact pins, environment identity, validation and run link beside each observation |
| documentation implies a universal winner | prohibit winner/ranking fields and require workload-limited language in artifact tests and semantic review |
| CHANGELOG date is guessed or rewrites the release | derive it from named official UTC evidence after publication and change only the header/test contract |

## 7. Open questions

None. The operator approved both exact observational scenarios. The mandatory
grill resolved the non-gating workflow, first-run trigger, dependency boundary,
publication precondition and existing-assert transition without inventing a new
release id or changing workspace behavior.
