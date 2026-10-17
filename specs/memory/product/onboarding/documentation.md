---
slug: documentation
title: Documentation site, llms.txt and agent skill
tldr: "Strict-built docs, README, llms.txt and an Agent Skill cover APIs, examples and use cases with executable code."
summary: "Zensical builds the repository's documentation from Markdown and public docstrings for the GitHub Pages target; README becomes the site home; rendered references cover the public API, returned writers and caller-facing errors; llms.txt indexes rendered guides, the skill and direct case files; and the suite checks semantic inventories, links and runnable Python blocks."
tags: [docs, site, llms-txt, agent-skill, readme]
sources:
  - docs/**
  - mkdocs.yml
  - llms.txt
  - README.md
  - skills/**
  - .github/workflows/docs.yml
---

## Site

- Zensical builds `mkdocs.yml` for the `https://marcoaureliomenezes.github.io/rand_engine/` GitHub Pages target. Mkdocstrings renders numpy-style docstrings; the main reference follows `rand_engine.__all__`, and separate destinations render the returned writer classes and the caller-facing exception family ([[public-api]], [[writers-and-streaming]]).
- Navigation: Home (the README, copied at build), Getting started, five Tutorials, How-to guides, a Reference group for the main API, returned writers and errors, Explanation and Benchmarks ([[benchmarks]]).
- Getting started maps all five packaged scaffolds to their command, filename, run command, prerequisite, observable outcome and tutorial. Each tutorial includes its case file verbatim, the same bytes `rand-engine get-started <slug>` writes ([[get-started-cli]]).
- The workflow copies `llms.txt` to the site root and the source Markdown tree beside rendered HTML in the Pages artifact.
- The docs workflow runs the strict build, which fails on a broken internal link, on pull requests to `development` and `master` and on pushes to `feature/**` and `master`; only a push to `master` uploads and deploys the Pages artifact. `site/`, `.cache/` and the generated `docs/index.md` are ignored build products.

## Landing README

- In order: the pitch, PyPI, Python, license and CI badges, install, a 30-second example, when to use it, the five get-started cases and the docs-site link; it links the agent skill and holds no method reference table.
- Faker is installed only as `pip install "rand-engine[faker]"`, here and in every docs page.

## llms.txt and the agent skill

- The root `llms.txt` links rendered guides and references, the agent skill and all five direct case files on the principal branch. Its site routes correspond to navigation destinations and its repository links resolve to existing files.
- `skills/rand-engine/SKILL.md` carries Agent Skills front matter (`name: rand-engine`, a `description` saying when to use it) and covers the complete catalog-backed method inventory, engine outcomes, the RandSpec grammar, builders, `pk`/`fk`, sinks, Spark, `rand-engine get-started` and errors ([[generation-methods]], [[rand-spec-grammar]], [[templates-and-examples]]). It lives in the repo, never in the wheel.

## Executed docs

- Runnable `python` blocks of the README, each Markdown page under `docs/` and the skill run in order in a temporary directory. A `python no-run` fence is reserved for the Kafka producer, each tutorial's case-file include and the skill's Spark blocks; separate contracts execute the packaged cases.
- Documentation contracts derive method parameters from `METHOD_CATALOG`, Spark outcomes from live validation, returned-writer and error inventories from their classes, factory inventories from the example classes, and scaffold names from `CASES`. README and `llms.txt` links resolve, and the strict site build validates internal routes.
