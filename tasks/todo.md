# Establish FLA and RLA; correct the citation for the six primate _LA codes

Tracking issue: #131 (46 entries still unestablished)

## Review

- **AGENTS.md names the de Groot nomenclature report as the authority for
  primate prefixes, so I read it** rather than repeating that IPD has no group
  page for these codes. Extracting the full text of
  `Groot_Nomenclature_Immunogenetics_2020_3174021.pdf`:

  ```
  Patr 77 hits   Mamu 8   Gogo 7   Popy 3   Mafa 3
  OmLA / MaLA / GoLA / ChLA / OrLA / RhLA : 0, case-insensitively
  ```

  The extraction is sound -- the 2+2 codes the report does use are all there.
  So the six primate `_LA` codes are absent from it.

- **That matters because the mhcseqs registry cites exactly that paper as their
  evidence.** `mhc_prefix_aliases.csv` gives all six
  `status: literature_historical` with the de Groot PDF as the URL, and the PDF
  does not contain them. The citation does not check out, so they stay `None`.
  Marking them designated on it would be the `Caau` mistake with a footnote.

- **Two of the eight had different evidence, and it holds.** Read from PubMed
  directly rather than the search summary:
  - `FLA` -- PMID 2492667, *"Genetic characterization of FLA, the cat major
    histocompatibility complex"*, and the abstract says "the major
    histocompatibility complex (MHC) of the domestic cat (termed FLA)".
  - `RLA` -- PMID 32522857, whose title names "rabbit Major Histocompatibility
    Complex Class I Molecule **RLA-A1**", so alleles carry the prefix.

  Both marked `designated` with the citation on the entry.

- **#131 is now 130 designated / 46 unknown**, from 11/163 when it was filed.
  The canary list drops from eight names to six, with the reason recorded next
  to it so the next reader does not re-follow the same broken citation.

- **Measured:** 0 of 11,558 corpus names change.
- Bumped to 3.48.3.
