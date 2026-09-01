# Establish Chpi from UniProt (#131)

## Review

- **One source I had never queried.** The `underrepresented_taxa_source_registry`
  is built from UniProt gene names -- `uniprot_gene_name: Tycu-IA` is what its
  own entries record -- and I had gone through IPD, PubMed and GenBank without
  once asking UniProt. Same gap as the GenBank one, one layer along.

- **It settles Chrysolophus pictus.** UniProt curates the golden pheasant class
  I sequences under prefixed gene names: A0A0U1ZFQ3 `Chpi-IA1`, A0A0U1ZFL7
  `Chpi-IA2`, A0A0U1ZCW0 `Chpi-IA3`, all referencing PMID 26700854 -- the paper
  already cited in this entry for IA3's pseudogene status, which writes the
  loci as IA1/IA2/IA3 *without* the prefix. The prefix is in the database
  curation rather than the paper text, which is why PubMed searching missed it.

- **And it strengthens two negatives rather than leaving them silent.** A
  `gene:Pacr*` search returns human PACRG and PACRGL; `gene:Xetr*` returns
  nothing. Those are negatives from a source that demonstrably finds the
  positives, which is worth more than an absence of hits, and the canary test
  now says so.

- **Queried twice, with different shapes**, after the GenBank retmax lesson:
  `"<prefix>" AND organism_name:"<species>"` and `gene:<prefix>*`. Boin, Mega,
  Pacr, StriOccCaur and Xetr are empty on both.

- **#131 is 158 designated / 15 unknown**, from 11/163 when filed.

- **Measured:** 0 of 36,752 corpus names change. 16,439 tests pass.
- Bumped to 3.59.1.
