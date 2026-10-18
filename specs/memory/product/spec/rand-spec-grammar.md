---
slug: rand-spec-grammar
title: RandSpec grammar
tldr: "A RandSpec maps output columns to a method, named kwargs and optional cols, transformers or modifiers, validated through one method catalog."
summary: "METHOD_CATALOG is the one authority for method names, parameters, types, engines and Arrow output types; AdvancedValidator validates every DataGenerator method and the Spark key subset, while CommonValidator owns ordinary Spark intake. Structure is checked before semantics, unknown column keys, positional args and top-level constraints are refused, and every issue is collected into one SpecValidationError."
tags: [spec, grammar, validation]
sources:
  - rand_engine/validators/**
---

## Shape

- A RandSpec is a non-empty dict keyed by output column name; `DataGenerator` also accepts a zero-argument callable returning one.
- A column is a dict with a string `method` and named `kwargs`. The accepted column keys are `method`, `kwargs`, `cols`, `transformers`, `null_rate`, `anomaly_rate` and `anomaly_values`; any other key, `splitable`, `sep` and `pk` included, is refused naming the accepted set, and `args` is refused with the instruction to pass named `kwargs`.
- Correlated multi-column methods declare `cols`; per-value callables may be declared in `transformers`. A `pk` column refuses transformers; an `fk` may transform its generated child values, but the embedded parent `pk` may not.
- Relations are ordinary `pk` and `fk` columns. A top-level `constraints` entry is refused with examples of the replacement grammar ([[pk-fk-constraints]]).
- Modifiers are sibling keys: `null_rate` and `anomaly_rate` are real numbers in `[0, 1]` (a bool is refused), and a positive `anomaly_rate` needs a non-empty list of scalar `anomaly_values`. They belong to ordinary single-column methods; `pk`, `fk`, the map methods and `complex_distincts` refuse them ([[generation-methods]]).

## Validation

- `METHOD_CATALOG` lists, per method, required and optional kwargs with types, the engines that run it, its kind (ordinary, correlated or key), its semantic rules and its Arrow output types. Validators, generation and the empty-file schema read it; no second registry exists.
- `AdvancedValidator` validates the fifteen ordinary methods, four correlated methods and two key methods for `DataGenerator`; `SparkGenerator` sends its extracted key subset through the same key semantics.
- `CommonValidator` validates ordinary columns for `SparkGenerator`; it refuses positional args, NumPy-only ordinary methods and modifiers with guidance to use `DataGenerator`, and warns for correlated methods that Spark represents as null columns. The Spark facade combines those errors with the advanced key errors before generation ([[spark-generator]]).
- A wrong type (a bool in a numeric slot included), a missing required kwarg or an unknown kwarg suppresses that column's semantic rules, so a bad type is reported as a validation issue and never as a raw `TypeError`.
- Semantic rules include: integer bounds inside `int_type`; an `int_zfilled` `length` within 1..18; a non-empty float grid with a finite span and `decimals` within the float limit; `true_prob` in `[0, 1]`; non-empty `distincts` pools and integer weights; supported date directives; positive `scale` and `a` greater than 1; `lam` within `[0, 10^6]`; immutable scalar `constant` values; non-empty map pools and levels, and `cols` equal to levels plus one for `distincts_multi_map`.
- On Spark, `uint64`, an `integers` width `max - min + 1` above 2^53 and an `int_zfilled` length above 15 are refused; the width test is the same predicate the Spark engine applies, so a Spark spec that validates never fails generation on width.
- Every issue is collected into one `SpecValidationError` whose message ends with a footer linking the docs site; warning-style helpers print the same issues and return a boolean.

## Key grammar

- A `pk` accepts only kwargs sufficient for another process to rebuild it: style, integer range inputs, optional permutation key and a constrained integer format.
- An `fk` embeds that parent `pk` spec and declares `parent_size` plus optional skew and `born_before`; parent transformers, extra parent keys and out-of-domain sizes are invalid. `born_before` has exactly the four event-time fields, finite builtin numeric starts and finite positive builtin numeric rates ([[pk-fk-constraints]]).
