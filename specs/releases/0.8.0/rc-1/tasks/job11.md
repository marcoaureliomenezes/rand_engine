# Job 11 — FR7 README landing page, CHANGELOG, llms.txt

**Wave:** 6 · **Waits on:** Job 8, Job 9, Job 10

- README is REBUILT as a landing page (reference -> landing): pitch, live shields badges, install, 30-second example, when to use it, the five cases, the docs-site link; the `derived-from` markers go, so the reconciliation pass leaves it alone. Method tables live on the site.
- Bug `faker-extra-undocumented-unpinned-install` closes inside the rebuild: every `pip install` in README/docs names only a declared extra.
- `CHANGELOG.md:10` `## [0.7.0] - Unreleased` becomes a dated header; the `## [0.8.0]` section lists this release's Added and Fixed entries. Bug `changelog-070-header-says-unreleased`.
- Evidence before merge: README links and `llms.txt` pages resolve only in the site build, so the task states a strict build in a scratch copy outside the repo tree (`cp -r <tree> $SCRATCH/site-check && cd $SCRATCH/site-check && cp README.md docs/index.md && zensical build --strict`), exit 0 handed to the reviewer; `docs.yml` repeats it on push to `feature/**`.
- `llms.txt` stays the one root file (deploy copies it); its links point at the site pages and the skill; `test_links_resolve[llms.txt]` stays.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J11.T1 | sr | AC7.1, AC7.2, AC7.3, AC6.2, AC5.5 | `tests/test_docs.py` | RED, one parametrized case per file under test with its own `xfail(strict=True)` marker (README T2, CHANGELOG T3, `llms.txt` T4), so each implementation task removes only its own: README section order and live badges, five slugs listed, site and skill links; no `pip install faker` and every `pip install` names a declared extra in README/docs; every `## [x.y.z]` carries an ISO date and `## [0.8.0]` exists; `llms.txt` links site pages. Owner: tests/test_docs.py |
| J11.T2 | sr | AC7.1, AC7.2, AC6.2 | `README.md`, `tests/test_docs.py` | REBUILD the README as the landing page; every python block still executes. Owner: tests/test_docs.py |
| J11.T3 | jr | AC7.3 | `CHANGELOG.md`, `tests/test_docs.py` | dated `0.7.0` header and the `0.8.0` section (Added, Fixed). Owner: tests/test_docs.py |
| J11.T4 | jr | AC5.5, AC6.2 | `llms.txt`, `tests/test_docs.py` | links to the site pages, the skill and the Markdown sources. Owner: tests/test_docs.py |
