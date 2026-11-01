# Job 1 — package metadata: keywords, classifiers, Project-URLs (wave 1)

Runs beside Job 4 (disjoint `W:`). Ruling R3 (the exact keyword list) and R21 (the test is renamed) are carried by the RED task's `test(…)` body. The RED task precedes its implementation; they use separate trees.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J1.T1 | sr | AC6.1, AC6.2 | `tests/integrations/test_public_api.py` | RED, `test(J1.T1)` body names R3 and R21: the wheel METADATA test asserts `Project-URL` holds `llms.txt, https://marcoaureliomenezes.github.io/rand_engine/llms.txt` and `Agent skill, https://marcoaureliomenezes.github.io/rand_engine/skills/rand-engine/SKILL.md` beside the five current URLs; `test_wheel_keywords_are_the_fourteen_search_terms` (`:465`) is renamed to the seventeen and its exact list gains `data-generation`, `python`, `test-fixtures` (17 terms in all); the classifier assert (`:476-486`) gains `Topic :: Software Development :: Testing :: Mocking` and `Topic :: Software Development :: Libraries :: Python Modules`. Red today: none of the three is in `pyproject.toml`. The `:449` Documentation URL assert and `:459-462` stay as they are |
| J1.T2 | jr | AC6.1, AC6.2 | `pyproject.toml` | add the two `[project.urls]` entries (`llms.txt`, `Agent skill`, the URLs of J1.T1), the three keywords (in the order J1.T1's list gives) and the two classifiers; no other line changes (`:4` is Job 3's). Owner test: `tests/integrations/test_public_api.py` |

Done when: `verify:`; `tests/integrations/test_public_api.py` passes.
