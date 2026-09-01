# Do not assign a species to a gene symbol shared across lineages (#130)

## Review

- **The rule.** `Parser.parse_gene_without_species` ranked every species that
  declares a digit-bearing gene name and returned the one with the longest gene
  list. That was written for `BLB2`, whose two declarers are `Galliformes sp.`
  and its own descendant `Gallus gallus`. Applied to `DRB1` it ranked 45
  unrelated declarers and returned *Macaca fascicularis*. The ranking now runs
  only when the declarers lie in a single lineage; otherwise the name names no
  species, per #108.

- **`BF2` was the one real casualty, and it is real.** IEDB publishes chicken
  alleles under the bare form -- `BF2*2101` (82 assay entries), `BF2*0401`
  (33), `BF2*1301` (30), and more. But GenBank EU430728.1 and EF643463.1 are
  both "Numida meleagris MHC class I antigen (BF2) mRNA", so the guineafowl's
  BF2 is not a curation error either and could not just be deleted.

  Resolved with the `context only` property #113 added: the guineafowl declares
  BF2, `NumiMele-BF2` resolves, and the bare form stays with the chicken. The
  attested side gets the bare name, the same rule AGENTS.md states for prefixes.

- **My corpus was lying to me.** The 25,200-name set I had been measuring
  against did not include `tests/iedb_allele_counts.csv` or the bundled
  netMHCpan lists. It reported 0 differences for this change while 17 tests
  failed, nearly all of them BF2. Rebuilt to 36,752 names; the rebuilt corpus
  showed the 8 BF2 forms immediately.

- **A pre-existing provenance bug, found on the way.**
  `infer_species_from_prefix` falls back to a gene name unique to one species
  and returns an empty matched string to say nothing in the input matched.
  `species_named_in` counted it anyway, so `species_source` reported
  **"explicit"** for `A8*01:01`, and `require_explicit_species=True` -- whose
  entire job is rejecting an inferred species -- accepted it. 98 gene names
  took that route. Fixed by honouring the sentinel.

- **Filed #160** for the reason `Ia1` can no longer resolve: the tokenizer
  lower-cases before `declares_gene_with_same_case` is ever consulted, so the
  case-aware ranking key the code comments describe has never fired in the
  normal path.

- **Measured:** 0 of 36,752 corpus names change. 16,011 tests pass. Reverting
  either mechanism fails 9 of the new tests.
- Bumped to 3.50.0.
