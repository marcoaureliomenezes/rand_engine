# Job 1 — Correct the current stream release note

**Wave:** 1
**Waits on:** —
**W:** `CHANGELOG.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | jr | AC1.1–AC1.3 | `CHANGELOG.md` | Replace only the false current 0.8.0 `stream_dict` bullet with a truthful statement of one normalized pandas `DataFrame.to_dict("records")` conversion. Remove Arrow eligibility, conversion and fallback claims; do not add behavior, performance or compatibility claims. Preserve the `Unreleased` header and every other changelog byte. No test: this is reversible low-impact prose and a text-mirroring test would not protect a product contract. Before commit, compare the wording semantically with `DataGenerator.stream_dict`, the approved rc-10 replacement and the data-generator memory atom; inspect the diff to prove `CHANGELOG.md` is the only write. |

The fully stated task is assigned to `jr`. The documented senior fallback may
execute it without changing its scope, model configuration or this task's
single-file ownership. The unchanged official merge verify is the only
automated gate; this job does not run or duplicate it locally.
