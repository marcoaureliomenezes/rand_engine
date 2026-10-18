# SPEC — Release: 0.8.0, candidate 13 (outreach closure and final maintenance)

**Status:** Approved
**Release ID:** 0.8.0
**Owner:** dd-product-engineer
**Opened:** 2026-10-18
**Origin:** backlog:outreach
**Approval:** The operator approved “Publicar anúncio e concluir nesse escopo
(Recomendado)”, making the retained outreach scope exactly one factual
repository announcement, two submitted curated-list pull requests and the
approved bounded comparison CI plus guide. The operator's earlier “Approved.
Move forward” and “continue” authorize the already-inspected final maintenance:
five `setup-java` pin updates and removal of two historical skill clauses. The
main thread additionally ruled that the non-secret four-component Java version
must use the exact opaque representation `Java (version components: 17, 0, 20,
1)` so the unpublished release suffix can pass the existing publication gate.
This formatting adaptation makes no product decision and does not change the
closed rc-12 scope.

- Mandatory grill:
  `2026-10-18T180520Z-main-thread-rc13-grill-and-outreach-publication.handoff.json`;
  every operator decision is resolved.
- Outreach closure authority:
  `2026-10-18T172545Z-dd-product-engineer-outreach-closure-contract.handoff.json`.
- Maintenance as-is authority:
  `2026-10-18T165336Z-dd-sw-engineer-sr-poststable-maintenance-as-is.handoff.json`.
- Publication-format ruling:
  `2026-10-18T185806Z-main-thread-publication-format-ruling.html`.
- Actual retained outreach evidence includes public Discussion
  [#51](https://github.com/marcoaureliomenezes/rand_engine/discussions/51),
  submitted curated-list pull requests
  [#18](https://github.com/statice/awesome-synthetic-data/pull/18) and
  [#393](https://github.com/igorbarinov/awesome-data-engineering/pull/393),
  and successful observational comparison run
  [39153239357](https://github.com/marcoaureliomenezes/rand_engine/actions/runs/39153239357).

## Bug window review

Rc-12 fixed no bug-ledger record. Its observational comparison, publication-date
correction and memory reconciliation introduced no persisted `fix_sha`, so
there is no new prior fix to classify KEEP or REBUILD. The bug ledger has 0 open
records and 11 resolved records; this candidate has no bug-window rebuild.

The active `outreach` backlog item is this candidate's sole ledger pick. Its
original brainstorm included more channels than the operator retained for this
delivery. The later approval above is authoritative: acceptance or indexing of
the submitted pull requests is not delivery credit; other channels, vinta and
conda-forge are outside this delivery; Context7 remains a manual account act.

## 1. Problem

All retained outreach acts now have direct evidence, including the bounded
comparison and public guide completed by rc-12, but the `outreach` entry remains
active because only a candidate with `Origin: backlog:outreach` can close it.
Leaving the broad idea-stage wording active would falsely imply unfinished
delivery after the operator narrowed and approved its terminal scope.

Five native CI workflows still pin the deprecated `actions/setup-java` v4
commit while the comparison workflow already uses the supported v5.7.0 commit.
The affected jobs keep Java 17 and run on GitHub-hosted runners compatible with
the Node 24 action. Only the action pin is stale; triggers, permissions,
matrices, commands and existing gates remain authoritative.

The repository Agent skill carries two pieces of release history in current-use
instructions: one contrasts the Agent starter with the old 0.8.0rc4 wheel and
one introduces the current stream record contract as a historical transition.
Removing that history makes the skill state only what users and agents need
now, without changing either contract.

Finally, the comparison guide writes the observed Java version as a dotted
four-component token. The existing publication gate conservatively recognizes
that shape as an IPv4 literal, so it refuses the unpublished suffix. The value
is public runner metadata, not a credential. The same opaque components can be
represented losslessly as `Java (version components: 17, 0, 20, 1)` without
assigning a meaning to any component or changing the observation.

## 2. Measurable goals

- Replace exactly five deprecated Java action SHA/comment pairs with the one
  supported v5.7.0 pin while every other workflow input and gate stays
  unchanged.
- Remove exactly two historical clauses from the Agent skill while preserving
  its starter safety and stream record contracts.
- Preserve the observed Java version in the comparison guide using the
  publication-safe non-IP representation and change no comparison fact.
- Close `outreach` as delivered only after reconciliation re-verifies the one
  announcement, two submissions and successful comparison CI/guide evidence.
- Pass the existing repository, documentation and native CI gates without a new
  test, gate, threshold or dependency.

### Wave ranking

| wave | scope | ACs |
|---|---|---|
| 1 — publication-safe maintenance | update five Java pins, prune two historical skill clauses and correct one Java-version representation | AC1.1–AC3.3 |
| 2 — truthful closure | verify the retained outreach evidence and disposition its one ledger entry | AC4.1–AC4.4 |

## 3. Non-goals

- Any new announcement, post, external submission, package channel or message;
  vinta, conda-forge and other channels remain outside this delivery, and
  Context7 remains a manual account act.
- Claiming acceptance, indexing, search rank, adoption, production use or a
  universal performance winner from the external submissions or comparison.
- Changing any workflow trigger, permission, matrix, Java distribution/version,
  command, required check, verify line or measured gate cost.
- Upgrading `setup-java` to v6, changing any other action pin or adding a test
  that merely mirrors a pinned SHA or prose phrase.
- Changing runtime code, public behavior, dependency declarations,
  `poetry.lock`, the comparison harness, observations, protocol, environment,
  internal benchmark paths, 1.3 regression limit or committed benchmark record.
- Editing dadaia-workspace, its hooks, worktree implementation, projected law,
  configuration or another repository; bypassing the existing publication gate.
- Reopening or amending rc-12, rewriting any public commit through
  `bff8526cc6a5d76cb2cb8a454b69971cbf0876a5`, rebuilding or overwriting the
  published 0.8.0 artifacts, or minting a next release id.

## 4. Requirements

### FR1 — Use the supported Java action pin without changing CI behavior

- AC1.1 (source review, no new test): in exactly
  `.github/workflows/auto_tag_publish_development.yml`,
  `.github/workflows/auto_tag_publish_master.yml`,
  `.github/workflows/pr_to_development.yml`,
  `.github/workflows/pr_to_master.yml` and
  `.github/workflows/test_on_push.yml`, replace
  `actions/setup-java@cf277c60eb25467037889841efdb72551f06f6c3 # v4`
  with
  `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961 # v5.7.0`.
  A text-mirroring assertion would not test action behavior, so no test is
  added for the literal.
- AC1.2 (source review): every other byte in those five setup steps retains
  `distribution: temurin`, Java 17 and the existing cache behavior; the
  workflows retain all triggers, permissions, matrices, commands and gates.
- AC1.3 (post-merge CI integration): after the reviewed candidate reaches its
  publication branch, its normal GitHub-hosted native CI proves compatibility
  for each setup-java invocation that actually executes. A conditional release
  job that legitimately skips because 0.8.0 already exists is recorded as
  skipped and is not falsely claimed as executed. This subsequent evidence does
  not block source reconciliation, and no workflow is rerun solely to repeat
  the merge gate.

### FR2 — Make the Agent skill describe only current contracts

- AC2.1 (documentation source): in `skills/rand-engine/SKILL.md`, delete only
  “The starter begins in 0.8.0 and is not in the published 0.8.0rc4 wheel.” The
  command, generated `PROJECT/AGENTS.md`, package-use-only boundary and
  existing-file preservation/review guidance remain unchanged.
- AC2.2 (documentation source): replace only “After unchanged normalization,
  every microbatch converts to pandas records, preserving public Python
  values.” with “Each microbatch converts to pandas records, preserving public
  Python values.” The endless-stream, timestamp, client ownership, throughput,
  ordering and value examples remain unchanged.
- AC2.3 (existing documentation integration): the current Agent-skill
  frontmatter, executable blocks, links, catalog and prepared-mirror contracts
  in `tests/test_docs.py`, plus the strict site build, stay green without an
  assertion removal, skip or phrase-mirroring test.

### FR3 — Preserve the Java observation in a publication-safe representation

- AC3.1 (documentation source, no new test): in `docs/comparison.md`, replace
  only the dotted four-component Java version token with `Java (version
  components: 17, 0, 20, 1)`. This is a lossless opaque formatting change to
  already-observed public runner metadata; it changes no workload, pin, sample,
  median, validation, limitation or claim. A dedicated text test would only
  mirror formatting, so existing documentation validation is sufficient.
- AC3.2 (publication integration): the existing publication gate accepts the
  candidate's final unpublished suffix without a bypass or workspace change.
  After the official candidate merge, the main thread applies the CLI's own
  remedy only to the unpublished suffix beginning at `cecbc0f` (whose parent
  `bff8526cc6a5d76cb2cb8a454b69971cbf0876a5` is already public and remains
  byte-for-byte unchanged), then obtains review on the resulting exact head.
- AC3.3 (existing documentation integration): the strict site build and
  executable documentation contracts pass with the corrected representation.

### FR4 — Close only the operator-approved outreach scope

- AC4.1 (closure observation): reconciliation verifies Discussion #51 is
  publicly readable and remains the one factual repository announcement. It
  credits publication only, not reach, adoption or indexing.
- AC4.2 (closure observation): reconciliation verifies the two authorized
  curated-list pull requests were submitted. Their current external state is
  recorded separately; delivery does not require or claim acceptance or
  indexing.
- AC4.3 (closure observation): reconciliation verifies Actions run 39153239357
  succeeded and that the repository contains its bounded comparison guide and
  evidence. The result remains limited to the two named workloads and carries
  no universal winner, competitor threshold or production claim.
- AC4.4 (backlog ledger): only after AC4.1–AC4.3 and the candidate's existing
  source and documentation gates are satisfied, run the official backlog writer
  once to exit `outreach` with disposition `delivered`, release `0.8.0` and a
  bounded summary naming the one announcement, two submitted pull requests and
  comparison CI/guide. Post-merge native CI remains AC1.3 evidence and does not
  block reconciliation. The closure summary repeats the exclusions: other
  channels, vinta and conda-forge are outside this delivery; Context7 is a
  manual account act.

## 5. Replaces

- The five deprecated setup-java v4 SHA/comment pairs are replaced by one
  immutable supported v5.7.0 SHA/comment pair; their surrounding CI behavior is
  retained.
- The two historical skill clauses are replaced by current starter safety and
  direct pandas-record guidance; no user or agent capability is removed.
- The IP-shaped Java version token is replaced by an equivalent opaque
  component-list representation; the observed value is retained.
- The broad idea-stage `outreach` wording is replaced at closure by the
  operator-approved terminal scope and its actual evidence.

## 6. Constraints and risks

| risk | control |
|---|---|
| Node 24 action is incompatible with a runner | use the pinned supported v5.7.0 action and require observed normal hosted-CI results; do not infer a skipped job ran |
| a pin-only edit changes workflow behavior | exact five-site replacement; source review proves all surrounding inputs, matrices and gates unchanged |
| skill cleanup removes current safety guidance | delete/replace only the two quoted clauses and retain existing documentation contracts |
| Java formatting loses provenance or invents component semantics | retain the four opaque components in order and leave every other observation unchanged |
| history remediation rewrites a public commit | preserve `bff8526...` and all earlier public commits; apply the official remedy only to the unpublished suffix and review its exact resulting head |
| backlog closure overclaims external outcomes | credit submission/publication only; explicitly exclude acceptance, indexing, adoption, ranking and omitted channels |
| maintenance is mistaken for a new release | remain in 0.8.0, use the existing work branch and mint no release id or distribution artifact |

## 7. Open questions

None. The mandatory grill resolved the final outreach boundary, actual retained
acts, excluded channels, maintenance scope, proof strategy and no-next-release
decision. The publication-format correction is the main thread's inspected
adaptation to the existing gate and changes no product fact.
