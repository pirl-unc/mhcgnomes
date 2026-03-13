# Immutable Data Objects Refactor

## Goal

Replace the mutable `Serializable`-based parsed object model with immutable
Python dataclasses while keeping parsing, formatting, serialization helpers,
and CLI behavior as close to drop-in identical as possible.

This refactor is intended for a major release because it changes one important
runtime guarantee: parsed result objects can no longer be mutated in place.

## Scope

The refactor covers the objects that leave parser and tokenizer boundaries:

- `Result` and all parsed result subclasses
- `Species`
- `Token`
- `TokenizationResult`

The parser itself remains mutable because it owns internal transform caches.
That is not a data-object API and is intentionally out of scope for this pass.

## Constraints

These behaviors should stay the same:

- string parsing semantics
- `to_string()`, `compact_string()`, and `to_record()` outputs
- `to_dict()`, `from_dict()`, `to_tuple()`, `from_tuple()`, and `copy()` helpers
- public constructor signatures where practical
- sort/equality/hash semantics
- `Species.from_dict()` returning canonical singleton species objects

These behaviors are allowed to change in `3.0.0`:

- direct attribute mutation now raises instead of silently mutating cached data
- tokenizer attributes become read-only mappings
- cached `parse()` / `tokenize()` calls may return shared object identities
  because defensive copying is removed once the object graph is immutable

## Design

### Dataclass strategy

Use `@dataclass(frozen=True, init=False, eq=False, repr=False)` for the core
result objects.

Rationale:

- `frozen=True` gives strong immutability semantics
- `init=False` lets us preserve existing constructor signatures and computed
  fields instead of forcing dataclass-generated initializers on callers
- `eq=False` and `repr=False` preserve the existing custom equality, hash, and
  pretty-print logic

`slots=True` is intentionally not used because the package still supports
Python 3.9 and dataclass slots are only standard from Python 3.10 onward.

### Serialization strategy

`Serializable` goes away.

The `Result` base class keeps explicit implementations of:

- `to_dict()` / `from_dict()`
- `to_tuple()` / `from_tuple()`
- `copy()`
- `__str__()` / `__repr__()`

That preserves the existing serialization surface while decoupling it from the
third-party dependency.

### Species immutability

`Species` is only effectively immutable if its nested ontology structures are
also read-only.

This refactor freezes:

- `NormalizingSet` and `NormalizingDictionary` containers stored on `Species`
- nested list/set/dict values inside those containers
- exposed species metadata collections such as `other_common_names` and
  `other_mhc_prefixes`

Mutable construction still happens during ontology loading; freezing occurs when
`Species` objects are finalized.

### Cache strategy

After immutable results are in place:

- `Parser.parse()` no longer returns a defensive `deepcopy`
- `tokenize()` no longer returns a defensive `deepcopy`

That should preserve cache correctness while improving warm-cache performance.

## Implementation Order

1. Add the plan document and behavior-change contract.
2. Add freezing support to normalizing containers used by `Species`.
3. Convert `Result`, token objects, and parsed result classes to frozen
   dataclasses with explicit constructors.
4. Freeze `Species` nested ontology data during construction.
5. Remove defensive cache copies from parser/tokenizer.
6. Add or update tests for:
   - immutability
   - serialization helper parity
   - cache safety after copy removal
   - no regression in parser outputs
7. Bump the major version and document all observed behavior changes.

## Expected Behavior Changes

This section should remain exhaustive for the release.

1. Parsed objects are immutable. Direct attribute assignment now raises
   `FrozenInstanceError`.
2. `TokenizationResult.attributes` is now read-only and raises `TypeError` on
   in-place mutation.
3. `Species` ontology containers exposed on parsed objects are read-only and
   raise `TypeError` when mutated.
4. Repeated cached parses may return the same object identity instead of a fresh
   defensive copy.
5. The package no longer depends on `serializable`.
