# Job 6 — reconciliation and terminal evidence

**Status:** Approved

## Stage J6.S1 — RED

- Contract: after Jobs 4/5, exit executable-doc/public/benchmark-artifact tests fail by assertion under strict xfail markers; envelope `tests/test_docs.py tests/test_benchmarks.py tests/integrations/test_public_api.py`; ACs AC2.4, AC4.4, AC9.2, AC9.4.
- J6.S1.T1 — executable RC2 docs RED · AC9.2, AC9.4 · `W:` `tests/test_docs.py` · owner `tests/test_docs.py` · approved spellings/defaults, kwargs migration, batching and helper examples execute at light sizes.
- J6.S1.T2 — terminal benchmark artifact RED · AC2.4, AC4.4 · `W:` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · artifact must name final feature/base commits and satisfy distribution 1.5x/modifier 1.25x thresholds.
- J6.S1.T3 — final public boundary RED · AC9.2, AC9.4 · `W:` `tests/integrations/test_public_api.py` · owner `tests/integrations/test_public_api.py` · unsupported Spark features refuse; imports/dependency boundary unchanged.

## Stage J6.S2 — reconcile derived surfaces

- Contract: consume the authorized final-feature CI artifact, exit documentation/public/benchmark owners GREEN by marker deletion only, then full local verify/build/package checks; envelope `README.md llms.txt docs/** CHANGELOG.md tests/test_docs.py tests/test_benchmarks.py tests/integrations/test_public_api.py`; ACs AC2.4, AC4.4, AC9.2, AC9.4.
- J6.S2.T1 — rebuild executable docs and migration surfaces · AC9.2, AC9.4 · `W:` `README.md` `llms.txt` `docs/1_DATA_GENERATOR.md` `docs/2_SPARK_GENERATOR.md` `docs/3_WRITING_FILES.md` `docs/5_RECIPES.md` `CHANGELOG.md` `tests/test_docs.py` `tests/integrations/test_public_api.py` · owner `tests/test_docs.py` · generated examples use only synthetic data and current public names.
- J6.S2.T2 — record terminal performance proof · AC2.4, AC4.4 · `W:` `docs/benchmarks.json` `docs/BENCHMARKS.md` `tests/test_benchmarks.py` · owner `tests/test_benchmarks.py` · exact run/head/base and every new row; failure reopens owning job, never edits thresholds.

## Stage J6.S3 — enter closure

- Contract: after local verify, release check, build and package metadata are green, exit with the IMPLEMENTATION → CLOSURE milestone at the exact J6.S2 implementation SHA; envelope `specs/releases/0.7.0/_RELEASE.json`; ACs AC1.1–AC9.4 evidence index.
- J6.S3.T1 — main-thread closure transition · AC1.1–AC9.4 · `W:` `specs/releases/0.7.0/_RELEASE.json` · owner `tests/test_docs.py` · use only `release.py phase CLOSURE --sha <J6.S2-sha>` after all five bugs are resolved and every implementation gate is green.

## Stage J6.S4 — product-memory reconciliation

- Contract: in CLOSURE, exit with the exact `release.py drift` worklist reconciled, bug balance refreshed, catalog generated and one memory ledger entry; envelope `specs/memory/QUALITY.md specs/memory/product/** specs/releases/0.7.0/_RELEASE.json`; ACs AC1.1–AC9.4 current product truth.
- J6.S4.T1 — product-engineer memory pass in the same reconcile tree · AC1.1–AC9.4 · `W:` `specs/memory/QUALITY.md` `specs/memory/product/content/templates-and-examples.md` `specs/memory/product/generation/data-generator.md` `specs/memory/product/generation/generation-methods.md` `specs/memory/product/generation/spark-generator.md` `specs/memory/product/output/writers-and-streaming.md` `specs/memory/product/quality/benchmarks.md` `specs/memory/product/relations/pk-fk-constraints.md` `specs/memory/product/spec/rand-spec-grammar.md` `specs/memory/product/index.md` `specs/memory/product/catalog.json` `specs/releases/0.7.0/_RELEASE.json` · owner `tests/test_docs.py` · refresh the generated bug balance, DELETE/UPDATE/ADD only the drift-returned product atoms, leave any listed-but-unchanged atom byte-identical, regenerate index/catalog and call `release.py memory` with the exact reviewed/changed sets.

## Stage J6.S5 — terminal reconciliation

- Contract: exit closure narrative, disposition sweep, artifact GC, release check and doctor green in this one tree; envelope `specs/releases/0.7.0/_RELEASE.json`; ACs AC1.1–AC9.4 closure proof.
- J6.S5.T1 — main-thread terminal ledger evidence · AC1.1–AC9.4 · `W:` `specs/releases/0.7.0/_RELEASE.json` · owner `tests/test_docs.py` · record summary, size, drifts, test dispositions, dispositions, reviews and artifact-GC results through canonical writers; the reviewer then judges the complete reconcile HEAD once.
