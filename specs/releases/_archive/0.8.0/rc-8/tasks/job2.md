# Job 2 — Publish one compatibility path and trustworthy repository routes

**Wave:** 2
**Waits on:** Job 1
**W:** `README.md`, `docs/getting-started.md`, `docs/compatibility.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md`, `CONTRIBUTING.md`, `SECURITY.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC2.1–AC2.5, AC3.1–AC3.5, AC4.1–AC4.2 | `README.md`, `docs/getting-started.md`, `docs/compatibility.md`, `mkdocs.yml`, `llms.txt`, `skills/rand-engine/SKILL.md`, `CONTRIBUTING.md`, `SECURITY.md` | Add one rendered Compatibility and migration guide with current package/CI/code facts: Python range versus tested set; core/Faker/PySpark/Java/platform requirements; Spark partitions and seed/features limits; 0.7→0.8 actions; and concise symptom/cause/recovery paths. Add repository-relative contribution guidance, Issues intake requirements and native private-vulnerability reporting after the main thread verifies it enabled. Link these canonical authorities from README, navigation, llms.txt and the skill. Preserve the Job 1 Agent command/output and six-starter versus five-tutorial distinction. Preserve direct runnable blocks and use existing docs/link/build checks; add no prose snapshot or new gate. |

Before J2.T1 merges, the main thread records verified GitHub private reporting
state. The existing docs harness, strict build and repository `verify:` are the
evidence; no documentation-only RED task exists because no missing executable
behavior is introduced by this job.
