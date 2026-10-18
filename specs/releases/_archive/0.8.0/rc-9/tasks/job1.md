# Job 1 — Prepare truthful stable and preview documentation artifacts

**Wave:** 1
**Waits on:** —
**W:** `scripts/docs_site.py`, `mkdocs.yml`, `rand_engine/cases/agent.md.txt`, `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC1.1–AC1.6, AC1.8, AC3.1 | `tests/test_docs.py` | RED first. In the existing documentation-contract owner, add behavior tests that invoke a missing preparation authority with explicit stable/preview mode and a literal reviewed SHA. Every rendered page and advertised raw human/agent entry in preview must show its notice before install guidance and the one matching source-ZIP command; the Agent resource instead routes installation to that live Getting Started entry. Prove no own-project `blob/master` URL remains, third-party URLs stay unchanged, advertised raw documents and case sources exist, and the skill mirror is byte-derived from the canonical skill with front matter first. Stable output retains ordinary pip/principal behavior without preview content. The Agent resource remains copied as declared package bytes while its durable mirror/Getting-started route is tested. Preserve all existing stable source-link, runnable-example, five-starter, Agent-resource, and install assertions. Prove the old implementation fails before handoff. |
| J1.T2 | sr | AC1.1–AC1.6, AC1.8, AC3.1 | `scripts/docs_site.py`, `mkdocs.yml`, `rand_engine/cases/agent.md.txt` | GREEN. Add the one standard-library preparation authority. It receives explicit mode and SHA, works in a caller-supplied untracked output directory, stages the complete docs input/artifact without mutating tracked sources, inserts the preview-only notice before install guidance on every rendered/raw public entry and its one source-ZIP command, transforms only own-project `blob/master` routes to that SHA, preserves external links and copies raw docs, `llms.txt`, case sources and one generated canonical-skill mirror at a durable Pages path. Stable mode produces ordinary source/PyPI routes. Give `mkdocs.yml` the concise truthful need-oriented description. Update the static Agent resource to link that durable mirror and to direct unreleased/new-feature installation to the live Getting started authority; do not add self-SHA bytes, a second skill, or CLI behavior. |

J1.T1 must merge before J1.T2. The implementation task does not edit tests.
The existing strict build is invoked against each prepared input as artifact
evidence; it is not made a new repository gate. The reviewer checks the
generated-mirror and packaged-context routes through the AI-surface lens.

