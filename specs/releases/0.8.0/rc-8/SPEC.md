# SPEC — Release: 0.8.0, candidate 8 (sustainable adoption for humans and agents)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand

- The operator requires sustainable discoverability and adoption for humans and
  agents, with clear installation, onboarding, feature guidance and an optional
  `AGENTS.md` scaffold. Stable 0.8.0 must not deploy until the evidenced score is
  strictly greater than 90 in every field of the frozen 20-check rubric.
- Main-thread grill handoff
  `2026-10-18T035720Z-main-thread-rc8-adoption-grill.handoff.json` authorizes the
  bounded source work below: one agent starter, one compatibility and migration
  path, and truthful contribution, support and private-security routes. Public
  distribution, search observations and the independent performance repair stay
  outside this candidate, so the full adoption goal remains active.

## Bug window review

Rc-7 resolved one bug-ledger record. Its persisted fix
`get-started-race-overwrites-existing-target` (`f969425`) was inspected with
`git show` against the overfitting patterns and is **KEEP**. It replaces the
separate existence decision and truncating write with one `open("xb")`, catches
only `FileExistsError`, and retains the established error and exit behavior. The
race test creates a competitor at the write boundary rather than special-casing
a product value. This candidate retains that path and every protecting assertion.

The adjacent target-name seam also carries the older
`get-started-scaffold-shadows-package` fix (`16e8fc1`). Because target selection
has two prior fixes and the new Markdown starter needs a different output name,
the PLAN must REBUILD the case descriptor and target/resource selection as one
authority. The five existing `<slug>-example.py` names, packaged bytes and
exclusive-create behavior remain contract tests; no conditional second writer or
fallback path is added.

## 1. Problem

An agent can read the repository skill, but a user cannot ask the CLI to place
concise rand-engine usage context in another project. The repository's own
`AGENTS.md` is unsuitable because it contains contributor governance and private
workspace mechanics rather than portable package-use instructions.

Compatibility facts are spread across packaging metadata, the Spark guide,
tutorials and the changelog. A data engineer still has to assemble the tested
Python range, optional extras, Spark/Java/platform boundaries, seed limits,
recovery actions and 0.7-to-0.8 migration from separate sources.

The project exposes GitHub Issues but has no concise contribution route or
private vulnerability guidance. Discussions and private vulnerability reporting
are disabled today, so neither can be advertised as working until the actual
repository state supports the claim.

The frozen candidate score is 90/100 and the public stable score is 42.5/100.
Under the 0/2.5/5 rubric, greater than 90 in every field requires full credit in
every field. Public Pages, external discovery routes and need-only search cannot
be made true by local documentation alone.

## 2. Measurable goals

- `rand-engine get-started agent --out PROJECT` creates only
  `PROJECT/AGENTS.md` from a packaged resource and never overwrites an existing
  project instruction file. The five runnable starters stay unchanged.
- The generated context orients an agent to install rand-engine, use its supported
  public surface and reach authoritative detail without copying repository
  governance or an exhaustive second reference.
- One canonical guide answers compatibility, troubleshooting and 0.7-to-0.8
  migration questions from current package, CI and code facts.
- Contributors and users can find working setup, issue and verified private
  security-reporting routes, with no invented contact, SLA or bounty.
- README, site navigation, `llms.txt` and the skill expose the new sources through
  the existing documentation build and tests.
- The final artifact is rescored field by field; only observed evidence earns
  credit and rc-8 completion does not authorize stable deployment.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — agent entry point | rebuild the case descriptor, add the portable context resource and preserve the five executable starters | AC1.1–AC1.7 |
| 2 — human compatibility and trust | canonical compatibility/migration guidance and verified contribution, support and security routes | AC2.1–AC3.5 |
| 3 — shared evidence | connect existing human/agent indexes, verify the final artifact and record only earned score evidence | AC4.1–AC4.4 |

## 3. Non-goals

- Stable publication, `master` merge, Pages deployment, prerelease preview,
  indexing, external submissions, announcements, Context7, Discussions,
  conda-forge or disposition of the active `outreach` entry.
- Guaranteed search rank, human conversion or universal agent-runtime support.
  External runtimes may consume project context. Runtime-specific integration
  testing is outside this candidate; controlled generic-agent evidence is never
  presented as validation of an untested runtime.
- Competitive speed claims or a new cross-tool benchmark. The factual
  Faker/dbldatagen comparison and rand-engine benchmark stay unchanged.
- The pending `stream_dict` Arrow decision, benchmark workload or threshold,
  generation behavior, dependencies, platform matrix, workflows or any
  dadaia-workspace feature.
- A new CLI command, overwrite flag, interactive merge, config parser, installer,
  agent service, generated-doc pipeline, workflow, gate or documentation system.
- Copying repo contributor law, private paths or hidden harness instructions into
  a consuming project; removing, skipping or loosening an existing test.

## 4. Requirements

### Terms

- **Runnable starters:** `test-data`, `lake`, `kafka`, `databricks` and `faker`,
  unchanged Databricks-format Python sources written as `<slug>-example.py`.
- **Agent starter:** the new `agent` slug, a Markdown project-context resource
  written as `AGENTS.md`, never treated as executable Python.
- **Case descriptor:** the one internal authority per slug for description,
  packaged resource, target filename and starter kind. CLI list/help, resource
  lookup, target selection, package checks and docs inventories consult it.
- **Private report:** a report through the repository's enabled GitHub private
  vulnerability-reporting route, not a public issue.

### FR1 — Scaffold portable agent context through the existing CLI

- AC1.1 (unit): one Case descriptor owns all six slugs. The five Runnable starters
  retain their order, descriptions, resource bytes and target filenames; `agent`
  declares its Markdown resource and `AGENTS.md` target. List, parser choices and
  help expose the six without a second registry.
- AC1.2 (unit, RED first): from a clean output directory,
  `rand-engine get-started agent --out PROJECT` exits 0, creates only
  `PROJECT/AGENTS.md`, writes the packaged bytes and prints the path. The module
  entry point behaves identically.
- AC1.3 (unit, RED first): an existing or write-boundary competitor
  `PROJECT/AGENTS.md` is preserved byte-for-byte; the command exits 1, prints
  nothing on stdout and retains the existing error text on stderr. All six
  starters share the one `xb` writer and unrelated I/O errors propagate.
- AC1.4 (unit): all five Runnable starters keep their exact filenames, resources,
  Databricks markers, prerequisites, row limits and execution contracts. The
  Agent starter has a distinct Markdown partition and is never passed to `runpy`.
- AC1.5 (integration): the wheel ships all six declared resources byte-for-byte
  and its installed CLI produces them. Existing wheel metadata, package,
  entry-point, typing and optional-extra assertions remain unchanged and pass.
- AC1.6 (unit and AI-surface review): the generated `AGENTS.md` has one job:
  rand-engine package use in a consuming project. It gives core and Faker-extra
  installation, supported top-level imports, a first DataGenerator path, when
  SparkGenerator applies, sharp docs/`llms.txt`/skill pointers, and synthetic-data
  and credential boundaries. It instructs users to preserve and merge with
  existing project rules, and contains no workspace law, secret, private path,
  universal-runtime promise or copied exhaustive method table.
- AC1.7 (integration): getting started and the skill name the exact command and
  output, state that the starter begins in 0.8.0, and explain review/merge when a
  project already has instructions. They do not claim the already-published
  0.8.0rc4 wheel contains it.

### FR2 — Make compatibility, troubleshooting and migration one task path

- AC2.1 (integration): one canonical guide distinguishes the open package range
  Python `>=3.10` from the CI-tested 3.10–3.13 set; it names the core install,
  Faker extra and caller-supplied PySpark prerequisite without calling 3.14+
  tested.
- AC2.2 (integration): the guide states the actual Spark test partitions, CI Java
  version, Windows/Python limitation, ordinary-column versus key seeding, and
  DataGenerator-only feature partitions. Each fact traces to packaging,
  workflows, memory or an executable contract.
- AC2.3 (integration): a 0.7-to-0.8 section gives concrete actions for stable
  imports, stricter validation, new CLI/docs/API surfaces, Spark keys, SQLite
  output and record compatibility, then links the changelog for full history.
- AC2.4 (integration): concise symptom → cause → recovery paths cover missing
  Faker, missing Spark/Java, a Spark-refused spec, invalid input and an existing
  scaffold target. Recovery never deletes or overwrites a user's file.
- AC2.5 (existing gates): runnable blocks execute in the docs harness and internal
  links pass the strict site build. No dependency, workflow, command, gate or
  source-text prose mirror is added.

### FR3 — Publish truthful contribution, support and security routes

- AC3.1 (integration): canonical contribution guidance gives repository-relative
  setup and check commands that work from a clean checkout, plus the minimum
  useful contribution flow. It also gives repeatable adoption checks for a fresh
  install, starter/task output, links and agent context by reusing the existing
  pytest/docs build plus a small declared manual sample; it creates no permanent
  score file, service or CI gate. It requires no private workspace path or dadaia
  tool.
- AC3.2 (integration): support links enabled GitHub Issues and asks for version,
  Python/platform, minimal synthetic RandSpec or command, expected and actual
  result, and a redacted traceback/reproduction. It advertises neither disabled
  Discussions nor a response-time promise.
- AC3.3 (external state plus integration): after IMPLEMENTATION begins and before
  the security guidance merges, the main thread enables native GitHub private
  vulnerability reporting and verifies the repository API reports it enabled.
  Security guidance sends vulnerabilities there and ordinary bugs to Issues;
  it invents no email, token, SLA or bounty.
- AC3.4 (integration): security guidance uses a published-release support policy,
  asks for impact and a minimal safe reproduction, and excludes credentials,
  personal data and production data from reports.
- AC3.5 (integration): README, navigation and `llms.txt` expose the compatibility,
  contribution/support and security authorities; the skill points to them rather
  than duplicating their detail. Existing semantic link checks and strict build
  pass, and directly documented setup commands are verified.

### FR4 — Keep discovery evidence and product truth honest

- AC4.1 (unit/integration): README and getting started distinguish six CLI
  starters from five executable tutorials. `llms.txt` links the Agent resource
  beside the skill and Runnable starter sources; every advertised site route maps
  to navigation or a canonical repository file.
- AC4.2 (integration): public APIs, method inventory, executable case bytes, seed
  semantics, writers and benchmark records remain unchanged; every existing
  assertion for them remains and passes.
- AC4.3 (no repository test; evidence report): rescore the final candidate against
  all 20 frozen checks and publish each field percentage separately. Plans,
  disabled routes, unpublished pages and unobserved indexing earn no full credit;
  candidate readiness, public availability and need-only retrieval stay separate.
- AC4.4 (closure tools): reconcile `documentation`, `get-started-cli`,
  `public-api`, `templates-and-examples`, Architecture and Quality from the final
  diff; update CHANGELOG; refresh only affected derived markers; leave `outreach`
  active; and pass release, memory, backlog and bug checks with no new open item.

## 5. Replaces

- The five-slug-only inventory and uniform `<slug>-example.py` assumption are
  replaced by one six-entry Case descriptor. The five executable contracts stay;
  the Agent starter has an explicit filename and kind.
- Agent onboarding that requires discovering the repo skill gains one opt-in
  context scaffold whose detailed authorities remain docs, `llms.txt` and skill.
- Scattered compatibility facts gain one canonical task path; their code and
  packaging authorities do not change.
- Implicit contribution and security discovery gains linked, working GitHub-native
  routes. No public import, runtime behavior, workflow, benchmark or release
  condition is replaced.

## 6. Constraints and risks

- The PLAN owns exact as-is authorities and `W:` sets. Keep two jobs: Job 1 carries
  the CLI behavior RED and implementation; Job 2 reuses docs tests and strict
  build rather than inventing editorial assertions. No test is removed or loosened.
- A literal `if agent` beside the old filename derivation, a second writer or a
  duplicated slug registry fails the one-authority requirement.
- The Agent starter follows the AI-entity authoring contract: one job, progressive
  disclosure, public facts, checkable actions and minimal durable content.
- Candidate validation uses its built wheel. Source guidance identifies 0.8.0 as
  the first Agent-starter version and never attributes it to 0.8.0rc4.
- Private-reporting guidance waits for verified repository state. Full score and
  deployment continue to wait for the public-discovery sequence and the separate
  performance gate.

| risk | control |
|---|---|
| `AGENTS.md` conflicts with project rules | exclusive no-overwrite output, review/merge guidance and package-use-only content |
| six cases break five executable contracts | starter kind is authoritative; preserve five Python partitions and add one Markdown partition |
| compatibility prose drifts | cite packaging/workflow/code authorities and execute examples in the existing harness |
| security link is false | enable and API-verify private reporting before merging guidance |
| aggregate score hides weak discovery | report each field and retain the operator's all-fields release condition |

## 7. Open questions

None for this bounded candidate. Public-preview/outreach sequencing, organic
retrieval and the Arrow/performance decision remain explicit release-level
questions outside rc-8.
