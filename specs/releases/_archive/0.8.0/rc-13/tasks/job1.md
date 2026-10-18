# Job 1 — Final maintenance sources

**Wave:** 1
**Waits on:** —
**W:** `.github/workflows/auto_tag_publish_development.yml`,
`.github/workflows/auto_tag_publish_master.yml`,
`.github/workflows/pr_to_development.yml`,
`.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml`,
`skills/rand-engine/SKILL.md`, `docs/comparison.md`

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | jr | AC1.1–AC1.2 | `.github/workflows/auto_tag_publish_development.yml`, `.github/workflows/auto_tag_publish_master.yml`, `.github/workflows/pr_to_development.yml`, `.github/workflows/pr_to_master.yml`, `.github/workflows/test_on_push.yml` | In each and only each named file, replace `actions/setup-java@cf277c60eb25467037889841efdb72551f06f6c3 # v4` with `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961 # v5.7.0`. Preserve every surrounding byte: Temurin, Java 17, cache behavior, triggers, permissions, matrices, commands and gates. No test: a literal-pin assertion would mirror implementation; native CI is the later behavioral proof. |
| J1.T2 | jr | AC2.1–AC2.2 | `skills/rand-engine/SKILL.md` | Delete only “The starter begins in 0.8.0 and is not in the published 0.8.0rc4 wheel.” Preserve the command, generated-file boundary and existing-file guidance. Replace only “After unchanged normalization, every microbatch converts to pandas records, preserving public Python values.” with “Each microbatch converts to pandas records, preserving public Python values.” Preserve all remaining stream guidance. No test change: the existing documentation contracts already protect the skill structure and mirror, while a phrase assertion would not protect product behavior. |
| J1.T3 | jr | AC3.1 | `docs/comparison.md` | Replace only the four-component dotted Java version in the observed-environment paragraph with `Java (version components: 17, 0, 20, 1)`. Preserve every other guide byte, including workload, pins, samples, validation, limitations and non-ranking claims. No test: this is a lossless documentation-format correction and a text assertion would mirror it. |

The three tasks have disjoint write sets and may run in parallel. They are
fully stated `jr` tasks; the documented senior fallback may execute them
unchanged because the installed junior model is unsupported for this account.
The unchanged official job merge performs repository verification. Native CI
after candidate publication supplies AC1.3; it is not a task-local pre-merge
gate. AC4 belongs to PE reconciliation and is not an additional job task.
