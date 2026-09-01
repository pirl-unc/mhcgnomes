# A haplotype locus that is positively absent (#162)

## Review

- **Built on the decision, not on my recommendation.** I had argued for waiting
  until the `Lr-` data is available, because the only consumer today is one
  row. The call was to build it now, so `Hp-2.0` says what its source says
  rather than recording it in a YAML comment.

- **Syntax follows the published notation.** Swine types are written
  "SLA-1*15XX or Blank", so a member is `<gene>*Blank` -- `null` accepted too,
  since Table 2 of PMC5472656 words it that way. Allele fields are numeric, so
  it cannot be confused with one.

- **The bug I predicted appeared, in the place I predicted.**
  `restrict_mhc_class` rebuilds a `Haplotype` from scratch, so a new field is
  what such a method forgets -- the #137 shape. It did not forget it; it
  filtered it with the wrong predicate. `is_valid_restriction` answers "may
  this restriction be applied at all" and returns **False** for `("Ia", "I")`,
  so `Hp-2.0 class I` kept its three class I alleles and lost its class I
  absent locus. The alleles beside them go through `restrict_alleles`, which
  uses a subtype table. Fixed with a `restrict_genes` twin sharing that table.

- **The serotype path needed a guard, not a pass-through.** The loader is
  shared with `Serotype`, and a serotype is a set of cross-reacting alleles
  rather than a locus map, so `Blank` says nothing there. It raises. A silent
  drop is how the swine haplotypes lost their alleles for years (#143).

- **The #143 guard was extended rather than relaxed.** "Every curated haplotype
  keeps every allele" now also requires every blank member to survive, so a
  blank cannot be quietly dropped either.

- **Not added to equality.** A haplotype's identity is its species and name --
  which is why `alleles` is not in `eq_field_names` either.

- **Verified:** reverting the `restrict_genes` call fails 2 tests. 16,439 tests
  pass. 0 corpus differences, since no bundled corpus name is a swine haplotype.
- Bumped to 3.59.0.
