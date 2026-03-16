# Species Identity Proposal

## Summary

This proposal makes `latin_name` the canonical identity for every `Species`
object and treats prefixes, common names, historic prefixes, and source-local
codes as aliases rather than as identity.

The main reason is collision handling. Today, bare prefixes can map to multiple
species and runtime lookup resolves that ambiguity with a heuristic. That is not
stable enough for a curated ontology.

## Current Problem

The repo already uses scientific names as the top-level keys in
`mhcgnomes/data/species.yaml`, but runtime lookup still conflates:

- canonical identity
- user-facing display prefix
- legacy aliases
- source-local external codes

This shows up in a few places:

- `Species.name` currently stores the scientific name, but that is not exposed
  explicitly as `latin_name`.
- `Species.get()` accepts prefixes, common names, and scientific names through a
  shared alias table.
- ambiguous aliases are sorted with `create_species_sort_key()` instead of being
  treated as ambiguous input.
- side tables such as `gene_aliases.yaml` are keyed by a mix of canonical
  prefixes and legacy identifiers rather than one stable species key.

The result is that collisions are handled as lookup accidents instead of as a
first-class ontology concern.

## Goals

- Make canonical species identity explicit and stable inside the codebase.
- Stop silently resolving colliding species aliases.
- Preserve parsing for unambiguous prefixes and common names.
- Keep normalized output based on the curated MHC prefix, not the scientific
  name.
- Allow a staged migration with minimal immediate breakage.

## Non-Goals

- Full taxonomic authority management or synonym history.
- Reworking allele or gene ontology beyond species identity boundaries.
- Changing the public normalized string format from `HLA-A*02:01` style output
  to scientific-name output.

## Proposed Model

### Canonical identity

Use scientific name as the canonical species key everywhere inside the runtime
model.

Proposed `Species` contract:

- `Species.latin_name`: canonical identity field
- `Species.name`: compatibility alias for `latin_name` during migration
- `Species.prefix`: curated primary runtime MHC prefix
- `Species.other_mhc_prefixes`: non-primary runtime prefixes
- `Species.old_mhc_prefix`: historic display/parse prefix
- `Species.common_name` and `Species.other_common_names`: human-oriented aliases

The important change is semantic, not cosmetic: prefixes stop being identity.

### Alias resolution

Split exact canonical lookup from alias lookup.

Proposed API shape:

- `Species.get_by_latin_name(latin_name) -> Species | None`
- `Species.get_multiple(query) -> tuple[Species, ...]`
- `Species.resolve_alias(query) -> tuple[Species, ...]`
- `Species.get(query) -> Species | None`

Behavior of `Species.get()` after migration:

- exact scientific name: return that species
- unique alias: return that species
- ambiguous alias: return `None` or raise a dedicated ambiguity error

The current heuristic winner-selection should be removed for ambiguous aliases.

## Parser Behavior

### Species-only parsing

When the input is just a species token:

- `HLA` should still parse as human because it is unique
- `Human` should still parse as human because it is unique
- a colliding token such as `Bubu` should not silently pick a species

### Species plus downstream context

Parser code should still be allowed to use downstream evidence to disambiguate.
For example:

- if an alias maps to multiple species but only one candidate contains the
  observed canonical gene or gene alias, resolve to that species
- if more than one candidate still fits, return ambiguity rather than choosing
  by number of curated genes

This preserves practical parsing while making collisions explicit.

### Default species

`default_species` should accept:

- `Species`
- scientific name
- unique alias

Internally it should normalize to canonical `latin_name` as early as possible.

## Data File Changes

### `species.yaml`

Keep the file keyed by scientific name. That is already the right shape.

Recommended schema clarification:

- `prefix`: primary runtime prefix
- `old prefix`: historic prefix
- `other prefixes`: additional accepted runtime aliases
- `name`: common name or list of common names

No top-level entry should be keyed by prefix.

### Alias-bearing runtime YAML

Files currently keyed by species alias should move toward canonical
scientific-name keys:

- `gene_aliases.yaml`
- `allele_aliases.yaml`
- `known_alleles.yaml`
- `haplotypes.yaml`
- `serotypes.yaml`
- `heterodimers.yaml`
- `supertypes.yaml`

Migration rule:

1. Canonical key is scientific name.
2. Loader temporarily accepts legacy prefix keys for backward compatibility.
3. Validation rejects ambiguous non-scientific-name keys once a collision exists.

This eliminates the current need to combine side tables by trying every
identifier associated with a species.

### Source registry

`underrepresented_taxa_source_registry.yaml` should also move away from
prefix-keyed entries. Prefix-keyed registry data becomes awkward exactly where
we most need it: collisions.

Recommended shape:

- top-level keyed by scientific name
- explicit `primary_prefix`
- optional `other_prefixes`
- optional `colliding_external_prefixes`

That keeps the curation record aligned with runtime identity.

## Runtime Data Structures

Introduce separate lookup indexes:

- `latin_name_to_species`
- `alias_to_species_objects`
- `prefix_to_species_objects`
- `common_name_to_species_objects`

This keeps the distinction between canonical identity and lookup aliases
visible in code instead of collapsing everything into one bag of identifiers.

`Species.all_identifiers` can remain as a convenience helper, but runtime logic
should stop depending on it for identity-sensitive operations.

## Serialization Changes

`to_record()` and any tabular output should expose scientific name explicitly.

Recommended record fields:

- `species_latin_name`
- `species_prefix`
- `species_common_name`

For compatibility, `species_name` can temporarily remain as an alias of
`species_latin_name`, but new code should stop relying on that ambiguity.

## Migration Plan

### Phase 1: Make identity explicit

- add `Species.latin_name`
- add `Species.get_by_latin_name()`
- add tests that canonical lookup is scientific-name-based
- leave existing prefix parsing behavior in place for unique aliases

### Phase 2: Separate alias resolution from identity

- add explicit alias-resolution helpers
- remove heuristic winner selection from `Species.get()` and
  `infer_species_from_prefix()`
- return ambiguity for colliding bare aliases

### Phase 3: Migrate runtime side tables

- convert YAML files to scientific-name keys
- keep temporary loader support for legacy prefix keys
- add validation that new entries use scientific names

### Phase 4: Tighten public behavior

- deprecate any API behavior that depends on heuristic alias resolution
- update docs and examples to prefer scientific-name-based internal references

## Test Plan

Minimum tests to add:

- exact scientific name lookup returns the canonical species
- unique prefix lookup still works
- ambiguous prefix lookup does not silently choose a species
- parser can disambiguate an ambiguous alias when downstream gene context makes
  only one species valid
- parser returns ambiguity when both species and downstream tokens remain
  compatible
- side-table loading by scientific name matches current behavior for existing
  unambiguous species

## Compatibility Notes

This proposal does not require changing normalized output strings. End users can
continue to see `HLA`, `BoLA`, `Gaga`, and similar curated prefixes in rendered
names.

The internal change is that scientific name becomes the primary key and aliases
become parse helpers.

## Open Questions

1. Should ambiguous alias lookup return `None` or raise a dedicated
   `AmbiguousSpeciesError`?
2. Should `Species.name` remain indefinitely as a synonym for `latin_name`, or
   should it eventually be deprecated?
3. Should parent/child species inheritance continue to merge alias-bearing side
   tables across all identifiers, or should that merge become strictly
   scientific-name-based once the YAML migration is complete?
