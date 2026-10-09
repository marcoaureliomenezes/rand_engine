---
slug: rand-spec-grammar
title: RandSpec grammar
tldr: "A RandSpec maps output columns to a method, named kwargs and optional multi-column or transformer metadata, and is validated before generation."
summary: "AdvancedValidator validates NumPy common, correlated and key methods; CommonValidator validates the Spark common-method subset. Args and top-level constraints are refused, and validation collects issues into SpecValidationError."
tags: [spec, grammar, validation]
sources:
  - rand_engine/validators/**
---

## Shape

- A RandSpec is a non-empty dict keyed by output column name; `DataGenerator` also accepts a zero-argument callable returning one.
- Every column declares a string `method` and named `kwargs`. `args` is refused.
- Correlated multi-column methods declare `cols`; per-value callables may be declared in `transformers`. A `pk` column refuses transformers; an `fk` may transform its generated child values, but the embedded parent `pk` may not.
- Relations are ordinary `pk` and `fk` columns. A top-level `constraints` entry is refused with examples of the replacement grammar ([[pk-fk-constraints]]).

## Validation

- `AdvancedValidator` validates the ten common methods, four correlated methods and the two key methods for `DataGenerator`.
- `CommonValidator` validates the ten common methods for `SparkGenerator`; it refuses keys and positional args, and warns for correlated methods that Spark represents as null columns.
- Unknown kwargs, invalid types, ranges, date directives, column counts and key definitions are reported before generation.
- Every issue is collected into one `SpecValidationError`; warning-style helpers print the same issues and return a boolean.

## Key grammar

- A `pk` accepts only kwargs sufficient for another process to rebuild it: style, integer range inputs, optional permutation key and a constrained integer format.
- An `fk` embeds that parent `pk` spec and declares `parent_size` plus optional skew; parent transformers and out-of-domain sizes are invalid.
