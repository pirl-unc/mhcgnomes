# Add the nine HLA class I gene fragments (#113)

## Review

- **The issue's premise had gone stale, and my own reading of it was wrong.**
  Fourteen of the nineteen genes it lists were added by #114 and already parse.
  What remained were the nine class I fragments `N R S T U W X Y Z`, which
  `species.yaml` deliberately held back with a comment giving two reasons.

- **I had recorded that these nine have no alleles. They do.** IPD-IMGT/HLA
  3.65.0 `Allelelist.txt` (2026-07-14) gives W 13, T 9, S and U 7 each, N 5,
  Y 3, R 2 -- only X and Z have none. So `HLA-W*01:01:01:01` is a real allele
  name that should parse, and a blanket "these name no alleles" rule would
  have been wrong for seven of the nine. Read the allele list, not the gene
  list.

- **Two properties, because the held-back comment named two distinct hazards.**
  - `alleles: none` -- the authority names the locus and deposits nothing under
    it. `Allele.get_with_gene` refuses to build on such a gene, so `HLA-Z`
    resolves and `HLA-Z*01:01` is None. This also closes a live gap: today
    `HLA-MICC*01:01` and `HLA-DQB3*01:01` mint alleles for loci with zero
    deposited sequences. Nine loci carry it.
  - `context only: true` -- the gene stays out of species-less lookup, the
    gene-level analogue of `context only prefixes`. Bare `N` stays `RT1-n` and
    bare `S` stays `H2-s`; `HLA-N` and `parse("N", species="Homo sapiens")`
    resolve.

- **The guard had to go in three places, not one.** The bare-token path, the
  species-inference path in `parse_species`, and `parse_standard_allele_format`
  -- which returns before either, so `N*01:01` was still resolving to human
  after the first two were done.

- **A test encoded the gap as a fact.** `test_nonsense_inputs.py` listed
  `HLA-X` under "X is not a valid gene". IMGT/HLA names it. Replaced with
  positive coverage and a note.

- **P and V are deliberately not `context only`.** They are equally single
  letters, but bare `P` and `V` have meant `HLA-P`/`HLA-V` since long before
  this; flipping them to `H2-p`/`H2-v` is a parser policy question about
  ambiguous bare tokens, which is #130. Adding data should not quietly move
  parses that already exist.

- **Measured:** 0 of 25,200 corpus names change. 15,996 tests pass. Disabling
  either new mechanism fails 29 of the new tests, so they are not vacuous.
- Bumped to 3.49.0.
