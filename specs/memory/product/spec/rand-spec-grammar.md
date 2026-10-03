---
slug: rand-spec-grammar
title: RandSpec grammar
tldr: "A RandSpec is a dict of column name to {method, kwargs or args, cols, transformers}, validated before any row is generated."
summary: "The declarative grammar both generators read; AdvancedValidator judges DataGenerator specs (common and correlated methods plus constraints), CommonValidator judges SparkGenerator specs (common methods only); every issue is collected and raised as one SpecValidationError with a corrected example."
tags: [spec, grammar, validation]
sources:
  - rand_engine/validators/**
---

## Shape

- A RandSpec is a plain dict keyed by output column name; a generator also accepts a zero-argument callable returning one.
- A column entry carries `method` (a method name string, never a callable), and exactly one of `kwargs` (dict, the recommended form) or `args` (list or tuple, validated only for shape).
- `cols` names the output columns of a multi-column method ([[generation-methods]]); `transformers` is a list of per-value callables applied in order ([[data-generator]]).
- A top-level `constraints` key declares PK/FK relations ([[pk-fk-constraints]]); only `DataGenerator` reads it.

## Validation

- Each generator validates at construction: `DataGenerator` through `AdvancedValidator.validate_and_raise`, `SparkGenerator` through `CommonValidator.validate_spark_and_raise`.
- Each validator holds a `METHOD_SPECS` catalog: description, required and optional parameters with types, allowed values and a working example per method.
- The validator checks the spec is a non-empty dict, each column is a dict with a known method, parameter names and types, the `cols` count of multi-column methods, transformer callability and the constraint fields.
- Every issue in a spec is collected, then raised together as one `SpecValidationError`; each message shows a corrected example.
- `validate_with_warnings` / `validate_spark_with_warnings` print the same issues and return a bool instead of raising.
