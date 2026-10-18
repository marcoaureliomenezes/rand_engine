# Job 2 — Build the bounded comparison harness

**Wave:** 2
**Waits on:** independently verified stable 0.8.0 publication evidence from the
main thread
**W:** `benchmarks/comparison.py`, `benchmarks/comparison-requirements.txt`,
`tests/test_comparison.py`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1–AC2.7 | `tests/test_comparison.py` | RED first. Add focused behavior tests for a missing comparison runner using only standard-library module imports and explicit factories. Prove both literal workload definitions, one warm-up per side, exact AB/BA/AB order, full Python and Spark contract validation, median derivation from raw samples, separate setup/validation timing, required provenance/plan/artifact fields, and rejection of winner/score/threshold fields. Prove the protected internal benchmark paths are byte-identical to this job's base. No timing target, comparator import at collection time, editable-package assumption, YAML-text mirror or test of exact random values. |
| J2.T2 | sr | AC2.1–AC2.7 | `benchmarks/comparison.py`, `benchmarks/comparison-requirements.txt` | GREEN after J2.T1. Implement the sole runner and a dedicated direct-pin requirements authority: Faker 28.4.1, dbldatagen 0.4.0.post1, PySpark 3.5.8, setuptools 83.0.0, jmespath 1.0.1 and pyparsing 3.2.5. Generate versioned JSON and derived Markdown for exactly the approved 100,000-record Python and 1,000,000-row/eight-partition Spark contracts; install/import/session setup and validation remain outside timed samples. Require an installed public `rand-engine==0.8.0` wheel identity, report pip/wheel/distribution/runner/Java/Spark metadata, raw samples, medians, schemas, validations and physical plans. Do not edit the protected benchmark paths, runtime dependencies or lockfile. Run J2.T1 GREEN. |

`J2.T1` must merge before `J2.T2`. The runner's local contract tests never
execute the comparator workloads or add their dependencies to the normal pytest
environment; the first full execution belongs to Job 3's isolated Actions run.
