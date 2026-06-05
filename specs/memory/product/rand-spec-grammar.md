---
slug: rand-spec-grammar
title: RandSpec grammar
category: product
tldr: 'Declarative dictionary grammar validated by common and advanced validators before generation.'
summary: 'Current RandSpec grammar truth: common methods, advanced methods, transforms, constraints, lazy sizing, validation, and known validator/runtime drift.'
tags:
- spec
- validation
- grammar
agent_tier: self-pull
token_estimate: 150
last_updated: '2026-06-05'
release_origin: reset-specs-rebuild
---

## Visão geral

RandSpecs are declarative Python dictionaries describing output size, columns,
methods, method arguments, transformers, and constraints. `RandSpecs` examples
and templates provide reusable specs.

The grammar is validated by `CommonValidator` and `AdvancedValidator`.
Validation is a product boundary: a spec that validates should not fail because
the runtime lacks the method.

Current drift to resolve:

- `distincts_external` validates but is not implemented in the runtime method
  map.
- Some integer examples/validation refer to `dtype`, while runtime methods use
  `int_type`.
- Boolean examples/comments can mention `prob_true`, while runtime/validator use
  `true_prob`.
- Spark advanced grammar is mapped in runtime but returns null stubs.

Future grammar changes must update validators, runtime dispatch, docs, examples,
and tests together.
