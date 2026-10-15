# Job 8 — FR5 the docs site (Zensical + mkdocstrings)

**Wave:** 4 · **Waits on:** Job 3, Job 5, Job 6

- Site shell: `mkdocs.yml` (nav Getting started, Tutorials x5, How-to = the existing guides `docs/1_...` to `5_RECIPES.md` kept as is, Reference, Explanation), mkdocstrings numpy handler, snippet include with the repo root as base path, anchor validation on, so `--strict` is also the link check (AC5.1; measured strict abort on a broken link).
- Tutorials hold no fenced python: each includes `rand_engine/cases/<slug>.py.txt` (AC5.3), so `test_docs` does not run them twice. Pages live under `docs/tutorials/` and `docs/*.md` without `python` fences except as the AC5.4 contract allows; `python no-run` stays reserved to the Kafka producer in `5_RECIPES.md`.
- Landing page: the workflow copies `README.md` to `docs/index.md` at build (gitignored); `llms.txt` and each page's `.md` are copied to the site root next to the HTML (Zensical emits HTML only; AC5.5).
- Zensical writes `site/` and `.cache/` inside the tree: both gitignored; the build runs only in `docs.yml`, never in `verify:` (measured 2.2 s; MkDocs-Material fallback 0.91 s on the same yml).
- `docs.yml` is born under FR2: top-level `contents: read`, job-level `pages: write` and `id-token: write` on the deploy job only, third-party actions SHA-pinned (AC2.2, AC2.3). Enabling Pages stays an operator act (AC5.7, no test: verified by the first deploy on `master`).
- `docs/5_RECIPES.md` is KEEP (ruling 6): moving its sections would move two existing asserts.
- Gate cost: strict build 2.2 s, in the docs workflow only.

| task | who | AC | `W:` | outcome |
|---|---|---|---|---|
| J8.T1 | sr | AC5.3, AC5.4, AC5.10 | `tests/test_docs.py` | RED: `docs/**/*.md` globbed recursively for python blocks; each tutorial includes its case file and the file exists; AC ids removed from the `test_docs.py` docstrings. Owner: tests/test_docs.py |
| J8.T2 | sr | AC5.2, AC5.1 | `mkdocs.yml`, `docs/getting-started.md`, `docs/explanation.md`, `docs/reference.md`, `.gitignore`, `tests/test_docs.py` | mkdocs.yml, Getting started, Explanation and Reference (`::: rand_engine.DataGenerator`, `SparkGenerator`, `RandSpecs`) pages; `.gitignore` gets `site/`, `.cache/`, `docs/index.md`. Owner: tests/test_docs.py (strict build runs in CI) |
| J8.T3 | jr | AC5.2, AC5.3 | `docs/tutorials/test-data.md`, `docs/tutorials/lake.md`, `docs/tutorials/kafka.md`, `docs/tutorials/databricks.md`, `docs/tutorials/faker.md`, `tests/test_docs.py` | five tutorial pages, each a short narrative plus the snippet include of its case file. Owner: tests/test_docs.py |
| J8.T4 | sr | AC5.1, AC5.5, AC5.7 | `.github/workflows/docs.yml` | PR to `development`/`master`: `zensical build --strict`; push to `master`: deploy to Pages; copies README to docs/index.md, `llms.txt` and page sources to the site root and checks `site/llms.txt` exists. No test (CI config; AC5.7 verified by the first deploy). Owner test: none, the strict build is the check |
