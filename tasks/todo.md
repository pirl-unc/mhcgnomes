# Refuse to read a non-MHC gene name as a locus plus an allele

Tracking issue: #133

## Specification

- [x] Verify the five reported symbols against HGNC before adding them.
- [x] Move the curated non-MHC table where both consumers can reach it.
- [x] Stop the parser splitting such a name into a locus plus a suffix.
- [x] Keep every name in that table that IS a declared gene parsing.
- [x] Measure against a worktree of `main`.

## Review

- **Two of the five were the dangerous kind.** `Kdm5d` under a mouse species
  parsed as `H2-K*dm5d` and `Daxx` as `H2-D*axx` -- the real mouse loci `K` and
  `D`, with everything after them read as an allele. Both look syntactically
  valid and get dispatched onward, so the false positive is silent. The other
  three returned `None` from `parse_gene_class` rather than saying `non_mhc`.
- **The table moved to `mhcgnomes/non_mhc_genes.py`.** It lived in
  `function_api.py`, but the misparse happens in `parser.py`, and importing
  the one from the other is backwards. The normalizer moved with it and is the
  same rule `parse_gene_class` already used, so nothing about its behaviour
  changes.
- **The guard is narrow, and had to be.** 13 of the 17 pre-existing entries --
  `TAP1`, `TAPBP`, `B2M`, `RING4`, `PSF1`, `TAP-L` and friends -- are real
  declared genes that must keep parsing. So the parser refuses a name only when
  the species does not declare it. A test asserts the invariant that makes this
  safe: none of the five reported symbols is declared by any of the 672 species,
  so refusing them cannot shadow a locus.
- **Sources cited.** All five are HGNC-approved symbols, checked against
  `rest.genenames.org` rather than assumed: `ARHGAP45` HGNC:17102,
  `ATP6V1G2` HGNC:862, `COL11A2` HGNC:2187, `DAXX` HGNC:2681, `KDM5D`
  HGNC:11115. Three of them lie inside the MHC region, which is why they turn
  up in these downloads at all.
- **One test of mine was wrong, not the code.** It expected bare `Kb` to parse;
  it returns `None` on `main` too, because a bare mouse locus needs a species.
  Checked against a worktree rather than assuming the guard had caused it.
- **Measured:** 0 of 11,558 corpus names change. 32 new tests, verified by
  mutation -- removing the guard fails 6 of them.
- Bumped 3.43.2 to 3.44.0: five inputs that returned a confident wrong answer
  now return `None`, which is a behaviour change even though it is a fix.
