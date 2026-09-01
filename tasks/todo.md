# Curate SLA (swine) haplotypes (#143)

## Review

- **The issue's premise was half wrong, and the half that was right hid a
  live bug.** `haplotypes.yaml` did have swine entries -- keyed by MHC prefix
  as `SLA:`, not by latin name, which is why a search for "Sus scrofa" found
  nothing. But both entries wrote their member alleles *with* the species
  prefix (`SLA-1*01:01`), and the loader hands the parser the string after the
  species. So both haplotypes resolved carrying **zero alleles** and printed
  six warnings to stdout on every parse. Nothing read those warnings.

- **One of the two was also wrong on the data.** Table 2 of Baekbo et al. 2017
  (PMC5472656) gives Hp-2.0 as SLA-1*0201/*0701, SLA-3 *null*, SLA-2*0201. The
  entry read `SLA-3*02:01` -- the SLA-2 column filed one locus over. SLA-3*02:01
  is a real allele, so nothing could have complained.

- **The naming question the issue asks in step 3 has an answer in the
  literature.** Reiner et al. 2024 (PMC10925748) states the ISAG/IUIS-VIC
  scheme: swine haplotypes carry their own prefix, `Hp-` high resolution and
  `Lr-` low resolution, numbered `<class I>.<class II>` -- so `Hp-04.0` and
  `Hp-0.03` are the two halves of one animal's type, not variants. No
  `haplotype prefix` field is needed: the prefix is part of the name, and
  `Hp-17.0` and `SLA-Hp-17.0` both parse.

- **Curated all nine designated class I haplotypes**, not just the two:
  Hp-1a.0, 2.0, 4b.0, 6.0, 7.0, 17.0, 28.0, 32.0, 62.0, from the "Known
  haplotypes" half of Table 2. The same table's A.0-Z.0 rows are that study's
  own proposals resting partly on unnamed sequences, so they are left out.

- **Added the general guard.** Every one of the 71 curated haplotypes must keep
  every allele it lists. That is the test that would have caught this: the
  failure mode is a warning on stdout and a haplotype that claims a name and
  carries nothing.

- **Filed #162** for what could not be sourced: `Lr-` haplotypes are defined by
  allele *groups* (`SLA-1*15XX`, `Blank`), which the file format cannot express,
  and the class II `Hp-0.y` compositions are in a paywalled table.

- **Measured:** 0 of 36,752 corpus names change. 16,110 tests pass; restoring
  either wrong spelling fails the guard.
- Bumped to 3.51.0.
