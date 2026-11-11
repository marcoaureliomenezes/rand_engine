# Job 9 — the benchmark record (wave 2)

Waits on Jobs 2 and 4, the only jobs that touch a measured path (`rand_engine/file_handlers/`). Dispatched after their merges, on the `wt-rc` head the main thread pushed; the Benchmarks run id comes with the dispatch.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J9.T1 | jr | AC30.3 | `docs/benchmarks.json`, `docs/BENCHMARKS.md` | both files hold, byte for byte, the CI artifact of the Benchmarks run on that head (`benchmarks.md:44`), superseding run 43036665165; the commit adds only `docs/` and `tests/`. A red run is its own bug and returns to the main thread. Owner: the committed-artifact tests `tests/test_benchmarks.py:337-351` |

Done when: `verify:`; `tests/test_benchmarks.py` passes; the commit body names the run id.
