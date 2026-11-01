# Job 2 — one `llms.txt` in the package, and `context7.json` (wave 2)

Waits on Job 1 (`tests/integrations/test_public_api.py`). R6 and R22 are carried here: the move is a `git mv` (`copy_input`, `scripts/docs_site.py:21`, copies only `git ls-files`), the published `/llms.txt` stays byte-equal, `.github/workflows/docs.yml:47` stays unchanged. The RED tasks T1 and T2 have disjoint `W:` and run together; T3 and T4 wait on them. `tests/AGENTS.md` matches the `tests:` glob, so it rides T1 and no implementation commit touches it.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J2.T1 | sr | AC6.3, AC6.4 | `tests/test_docs.py`, `tests/AGENTS.md` | RED, `test(J2.T1)` body names R6 and R22: every `llms.txt` consumer reads `ROOT / "rand_engine" / "llms.txt"` (the lines `:196`, `:201`, `:217` param, `:230`, `:420`, `:641`, `:877`, `:892`, `:936`, `:946`; `:911` is a test id and keeps its text), the publish test compares the site's `llms.txt` to that tracked file byte for byte, and `tests/AGENTS.md:8` names the new path. New test: `context7.json` at the root parses as JSON, `projectTitle` is `rand-engine`, `docs` is in `folders`, and `specs`, `tests`, `benchmarks`, `evals` are in `excludeFolders`. No assert is loosened; a path changes, nothing else. Red today: the new path does not exist |
| J2.T2 | sr | AC6.3 | `tests/integrations/test_public_api.py` | RED: the built-wheel test asserts `rand_engine/llms.txt` is in the wheel and its bytes equal the tracked `rand_engine/llms.txt`; the `:530-534` allowed-paths assert already admits `rand_engine/*`. Red today: the file is not in the package |
| J2.T3 | jr | AC6.3 | `llms.txt`, `rand_engine/llms.txt`, `scripts/docs_site.py` | `git mv llms.txt rand_engine/llms.txt` (content unchanged: Job 3 edits it); `scripts/docs_site.py:47` copies `input_root / "rand_engine" / "llms.txt"` to `public_root / "llms.txt"`; no other line changes. Sweep: `git grep -n 'llms.txt' -- . ':!specs' ':!CHANGELOG.md'` lists only the repointed consumers, the published-URL texts (`rand_engine/cases/agent.md.txt:25`, `skills/rand-engine/SKILL.md:8`, the workflow line) and `rand_engine/llms.txt` itself; cite it. Owner tests: `tests/test_docs.py`, `tests/integrations/test_public_api.py` |
| J2.T4 | jr | AC6.4 | `context7.json` | new file at the repo root: `projectTitle` `rand-engine`, `folders` `["docs"]`, `excludeFolders` `["specs", "tests", "benchmarks", "evals"]`, no other key; the registration with Context7 is the operator's. Owner test: `tests/test_docs.py` (J2.T1) |

Edges: T1 and T2 before T3; T1 before T4.

Done when: `verify:`; `tests/test_docs.py` and `tests/integrations/test_public_api.py` pass; the T3 sweep is quoted in its hand-back.
