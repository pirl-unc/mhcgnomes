# Curate the published water buffalo loci

Tracking issues: follow-up to #109 / #115 (both closed as not-a-bug)

Those two issues asked whether `Bubalus bubalis` belongs under `Bos sp.`
It does -- the tree is prefix scope. But checking the literature to answer
that turned up a real gap: the entry did not record the loci the buffalo
papers actually characterize.

## Specification

- [x] Declare on `Bubalus bubalis` the class II loci with published buffalo
      sequences, with sources cited next to each.
- [x] Stop the cattle `DRB -> DRB3` alias renaming the buffalo locus, since
      the literature reports homology rather than identity.
- [x] Leave inherited cattle loci reachable.
- [x] Decide, from IPD-MHC rather than one paper, whether `BoLA-DQB3` and
      `BoLA-DQB4` should exist.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- Declared `DRA`, `DRB`, `DQA2` in addition to the existing `DQA`, `DQA1`,
  `DQB`. All were previously inherited from `Bos sp.`, which parsed them but
  recorded no evidence that the buffalo locus itself had been characterized.
  Sources: PMID 12580780 (buffalo DRA and DRB, eight Bubu-DRB alleles across
  four breeds), PMID 22383896 (cites isolation of buffalo DQA1 and DQA2
  cDNAs), and IPD-MHC, which holds 39 Bubu-DQA alleles.
- **`Bubu-DRB` no longer renames to `Bubu-DRB3`.** `gene_aliases.yaml` maps
  `DRB -> DRB3` under `BoLA`, which is right for cattle, where DRB3 is the
  expressed DRB locus, and buffalo inherited it. PMID 22383896 says only that
  "the Bubu-DRB sequence showed maximum homology with the BoLA-DRB3*0101
  allele of cattle" -- homology, not identity -- and every paper writes the
  locus as Bubu-DRB. Declaring `DRB` on the species stops the rename;
  `Bubu-DRB3` still parses by inheritance.
- **`BoLA-DQB3` and `BoLA-DQB4` deliberately not added.** A trans-species
  phylogeny paper assigns buffalo sequences to loci it labels `BoLA-DQB1`,
  `BoLA-DQB3` and `BoLA-DQB4`, but IPD-MHC registers only `BoLA-DQB`. Those
  are that analysis's locus labels rather than designations. A test pins their
  absence so the distinction is not lost.
- Also added the prefix-scope explanation as a comment on the entry itself,
  since it is the specific line two people have now filed bugs against.
- No behaviour change on real data: 0 of 11,558 names in the bundled corpora
  parse differently. The `Bubu-DRB` rename is the only behavioural change and
  no corpus name exercises it.
- Bumped 3.38.0 to 3.39.0 -- minor rather than patch, because `Bubu-DRB` now
  returns a different gene name.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,507 tests; 91% statement coverage).
