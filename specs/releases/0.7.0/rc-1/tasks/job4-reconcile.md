# Job 4 — Reconciliation

**Status:** Approved

## Stage J4.S1 — readiness

- Contract: exit read-only evidence names the merged job heads, zero open rc-1 bugs, green owner tests, a final PR #42 artifact with every ratio ≤ 1.3, and the closure paths that need reconciliation; envelope empty (read-only); ACs all rc-1 ACs
- J4.S1.T1 — all rc-1 ACs · `W:` none (read-only evidence only) · owner `tests/test_docs.py`, `tests/test_benchmarks.py`, `tests/test_2_data_generator.py` · stop rather than changing the benchmark samples, repetition count, RNG contract or 1.3 limit

## Stage J4.S2 — reconcile

- Contract: exit memory describes shipped rc-1 behavior, derived documents agree, picked dispositions are terminal, the readiness checkpoint records no sampling-contract change, final PR #42 benchmark rows are all ≤ 1.3, and doctor is clean; envelope canonical memory, derived docs, ledgers and release state; ACs all rc-1 ACs
- J4.S2.T1 — all rc-1 ACs · `W:` `specs/memory/ARCHITECTURE.md`, `specs/memory/QUALITY.md`, `specs/memory/product/api/public-api.md`, `specs/memory/product/generation/data-generator.md`, `specs/memory/product/generation/generation-methods.md`, `specs/memory/product/generation/spark-generator.md`, `specs/memory/product/output/writers-and-streaming.md`, `specs/memory/product/relations/pk-fk-constraints.md`, `specs/memory/product/spec/rand-spec-grammar.md`, `specs/memory/product/index.md`, `specs/memory/product/catalog.json`, `README.md`, `llms.txt`, `docs/benchmarks.json`, `docs/BENCHMARKS.md`, `specs/releases/0.7.0/_RELEASE.json`, `specs/bugs/BUGS.jsonl`, `specs/bugs/_archive/bugs_histo.jsonl`, this file (`done`) · owner `tests/test_docs.py`, `tests/test_benchmarks.py`, `tests/test_2_data_generator.py` · run the closure memory protocol; record run 37416658724 as same-code noise without changing samples, repetitions, RNG or limit; commit the final green artifact; sweep dispositions, archive eligible bugs and record artifact GC
