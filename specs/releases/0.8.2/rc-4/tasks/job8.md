# Job 8 — `gen_uuid4` and the zero-row partition (wave 2)

Runs beside Jobs 5, 6 and 7. T1 first (both test tasks write `tests/test_0_np_core.py`: T1 then T2); T3 is independent of T2. Invariant 12, the operator's words: "Aprovo gen_uuid4 (Recommended)"; the approval is for `NPCore.gen_uuid4` by name, and no other `gen_*` body changes.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J8.T1 | sr | AC26.1, AC26.3 | `tests/test_0_np_core.py` | `test(J8.T1)`: `uuid4` and `int_zfilled` with size 0 return an empty Arrow column, added to the owning contract tests (`:192-212`, `:398-413`) as a partition. Green on arrival (`gen_uuid4(0)` already returns an empty array): the hand-back states it. The seeded golden `:412` and the golden at `tests/test_2_data_generator.py:596` run green on the old body first, output in the hand-back |
| J8.T2 | jr | AC21.3 | `tests/test_0_np_core.py` | `:399` states its contract instead of "AC4.5"; the "Pinned from 0.8.0" comment moves to the `_draw` test it describes (`:126`). Comments only; `test(J8.T2)` |
| J8.T3 | jr | AC26.1 | `rand_engine/core/_np_core.py` | `gen_uuid4` (`:132-140`): the hex step is `binascii.hexlify` in place of `bytes.hex().encode()`; output byte-identical for every seed. Keep the operator's style: 2-space indentation, one-line guards, terse NumPy; no other line of the file changes. Owner: the goldens above. Evidence in the hand-back: both goldens green on the new body; a 1M-row timing and `tracemalloc`/RSS peak of base against head from `benchmarks/speed.py` (the CI row is AC26.2, quoted at closure) |

Done when: `verify:`; `tests/test_0_np_core.py`, `tests/test_2_data_generator.py`, `tests/test_8_consistency.py` pass. Sweep: `git diff <base>...HEAD -- rand_engine/core/_np_core.py` shows changes inside `gen_uuid4` only.
