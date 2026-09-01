# Establish 11 more prefixes from GenBank (#131)

## Review

- **I stopped short of my own method.** The `Iibi` finding in #165 came from
  searching GenBank nuccore, and it worked because deposited records name
  species prefixes at allele level. I then reported the remaining 30 entries as
  "could not establish" having searched only PubMed and the IPD group tables.
  Running the same nuccore sweep across all of them establishes **eleven**.

- **A query shape hid two more.** The first sweep asked for
  `"<species>"[Organism] AND (<prefix> OR MHC OR histocompatibility)`, so for
  species with many MHC records the prefix hits fell outside `retmax`. Re-run
  with the prefix *required*, `Spau` and `Saal` appeared. A zero from a query
  that could not have found the answer is not a negative result.

- **Nine with allele-level names**: Acda (`Acda-DAB*1102`), Crac (`Crac-DB01`
  through `-DB06`), Crpo (`Crpo-DAB2`), Ctau (`Ctau-DRB23`), Ctpe
  (`Ctpe-DQA03`), Ctta (`Ctta-DRB26`), Ctto (`Ctto-DQA02`), Eqbu
  (`DQB-Eqbu-DQB*0401`), Orcu (`Orcu-U2*05:02:01:01`). Plus Spau
  (`Spau-DAA-214`).

- **One weaker, and said so in the entry.** `Saal` appears in 98 records as the
  *isolate* label `Saal_UBA_101`..`_106`, not as an allele name. That is the
  species code and the salmonid class I locus concatenated, which is real
  usage, but it is not `Saal-UBA*01:01` and the comment says so rather than
  rounding it up.

- **Two negatives now have evidence rather than silence**, and are pinned in
  the canary test: peafowl class II is deposited as `(B-LB) gene, B-LB-12
  allele` -- the chicken nomenclature, no `Pacr` anywhere -- and `Xetr` does
  occur in GenBank, as clone tags like `Xetr-T2R54` for bitter taste
  receptors, not for MHC.

- **#131 is now 157 designated / 19 unknown**, from 11/163 when filed and 30
  before this. Ten of the nineteen are group nodes with no organism of their
  own; the other nine are Boin, Chpi, EudyChrys, Mega, MesoCriAu, NeosScha,
  Pacr, StriOccCaur and Xetr.

- **Measured:** 0 of 36,752 corpus names change -- provenance is metadata, not
  parsing. 16,387 tests pass.
- Bumped to 3.56.0.
