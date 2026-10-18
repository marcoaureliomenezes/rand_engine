# PLAN — Release: 0.8.0, candidate 9 (truthful public documentation preview)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-sw-engineer-sr
**SPEC:** `specs/releases/0.8.0/rc-9/SPEC.md`
**Approval:** Operator `aprovado` on 2026-10-18; both decisions in SPEC section
7 are authorized, while stable publication and the separate Arrow decision stay
outside this candidate.

## 1. As-is review

This is Arm A. Evidence is the pre-SPEC as-is review
`2026-10-18T053251Z-dd-sw-engineer-sr-rc9-public-docs-as-is.handoff.json`, the
independent senior-engineer consumer pre-mortem
`2026-10-18T053137Z-dd-sw-engineer-sr-rc9-docs-consumer-premortem.handoff.json`,
and the corrected Pages race design
`2026-10-18T043929Z-dd-sw-engineer-sr-preview-deploy-race-design.handoff.json`.
The requested researcher did not produce an artifact because its runtime failed
before writing; the consumer pre-mortem is senior-engineer evidence, not
researcher output. The operator's `aprovado` resolves the public-root and
changelog-test decisions exactly as recorded in SPEC section 7. There are no
open bugs. `outreach` remains active and is not this candidate's pick.

| unit | today | bugs | verdict | why |
|---|---|---|---|---|
| `.github/workflows/docs.yml` build and deploy steps | copies README, builds the tracked source, and separately copies `llms.txt` and `docs/**/*.md`; only `master` uploads/deploys, while workflow-level per-ref cancellation is true | 0 open | REBUILD | inline preparation cannot make a testable immutable preview, and the deploy lifecycle can cancel an eligible Pages delivery; it is replaced by one preparation call plus bounded eligible-ref deployment control. |
| `scripts/docs_site.py` | absent | 0 open | ADD | no existing code unit can own isolated preparation, preview URL/install transforms, raw routes, canonical-skill mirroring, and deploy eligibility without duplicating workflow shell decisions; one standard-library script is the smallest authority. |
| `README.md`, `docs/**/*.md`, `llms.txt`, `mkdocs.yml`, and `skills/rand-engine/SKILL.md` | canonical stable-oriented source documentation; several own-project routes use `blob/master`; `mkdocs.yml` has no site description | 0 open | KEEP / UPDATE | the source documents remain the one maintained truth; preparation updates only an isolated copy for preview, while `mkdocs.yml` gains the truthful site description. |
| `rand_engine/cases/agent.md.txt` | packaged bytes direct agents to a missing principal-branch skill and show ordinary installation | 0 open | UPDATE | the existing CLI copy contract stays intact, but the static resource must point to the durable Pages mirror and live getting-started authority; it must not bake an unknowable self SHA into package bytes. |
| `tests/test_docs.py` | proves source documentation consistency and deliberately requires principal-branch repository URLs; no prepared-artifact or deployment-guard behavior is tested | 0 open | UPDATE | this is the existing documentation-contract home; it gains behavioral preparation and eligibility tests while preserving every stable source assertion. |
| `CHANGELOG.md` and its `_changelog` assertion | claims dated `0.8.0` publication, while the test requires every numeric header to be dated | 0 open | UPDATE, operator-authorized | truthful Unreleased wording and the exact narrower test contract are authorized by the ruling in SPEC section 7. |
| GitHub `github-pages` environment branch policy | live configuration permits only `master` | 0 open | UPDATE, main-thread external action | source changes cannot bypass it; the main thread may add only `feature/0.8.0` after approval and records its identifier for removal after verified stable deployment. |

### 1.1 Authorities

| question | authority | consults | deleted |
|---|---|---|---|
| isolated stable/preview docs input, source-route transformation, banners, source-ZIP command, raw routes, and skill mirror | `scripts/docs_site.py` | canonical source documents, `mkdocs.yml`, and `docs.yml` | the workflow's inline README/raw-copy preparation and any second URL registry or maintained skill copy |
| whether an event may deploy the preview | `scripts/docs_site.py` eligibility result after fresh remote reads | `.github/workflows/docs.yml`, event ref/SHA, remote refs and project versions | ad hoc workflow conditions that do not prove version/ref freshness |
| stable source documents and the canonical skill content | tracked `README.md`, `docs/**/*.md`, `llms.txt`, `skills/rand-engine/SKILL.md` | artifact preparation only reads them | no source rewrite for a preview |
| installed Agent context bytes | `rand_engine/cases/agent.md.txt`, copied unchanged by `rand-engine get-started agent` | live generated Getting started page and Pages skill mirror | unavailable `blob/master` skill pointer; any self-referential SHA baked into the package resource |
| the Pages permission boundary | existing `github-pages` environment policy | main-thread API observation | any wildcard feature permission |
| unreleased versus published changelog wording | `CHANGELOG.md` plus its asserted contract after the operator's explicit ruling | actual stable publication event | the false planned date and the all-numeric-headers rule only if the operator authorizes its replacement |

## 2. Decisions and measured gate cost

- Job 1 introduces only `scripts/docs_site.py`, a small standard-library
  preparation authority. It prepares outside tracked source, receives mode and
  SHA explicitly, and is exercised through its output. It replaces the existing
  inline copying rather than adding a second docs pipeline or URL registry.
- The static Agent starter remains a package resource and the CLI continues to
  copy it byte-for-byte. Its durable skill link is the generated Pages mirror;
  for an unreleased preview it tells a consumer to use the live Getting started
  page, which carries the event SHA's install command. It therefore neither
  changes the CLI nor creates an impossible self-SHA package artifact.
- Job 2 depends on Job 1 and makes `docs.yml` invoke the authority. Its deploy
  job alone has the shared bounded `pages-public-site` queue. The workflow leaves
  non-deploy cancellation bounded, disables it for the two deploy refs, and
  relies on fresh post-queue eligibility rather than claiming atomicity.
- Job 3 remains serialized after Job 2. The operator's `aprovado` satisfies its
  reserved ruling exactly as recorded in SPEC section 7; no implementer may
  weaken another assertion to make the candidate pass.
- The repository `verify:` command and merge checks are unchanged. The prior
  successful feature Docs run is `39100631865`; its strict build was measured
  at 1.13 s in the recorded Docs run `38973485919`. The new preparation and
  guard's incremental CI cost is unknown until the reviewed Job 2 run, so this
  PLAN does not invent a value or add a permanent gate.
- After approval but before the first preview deploy, the main thread alone
  adds exactly `feature/0.8.0` to `github-pages`, verifies the policy contains
  exactly that rule and the existing `master` rule, and preserves the returned
  identifier. After an HTTP-verified stable `master` deploy, it removes that
  exact identifier and verifies `master` is again the sole rule. Those external
  acts are not task-tree writes and are never represented as complete early.

## DAG

| job | waits on | wave | W: |
|---|---|---|---|
| Job 1 | — | 1 | `scripts/docs_site.py`, `mkdocs.yml`, `rand_engine/cases/agent.md.txt`, `tests/test_docs.py` |
| Job 2 | Job 1 | 2 | `.github/workflows/docs.yml`, `scripts/docs_site.py`, `tests/test_docs.py` |
| Job 3 | Job 2; operator ruling recorded in SPEC section 7 | 3 | `CHANGELOG.md`, `tests/test_docs.py` |

## 3. Requirement trace and post-merge boundary

| acceptance criteria | owner and evidence |
|---|---|
| AC1.1–AC1.6, AC1.8; AC3.1 | Job 1 RED/implementation tasks: prepared stable and preview artifact behavior, source-route transformation, raw documents, canonical skill mirror, static Agent-resource route, truthful description and strict build inputs. |
| AC2.1–AC2.4 | Job 2 RED/implementation tasks: deploy eligibility and queue behavior, including fresh remote reads and observable successful skips. |
| AC1.7 | Job 3 after the explicit changelog test ruling recorded in SPEC section 7. |
| AC2.5 | main thread, only after candidate approval and before first reviewed preview deployment: exact external environment-policy addition and live API observation. |
| AC2.6–AC2.7 | main thread after future stable promotion: observed master queue result, HTTP verification, exact policy removal, and retry only if GitHub reports the documented queue-capacity cancellation. |
| AC3.2 | unchanged repository `verify:`, strict build, and existing documentation contracts at each normal job/candidate gate. |
| AC3.3–AC3.5 | release-level main-thread actions only after source closure, whole-candidate approval, official rc merge, and the `feature/0.8.0` push: public HTTP route sweep, fresh source-ZIP journey, then frozen 20-check rescore. No source-closure score gives F3 credit. |
| AC3.6 | product-engineer reconciliation on the rc integration tree after every job is merged: phase transition, drift-derived memory pass, affected derived markers/catalog/index, and release/backlog/bug checks. It records the public observations as pending and leaves `outreach`, Arrow work, and stable promotion untouched. |

The public checks are intentionally outside a task worktree: deploying an
unmerged branch would violate the specified lifecycle and could not prove the
official reviewed head. Rc-9 can raise discoverability only to 87.5% before the
separate external-discovery work, so its successful preview does not release the
stable hold.

## 4. Reconciliation (after all runnable jobs)

**W:** `CHANGELOG.md`, `specs/memory/ARCHITECTURE.md`,
`specs/memory/QUALITY.md`,
`specs/memory/product/onboarding/documentation.md`,
`specs/memory/product/onboarding/get-started-cli.md`,
`specs/memory/product/catalog.json`, `specs/memory/product/index.md`, and
`specs/releases/0.8.0/_RELEASE.json`.

The product engineer moves the phase once all job trees are closed, derives the
memory worklist from the final source diff, and changes only product truth that
the diff establishes. It regenerates catalog/index and refreshes only their
affected markers. It records source/artifact evidence separately from later
public HTTP/install observations, keeps `outreach` active, and retains the
stable promotion hold.

