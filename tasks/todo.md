# Support the hyphenated class shorthand

Tracking issue: #104

## Review

- **The reported bug is real and now fixed.** `SLA-I`, `BoLA-I`, `HLA-I`,
  `DLA-I`, `Patr-I`, `Gaga-I` and `<prefix>-II` everywhere returned `None`,
  while `<prefix> class I` worked. Both spellings now give the same
  `MhcClass`, which is what a caller pulling MHC tokens out of curated text
  needs -- the reported failure was a sample silently ending up with no
  genotype.
- **But two of the issue's three claims do not hold**, and checking them was
  the point:
  - **`Mamu-I` is not a misparse.** It is a published macaque MHC class I
    locus: J Immunol 2000;164:1386, *"Mamu-I: A Novel Primate MHC Class I
    B-Related Locus with Unusually Low Variability"*, and the ontology declares
    the gene. The issue called it "wrong-but-plausible"; it is right. It stays
    a `Gene`.
  - **`H2-I` is a curated mouse haplotype**, `i`. The issue's observation that
    mouse literature also writes `H2-I` for the class II region is a genuine
    ambiguity in the source material, but the haplotype is what the ontology
    has evidence for, so it stays. Recorded in the test rather than silently.
- **So the shorthand is offered as a candidate, not a short-circuit.** Result
  sorting picks the `Gene` for `Mamu-I` and the `Haplotype` for `H2-I`, and the
  `MhcClass` everywhere else. `-II` is unambiguous for every species -- gene
  `II` resolves nowhere in the ontology -- so it works even for those two.
- **The digit spelling is deliberately left alone.** My first version mapped
  `<prefix>-1` as well, and the tests caught it: `SLA-1`, `BoLA-1` and `ELA-1`
  are real class I gene names. Mapping the digits would have shadowed genuine
  loci for some species and not others -- recreating the exact inconsistency
  this issue is about. `HLA-1` still returns `None`, as on `main`.
- **A sweep test guards the boundary**: gene `I` resolves for 12 species (the
  macaque group plus two others) and gene `II` for none, so a future addition
  cannot quietly take the shorthand away from a prefix that has it.
- **Measured:** 0 of 11,558 corpus names change -- no bundled corpus name uses
  the shorthand. 48 new tests; removing the shorthand fails 42 of them.
- Bumped 3.46.1 to 3.47.0: strings that returned `None` now parse.
