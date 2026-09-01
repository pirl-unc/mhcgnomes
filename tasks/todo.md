# Prevent Tasmanian-devil ambiguity labels from becoming `Pair`

GitHub issue: #186

## Evidence and intended behavior

- [x] Check the current IPD-MHC release rather than inferring registry coverage
  from search results. IPD-MHC 3.17.0.0 (2026-07-26; 12,833 entries) contains
  zero entry names beginning `Saha` and zero entries whose organism contains
  `Sarcophilus`.
- [x] Check primary literature for the nomenclature. `SahaI*NN` is an attested
  author-used convention: Siddle et al. deposited `SahaI*27`--`*85`
  (PMID 20219742), and Caldwell et al. use `SahaI*49/82` and `SahaI*74/88`
  (PMCID PMC6092122). This is literature usage, not an IPD-MHC registration.
- [x] Check the underlying records. The candidate designations correspond to
  GenBank GQ411457 (`SahaI*49`), GQ411490 (`SahaI*82`), GQ411482
  (`SahaI*74`), and JN389436 (`SahaI*88`). Caldwell's source-data FASTA has
  one sequence for each slash label, so neither label denotes two paired MHC
  molecules.
- [x] Keep both candidates gene-unassigned. Caldwell explicitly labels
  `SahaI*74/88` unassigned, and the compound labels do not justify promoting
  either candidate to a particular locus.

## Implementation

- [x] Recognize only the two published Saha compound labels as allele-name
  ambiguity, independent of the optional alias-resolution flag.
- [x] Keep ordinary slash parsing unchanged, especially the common class-II
  alpha/beta `Pair` case.
- [x] Replace incorrect "IPD-style" / "IPD entries" prose with citations to
  Caldwell's paper, source-data FASTA, and the four GenBank accessions.
- [x] Add regression tests for both spellings (`SahaI` and `Saha-I`), both
  alias settings, gene-unassigned members, class-I context, and non-creation
  of `Pair`.
- [x] Add a non-regression test for a genuine class-II alpha/beta pair.
- [x] Run `./format.sh`, `./lint.sh`, and `./test.sh`.

## Review

- IPD-MHC 3.17.0.0 was checked directly: 0 `Saha` entry names and 0
  *Sarcophilus* organisms. The nomenclature is nevertheless attested by Siddle
  et al. (PMID 20219742), Caldwell et al. (PMCID PMC6092122), Caldwell's
  one-record-per-label source FASTA, and GenBank GQ411457/GQ411490/GQ411482/
  JN389436.
- Both `SahaI*49/82` and `SahaI*74/88` now return `AmbiguousAlleles` containing
  two gene-unassigned class-I candidates with aliases either off or on. The
  parser never constructs a `Pair` from the source's `I` placeholder.
- The exception is deliberately source-specific. An invented `SahaI*49/74`
  stays unresolved; ordinary HLA class-II alpha/beta slash notation still
  returns `Pair`. The broader alias-based ambiguity conversion was removed.
- `./format.sh` passed; `./lint.sh` passed; all 17,143 tests passed with 92%
  coverage. Bumped to 3.64.2.
