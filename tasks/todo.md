# Expose species provenance, and document the sharp edges

Tracking issues: #116, #117, #118

Three requests from downstream curation work, all one theme: the library knows
something it does not expose, so callers re-implement it badly.

## Specification

- [x] Expose whether a result's species was explicit in the input, inferred from
      a gene name, or taken from `default_species` (#116).
- [x] Add a parse flag that refuses a result whose species was not explicit.
- [x] Keep provenance out of result identity, and off the hot path.
- [x] Document `required_result_types` as the way to parse untrusted text, and
      say what each result type means (#117).
- [x] Add a species-compatibility helper and document that the species tree is
      nomenclature-shaped with a universal root (#118).
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- **#116**: `Result.species_source` returns `"explicit"`, `"inferred"`,
  `"default"` or `None`, with `Result.species_from_input` as the boolean form.
  The reporter asked for a bool but noted the three-way form would be more
  useful, and it is: their worst case was a curator writing the deliberately
  generic `MHC class II` and getting *Homo sapiens* — correct behaviour, and
  invisible. `"default"` names exactly that, and a bool could not.
- Determining the source needs both routes the parser uses to take a species
  off a string: an attached prefix (`Gaga-BLB2*02` tokenizes as one token) and
  leading species tokens (`mouse H2-Kb`, `Homo sapiens class I`). Neither alone
  is enough. `parse_species_from_prefix` is not usable for this on its own — it
  answers *Capra sp.* for `"MHC class II"` — but a false positive is harmless
  because the result's own species has to be in the matched set.
- Provenance is **not** an `__init__` field, so `init_field_names()` never sees
  it and equality, hashing, `repr` and `to_dict()` are untouched:
  `parse("HLA-A*02:01") == parse("A*02:01")` still holds while their sources
  differ. It is also computed lazily: an eager version cost 19% of cold parse
  throughput (0.080 vs 0.067 ms/name), which is not a reasonable price for
  something almost no caller reads. `parse` stores the two inputs and the
  property does the work on first access and memoizes.
- `require_explicit_species=True` refuses anything not explicit, and composes with
  `required_result_types`.
- The boolean is `species_from_input` rather than the `species_inferred` the
  issue suggested. `species_inferred` would have been true for both
  `"inferred"` and `"default"` while sharing a name with only one of them;
  `species_from_input` states the question a caller actually has and is the
  exact complement of `species_source == "explicit"`.
- **#117**: a README section on parsing untrusted input, showing
  `required_result_types` + `raise_on_error=False`, plus a table of what each
  result type means — the reporter lost time to `HLA-DR15` and `BoLA-DR`
  parsing fine while yielding no allele. Every example in the section is
  verified by running it; the first draft claimed `HLA-*02:01` was an
  `AlleleWithoutGene` and it does not parse at all, so the example is now
  `BoLA-D18.4`.
- **#118**: `Species.compatible_with` implements equal-or-direct-ancestor, and
  a README section covers the two sharp edges: `Gnathostomata sp.` is a
  universal root so "shares a common ancestor" accepts everything and fails
  open, and the tree is shallow where a species owns its MHC system, so
  `Primata sp.` is not an ancestor of *Homo sapiens* although it is of
  *Saimiri sciureus*.
- No behavioural change: 0 of 11,558 names in the bundled corpora parse
  differently. This PR only adds API and docs.
- Bumped 3.37.0 to 3.38.0.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,472 tests; 91% statement coverage).
