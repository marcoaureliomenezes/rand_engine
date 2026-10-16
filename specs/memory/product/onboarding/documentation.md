---
slug: documentation
title: Documentation site, llms.txt and agent skill
tldr: "A strict-built GitHub Pages site, a landing README, a root llms.txt and an Agent Skill document rand-engine, and the suite executes their code."
summary: "The docs site at https://marcoaureliomenezes.github.io/rand_engine/ is built by Zensical from the repo Markdown and the public docstrings; README is a landing page that becomes the site home; llms.txt indexes site pages, the skill and the case files for agents; skills/rand-engine/SKILL.md teaches agents the RandSpec grammar. Every python block of the README, the docs pages and the skill runs in the suite."
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

- `https://marcoaureliomenezes.github.io/rand_engine/` is built by Zensical over `mkdocs.yml`, with mkdocstrings rendering the API reference from the numpy-style docstrings of the public surface ([[public-api]]); MkDocs-Material builds the same configuration as fallback.
- Navigation: Home (the README, copied at build), Getting started, five Tutorials (one per get-started case), How-to guides (data generator, Spark generator, writing files, keys, recipes), Reference, Explanation and Benchmarks ([[benchmarks]]).
- Each tutorial includes its case file verbatim, the same bytes `rand-engine get-started <slug>` writes ([[get-started-cli]]).
- The site serves `/llms.txt` at its root and each page's Markdown source beside its HTML.
- The docs workflow runs the strict build, which fails on a broken internal link, on pull requests to `development` and `master` and on pushes to `feature/**` and `master`; a push to `master` deploys the site to GitHub Pages. The working tree never holds a build: `site/`, `.cache/` and the generated `docs/index.md` are ignored.

## Landing README

- In order: the pitch, PyPI, Python, license and CI badges, install, a 30-second example, when to use it, the five get-started cases and the docs-site link; it links the agent skill and holds no method reference table.
- Faker is installed only as `pip install "rand-engine[faker]"`, here and in every docs page.

## llms.txt and the agent skill

- The root `llms.txt` lists site pages, the agent skill and the five case files for language models.
- `skills/rand-engine/SKILL.md` carries Agent Skills front matter (`name: rand-engine`, a `description` saying when to use it) and covers the RandSpec grammar, choosing a method, `pk`/`fk`, sinks, Spark, `rand-engine get-started` and errors ([[rand-spec-grammar]]). It lives in the repo, never in the wheel.

## Executed docs

- Every `python` block of the README, of each Markdown page under `docs/` and of the skill runs in order in a temporary directory; a `python no-run` fence is reserved to the Kafka producer and the tutorials' case includes.
- The skill's method table is checked against the method catalog, its Spark column against what validation does; README and `llms.txt` links must resolve.
