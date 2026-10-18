# Job 2 — Deliver only a current bounded Pages preview

**Wave:** 2
**Waits on:** Job 1
**W:** `.github/workflows/docs.yml`, `scripts/docs_site.py`, `tests/test_docs.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1–AC2.4, AC3.1 | `tests/test_docs.py` | RED first. Add behavior tests for the preparation authority's deploy-eligibility interface using literal event refs, SHAs and temporary remote-ref fixtures. Prove that only exact `feature/0.8.0` preview and `master` stable events are eligible; preview accepts only own version `0.8.0`, freshly read remote master version `0.7.0`, and an equal remote feature SHA. Missing, unreadable, stale and mismatched inputs must be observable successful skips before deployment. Prove master does not use the preview version pair. Do not test YAML prose or weaken source assertions. |
| J2.T2 | sr | AC2.1–AC2.4 | `.github/workflows/docs.yml`, `scripts/docs_site.py` | GREEN. Extend the same authority with the tested eligibility result and make the existing Docs workflow use it to prepare/upload the appropriate artifact. Deploy is eligible only for push events on the two exact refs. Its job alone uses `pages-public-site`, `queue: max`, and `cancel-in-progress: false`; workflow-level cancellation remains bounded for non-deploy work and is false for the two deploy refs. After the shared queue, preview reads remote refs without moving its checkout and invokes deploy only when the tested exact pair holds; otherwise it exits successfully with the skip reason. Master keeps its ordinary deployment path. Do not create a workflow, host, plugin, dependency, broad branch policy, or claim atomic deployment. |

J2.T1 must merge before J2.T2. Before any first preview deployment after
candidate approval, the main thread performs AC2.5's exact external policy act;
this job neither writes GitHub environment configuration nor treats source CI as
public proof. The reviewer verifies the bounded queue and that an eligible master
job remains able to overwrite a preview.

