# SPEC — Release: 0.8.0, candidate 9 (truthful public documentation preview)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** operator-demand
**Approval:** Operator `aprovado` on 2026-10-18; applies to both decisions
recorded in section 7 and leaves the stable hold and separate Arrow decision
unchanged.

- The operator requires sustainable discoverability and adoption for humans and
  agents, and has said: “we will only deploy 0.8.0 after we make sure we are
  greater than 90.” The active release condition remains strictly greater than
  90 overall and in every field of the frozen 20-check rubric.
- Mandatory refinement handoff
  `2026-10-18T053629Z-main-thread-rc9-public-docs-grill.handoff.json` settles the
  goal and the stable hold. The operator's `aprovado` approves the short-lived
  public-root preview, temporary exact-branch environment rule and this SPEC and
  PLAN within the recorded scope.
- The as-is review, independent senior consumer pre-mortem and corrected Pages
  race analysis are
  `2026-10-18T053251Z-dd-sw-engineer-sr-rc9-public-docs-as-is.handoff.json`,
  `2026-10-18T053137Z-dd-sw-engineer-sr-rc9-docs-consumer-premortem.handoff.json`
  and
  `2026-10-18T043929Z-dd-sw-engineer-sr-preview-deploy-race-design.handoff.json`.
  The pre-mortem is senior-engineer fallback evidence after the requested
  researcher runtime failed before writing; it is not represented as researcher
  output.

## Bug window review

Rc-8 resolved no bug-ledger record and changed no bug-ledger byte over its
source window, so there is no new persisted `fix_sha` to judge KEEP or REBUILD.
Its final-review correction only strengthens the existing five-starter stdout
oracle. This candidate keeps that assertion and every existing runtime, CLI,
package, source-link and documentation assertion unless the operator gives the
specific test ruling recorded in section 7.

The bug ledger has zero open records. The only active backlog entry is
`outreach`; its operator provenance schedules external submissions after 0.8.0,
so this candidate neither consumes nor dispositions it. There is no live audit
finding to pick.

## 1. Problem

The 0.8 source documentation is accurate and its strict feature-head build is
green, but the canonical Pages root, `llms.txt` and sitemap return HTTP 404.
`master` is still 0.7.0 and does not contain the docs workflow or the 0.8 site.
Humans and agents therefore cannot reach the candidate authorities through the
public routes the README, package metadata and generated Agent context advertise.

Publishing the repository bytes unchanged would also be false. Normal
`pip install rand-engine` installs stable 0.7.0, while the current prerelease
does not contain the new Agent starter. README, guides, navigation, `llms.txt`,
the canonical skill and packaged Agent context contain project source links to
`master`; that branch lacks several 0.8 authorities. The dated 0.8 changelog
header claims a publication event that has not occurred, and the site has no
need-oriented description.

GitHub Pages exposes one public root. A feature preview therefore temporarily
replaces that root and requires the existing `github-pages` environment to allow
exactly `feature/0.8.0`. The current workflow cancellation and a default
single-pending shared concurrency group can cancel or replace a waiting stable
deployment. A preview is acceptable only with a bounded shared deploy queue,
fresh fail-closed remote checks and an explicit post-stable removal of the
temporary environment rule.

The frozen score is candidate readiness 95/100, public stable 42.5/100 and
discoverability 15/20 (75%). Public delivery can complete F3, but this candidate
does not complete F4 external discovery. Even after successful preview evidence,
discoverability is at most 17.5/20 (87.5%) until the separate external-discovery
work earns its missing half-check. Rc-9 cannot authorize stable 0.8.0.

## 2. Measurable goals

- The public root serves a prominently labelled unreleased 0.8.0 preview built
  from one reviewed `feature/0.8.0` event SHA. Every preview install and
  own-project source route identifies that same immutable SHA.
- A human can use the preview to install the reviewed source ZIP in a fresh
  environment, reach a first result and generate all six starters, including an
  `AGENTS.md` whose detailed skill route resolves publicly.
- An agent can retrieve `llms.txt`, rendered guides and references, raw Markdown,
  the one canonical skill's generated public mirror and starter sources without
  following a missing or stale own-project `master` path.
- Stable rendering remains ordinary PyPI/principal-branch documentation with no
  preview banner or source-ZIP install instruction. The `master` deployment path
  stays authoritative and eventually overwrites any preview at promotion.
- Deployment skips safely when the candidate is stale, either remote cannot be
  read, the feature/master versions differ from the exact allowed pair or the
  event is not the exact feature head.
- Source closure records only source and artifact evidence. After independent
  review, the official rc merge and the resulting `feature/0.8.0` push, a
  release-level verification records real HTTP and fresh-install observations
  and rescores the frozen rubric without credit for plans, local builds,
  submissions, indexing, ranking or unobserved agent runtimes.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — artifact truth | one isolated preview preparation authority, exact-SHA public content, canonical skill mirror and truthful release wording | AC1.1–AC1.8 |
| 2 — bounded public delivery | exact-ref eligibility, shared Pages queue, fail-closed remote guards and temporary environment policy | AC2.1–AC2.7 |
| 3 — source proof then public verification | artifact contracts before the official merge; deployed HTTP/install journey and frozen-rubric rescore after its feature push | AC3.1–AC3.6 |

## 3. Non-goals

- Stable publication, the `development` → `master` merge, a stable PyPI release,
  a stable GitHub release or declaring the operator's score condition met.
- Search-engine indexing, guaranteed rank, human conversion, universal agent
  runtime support, external submissions, announcements, Discussions,
  documentation registries, conda-forge or disposition of `outreach`.
- Competitive speed claims, comparator CI or a new Faker/dbldatagen benchmark.
- The pending `stream_dict` Arrow contract decision, its tests, benchmark
  workload, the 1.3 regression limit or any generation/runtime behavior.
- A dependency, site framework, workflow file, service, preview host, plugin,
  permanent score artifact, new gate or duplicate maintained skill.
- A broad `feature/**` Pages permission, a second public site, an atomic
  compare-and-deploy claim or an unconditional guarantee beyond the documented
  shared-queue capacity.
- Changing dadaia-workspace, its worktree model, hooks, personas, skills, rules or
  configuration; removing, skipping or loosening an existing assertion without
  the operator's specific ruling.

## 4. Requirements

### Terms

- **Preview artifact:** the isolated Pages artifact prepared for an eligible
  `feature/0.8.0` push; repository sources remain stable-oriented.
- **Stable artifact:** the Pages artifact prepared for `master`, using ordinary
  PyPI installation and principal-branch source links.
- **Reviewed SHA:** the deploy run's immutable `github.sha`, equal to a fresh read
  of the remote `feature/0.8.0` head after the shared deploy queue is acquired.
- **Own-project source URL:** a repository URL under the rand-engine project.
  Faker, dbldatagen and other third-party URLs retain their external identity.
- **Skill mirror:** a generated copy of `skills/rand-engine/SKILL.md` in the Pages
  artifact. The repository skill remains the sole maintained source.

### FR1 — Prepare a truthful immutable preview artifact

- AC1.1 (unit, RED first): one preparation authority accepts stable or preview
  mode plus the event SHA and produces the complete docs input/artifact without
  mutating tracked sources. It replaces any inline copies or rewrites it
  supersedes; no second URL registry, content tree or maintained skill exists.
- AC1.2 (unit, RED first): preview mode places a prominent unreleased 0.8.0 notice
  before installation guidance on every rendered page and on advertised raw
  human/agent entry documents. It gives one source-ZIP install command whose URL
  embeds the reviewed SHA. Stable mode has neither the notice nor a source-ZIP
  install command and retains the ordinary PyPI path.
- AC1.3 (unit, RED first): preview preparation rewrites every own-project
  `blob/master` source URL in the public artifact to the reviewed SHA, covering
  the README-derived home, `llms.txt`, navigation targets, compatibility and
  comparison content, the canonical skill mirror and copied raw Markdown. It
  does not rewrite third-party URLs. The prepared preview contains no remaining
  own-project `blob/master` source URL.
- AC1.4 (unit/integration, RED first): the skill mirror is byte-derived from the
  canonical repository skill, retains its YAML front matter as its first bytes
  and is reachable at one durable Pages path. The packaged Agent starter points
  to that route, and no hand-maintained mirror is added.
- AC1.5 (integration): the prepared preview publishes `llms.txt`, every raw
  Markdown route advertised by it, the skill mirror and starter source routes
  alongside the strict-built HTML. Snippet and case includes remain the same
  bytes as their source authorities.
- AC1.6 (integration): `mkdocs.yml` carries a concise, truthful, need-oriented
  site description covering Python synthetic test data, pandas, related tables,
  files/streams and optional Spark without claiming search rank or an unsupported
  engine/runtime.
- AC1.7 (integration plus operator-reserved test ruling): 0.8.0 is labelled
  `Unreleased`; its eventual date is recorded only from the actual publication
  event. The existing changelog contract currently requires every numeric release
  header, including 0.8.0, to carry an ISO date. Any replacement or narrowing of
  that assertion is authorized only as recorded in section 7; no implementer may
  silently waive or delete any other assertion.
- AC1.8 (integration): the strict site build passes for both prepared modes. The
  existing source assertions for principal-branch README/`llms.txt` links,
  executable examples, five runnable starters, one Agent starter and stable
  install syntax remain present and pass; preview assertions inspect only the
  prepared artifact.

### FR2 — Deploy only the exact eligible preview without stranding stable Pages

- AC2.1 (workflow integration, RED first): only a push to exact
  `refs/heads/feature/0.8.0` or `refs/heads/master` is deploy-eligible. Pull
  requests and other feature refs still build as today but cannot deploy.
- AC2.2 (workflow integration): the deploy job alone uses the shared
  `pages-public-site` concurrency group with `queue: max` and
  `cancel-in-progress: false`. Workflow-level cancellation is false for the two
  deploy-eligible refs, so it cannot cancel an active or queued Pages deploy;
  non-deploy runs retain bounded cancellation.
- AC2.3 (workflow integration, RED first): after acquiring the shared deploy
  queue, a preview job freshly reads the remote refs without moving its checkout.
  It proceeds only when its own project version is exactly 0.8.0, remote
  `master`'s project version is exactly 0.7.0 and remote `feature/0.8.0` equals
  `github.sha`. Missing, unreadable, stale or different values exit successfully
  before artifact deployment and emit an observable skip reason.
- AC2.4 (workflow integration): a `master` job retains the stable deployment path
  and is never rejected by the preview version pair. A queued stale preview
  rechecks after acquisition and skips if promotion or a newer feature head has
  arrived; a later eligible master deployment overwrites a running preview.
- AC2.5 (external integration, after SPEC/PLAN approval): immediately before the
  first reviewed preview deploy, the main thread adds exactly
  `feature/0.8.0` to the existing `github-pages` environment branch policies and
  verifies the live API returns only the prior `master` rule plus that exact
  temporary rule. It adds no wildcard and records the policy identifier needed
  for removal.
- AC2.6 (external release action): after a successful stable `master` Pages
  deployment is HTTP-verified, the main thread removes the exact temporary
  `feature/0.8.0` policy and verifies `master` is again the only allowed branch.
  Rc-9 records this future cleanup action and never claims it ran during the
  preview.
- AC2.7 (release evidence): promotion observes the shared queue result. If the
  documented 100-pending capacity cancels the master deploy, the master deploy is
  rerun and verified; the design is described as bounded eventual ownership, not
  atomic or universal ordering.

### FR3 — Prove source behavior, then the post-merge public experience

- AC3.1 (unit/integration, RED first): behavior-focused artifact tests take an
  explicit mode and SHA and prove the banner/install distinction, exact-SHA URL
  binding, absence of preview own-project `master` routes, unchanged external
  URLs, skill-mirror derivation and all advertised raw paths. They derive the
  consumer set from the preparation output rather than duplicate a prose list.
- AC3.2 (existing gates): the unchanged repository `verify:` line, docs strict
  build and existing documentation contracts pass. No new permanent gate or
  workflow is created, and the test command is not changed.
- AC3.3 (post-merge public E2E, no repository test): only after source closure,
  independent approval, the official rc worktree merge and its
  `feature/0.8.0` push may the exact reviewed head be deployed. HTTP checks then
  return success for the root, `llms.txt`, sitemap, local-search assets, getting
  started, compatibility, API/writer/error references, raw Markdown, the skill
  mirror and every advertised own-project case/source link. Canonical URLs
  identify the public site and the visible preview identifies that reviewed SHA.
- AC3.4 (post-merge public E2E, no repository test): from that public deployment,
  a fresh supported-Python environment installs the exact reviewed source ZIP,
  passes package dependency checks, reaches the documented first result, lists
  all six starters and runs the existing installed journey. `get-started agent`
  emits the packaged bytes and its skill pointer resolves over HTTP to the
  generated canonical mirror.
- AC3.5 (post-merge evidence report, no repository test): after AC3.3 and AC3.4,
  rescore the same frozen 20 checks and report every field separately. F3 receives
  no full credit before those observations; F4 receives no additional credit from
  publication alone. Candidate, public-preview and public-stable scores remain
  distinct, and no indexing, ranking, conversion or generic-runtime claim is
  inferred. The report/handoff is release-level evidence outside the closed SPEC;
  if a canonical release-state note is required, it lands only through a separate
  reviewed specs lane, never by amending the closed candidate or writing the work
  branch directly.
- AC3.6 (source closure tools): before the official rc merge, reconcile
  documentation, get-started-cli, Architecture and Quality from the final diff,
  regenerate the catalog/index, refresh only affected derived markers and pass
  release, memory, backlog and bug checks. Record AC3.3–AC3.5 as pending
  post-merge observations and assign no public F3 credit. Keep `outreach` active,
  the Arrow/performance decision untouched and the stable promotion hold explicit.

## 5. Replaces

- Docs preparation split across inline README copy, strict build and later raw
  copies is replaced by one coherent, testable artifact-preparation result when
  the PLAN confirms that replacement is needed. The canonical source documents
  and existing docs system remain.
- A public preview that would present ordinary PyPI and moving `master` routes is
  replaced by an unreleased, exact-SHA artifact. Stable output retains its
  ordinary PyPI/principal-branch contract.
- The Agent starter's unavailable principal-branch skill pointer is replaced by
  a durable Pages route generated from the one canonical skill source.
- Per-ref cancellation as the lifecycle controller for deploy-eligible Pages
  pushes is replaced by one bounded shared deploy-job queue plus execution-time
  remote guards. Non-deploy build cancellation remains.
- The false planned 0.8.0 date is replaced by truthful Unreleased status under
  the explicit test-contract ruling recorded in section 7.

## 6. Constraints and risks

- The operator approved the concrete SPEC and PLAN with `aprovado`. No workflow
  or remote environment policy changes during DEFINITION.
- The lifecycle order is source implementation → source closure and reconciliation
  → independent whole-candidate approval → official rc worktree merge and feature
  push → preview deployment → release-level HTTP/install verification and rescore.
  The candidate is not represented as complete public delivery before the last
  two steps, and the closed SPEC is never rewritten afterward.
- The existing docs workflow/site, repository tests and GitHub Pages environment
  carry this candidate. A new workflow, host, plugin, service, dependency or gate
  is outside scope.
- The preview uses the one public Pages root. An isolated public preview URL is
  unavailable through the current action; this trade-off requires the operator's
  explicit approval.
- The exact-SHA transformation applies to an isolated artifact, not tracked
  source documents. This preserves stable source assertions and makes the future
  master render ordinary stable documentation.
- GitHub supplies no atomic remote-ref-check-and-deploy operation. A newer
  reviewed feature push after the last check queues another non-cancelled run and
  eventually becomes the final preview; the residual window is disclosed.
- Local builds and green feature CI prove source integrity only. They earn no
  public availability, indexing, search-rank or external-discovery credit.

| risk | control |
|---|---|
| preview advertises content a normal install lacks | prominent unreleased notice and exact-SHA source-ZIP install in every public entry path |
| stale own-project links route to missing 0.8 files | transform all artifact consumers through one authority and prove zero remaining own-project `blob/master` routes |
| packaged Agent context points at an unavailable skill | durable generated Pages skill mirror plus fresh-install HTTP journey |
| preview run cancels or replaces stable deploy | no workflow cancellation on deploy refs, shared `queue: max`, fresh post-queue guards and observed promotion outcome |
| temporary environment permission becomes permanent | exact rule only, recorded identifier and API-verified post-stable removal action |
| preview publication is mistaken for full discoverability | frozen rescore keeps F4 unchanged; stable remains held below >90 in discovery |
| changelog test is weakened without authority | exact operator authorization recorded before the narrowly scoped assertion change |

## 7. Approval record

The operator answered `aprovado` to both concrete decisions:

1. Temporarily use the one public Pages root for this clearly labelled exact-SHA
   preview, adding only `feature/0.8.0` to the `github-pages` environment until a
   verified stable `master` deployment removes it.
2. Replace the existing changelog assertion that every numeric release header
   has an ISO date with the narrower contract “the one live unreleased version
   is labelled Unreleased; every published numeric release has an ISO date,”
   while retaining all 0.8 content and the fixed 0.7 date assertion.

This approval does not cover the separate Arrow conversion/test decision, change
the 1.3 regression limit or lift the stable-release hold; those remain outside
this candidate.
