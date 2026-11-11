# Job 1 — the speed gate's base partition (wave 1)

Runs beside Jobs 2, 3, 4 and 5 (disjoint `W:`). AC30.2 is read on the diff: `benchmarks/speed.py` is not in any `W:`.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | jr | AC30.1 | `tests/test_benchmarks.py` | `Fake` takes `bases=` like `heads=`; the parametrize at `:188-192` gains `bases=(1.0, 3.0, 3.0)`, `heads=(1.4, 1.5, 1.6)` expecting `"over 1.3x base: [('integers', 10)]"`. Green on arrival; reviewer check: `speed.py:311` back to `statistics.median` turns it red. Owner: itself |

Done when: `verify:`; `tests/test_benchmarks.py` passes; `git diff <base>...HEAD --stat` shows no `benchmarks/` path.
