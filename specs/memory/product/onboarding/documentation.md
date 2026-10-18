---
slug: documentation
title: Documentation site, llms.txt and agent skill
tldr: "Strict-built stable or preview docs, README, llms.txt and Agent guidance cover APIs, tutorials, compatibility, migration, support and security routes."
summary: "Zensical builds an isolated stable or immutable-source preview from Markdown and public docstrings for the GitHub Pages target; README becomes the site home; rendered references and five tutorials cover package use; one compatibility guide covers tested boundaries, migration and recovery; llms.txt indexes rendered guides, the mirrored canonical skill and all six starter resources; and canonical contribution and security files route support and private reports."
tags: [docs, site, llms-txt, agent-skill, readme]
sources:
  - docs/**
  - mkdocs.yml
  - llms.txt
  - README.md
  - skills/**
  - .github/workflows/docs.yml
  - scripts/docs_site.py
---

## Site

- Zensical builds `mkdocs.yml` for the `https://marcoaureliomenezes.github.io/rand_engine/` GitHub Pages target. Mkdocstrings renders numpy-style docstrings; the main reference follows `rand_engine.__all__`, and separate destinations render the returned writer classes and the caller-facing exception family ([[public-api]], [[writers-and-streaming]]).
- Navigation: Home (the README, copied at build), Getting started and Agent context, Compatibility and migration, five Tutorials, How-to guides, a Reference group for the main API, returned writers and errors, Explanation, a factual Comparison, Benchmarks, Contributing and Security ([[benchmarks]]).
- The comparison page uses primary sources to distinguish rand-engine, Faker and dbldatagen by execution model, output, relationship support and deployment fit. It separates the internal same-runner regression authority from one bounded CI observation whose two exact workloads, pins, runner, validation, raw samples, medians, setup costs and retained artifact are stated in full; it makes no universal speed, score, adoption, production-throughput or winner claim.
- Getting started maps the five runnable scaffolds to their command, filename, run command, prerequisite, observable outcome and tutorial. Each tutorial includes its case file verbatim, the same bytes `rand-engine get-started <slug>` writes; a separate Agent-context section explains the sixth starter and its `AGENTS.md` output ([[get-started-cli]]).
- Compatibility and migration is the canonical path for the package range versus tested Python set, optional Faker and caller-supplied Spark/Java requirements, platform and engine feature boundaries, concrete migration actions and symptom-to-recovery guidance.
- One preparation authority copies tracked source into a caller-owned build input and emits `llms.txt`, raw Markdown, starter resources and a byte-derived mirror of the canonical skill. The workflow renders the isolated input with Zensical and combines its HTML with those prepared resources; neither step mutates the tracked documentation tree.
- Stable preparation retains ordinary PyPI installation and principal-branch source routes. Preview preparation places a visible unreleased notice before guidance, binds core and Faker-extra installs plus own-project source routes to one immutable event-source archive, preserves third-party links and keeps skill front matter first.
- The docs workflow runs the strict build, which fails on a broken internal link, on pull requests to `development` and `master` and on pushes to `feature/**` and `master`. Only the exact stable and preview push refs may upload and enter the shared bounded Pages queue; preview deployment rechecks remote source identity and version state after acquiring the queue, while stale or unreadable state exits successfully with its reason. `site/`, `.cache/` and the generated `docs/index.md` are ignored build products.

## Landing README

- In order: the pitch, PyPI, Python, license and CI badges, install, a 30-second example, when to use it, five runnable starters plus the optional Agent context, and documentation and support routes; it links the skill and holds no method reference table.
- Stable source guidance installs Faker as `pip install "rand-engine[faker]"`; preview preparation rewrites the extra to the reviewed source archive. The copied Faker case carries no install command and points readers to Getting started.

## llms.txt and the agent skill

- The root `llms.txt` links rendered guides and references, compatibility and migration, canonical contribution and security files, the agent skill, the Agent context resource and all five runnable case files. Its site routes correspond to navigation destinations; preparation publishes the raw resources and generated skill mirror that machine readers follow.
- `skills/rand-engine/SKILL.md` carries Agent Skills front matter (`name: rand-engine`, a `description` saying when to use it) and covers the complete catalog-backed method inventory, engine outcomes, the RandSpec grammar, builders, event-time `pk`/`fk`, file and SQLite sinks, Spark key parity, normalized record streams, `rand-engine get-started` and errors ([[generation-methods]], [[rand-spec-grammar]], [[templates-and-examples]]). It points to compatibility, contribution and security authorities and explains the opt-in Agent starter without duplicating them. It lives in the repo, never in the wheel.
- `CONTRIBUTING.md` gives public setup, tests, strict docs build, a repeatable adoption sample and GitHub Issues intake. `SECURITY.md` sends potential vulnerabilities to GitHub's enabled private-reporting route and ordinary bugs to Issues, with no email, SLA or bounty.

## Executed docs

- Runnable `python` blocks of the README, each Markdown page under `docs/` and the skill run in order in a temporary directory. A `python no-run` fence is reserved for the Kafka producer, each tutorial's case-file include and the skill's Spark blocks; separate contracts execute the packaged cases.
- Documentation contracts derive method parameters from `METHOD_CATALOG`, Spark outcomes from live validation, returned-writer and error inventories from their classes, factory inventories from the example classes, and starter resource, filename and kind partitions from `CASES`. README and `llms.txt` links resolve, and the strict site build validates internal routes.
