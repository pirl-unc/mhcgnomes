# Finish the IPD-MHC namespace sweep; 15 more prefixes established (#131, #112)

## Review

- **All eleven IPD-MHC groups are now transcribed**, not eight.
  `ipd_designations.yaml` goes from 55 rows to 125 with CHICKEN, FISH, NHP and
  the `Bos sp.` group row. The eight groups already there were re-read at the
  same time and every row still agreed, code for code.

- **The completed sweep found zero disagreements.** All 125 IPD designations
  match our prefix, and every species IPD lists is in our ontology. That is now
  a CI check rather than a thing someone did by hand once.

- **Three groups are far smaller than they look**, which is itself the finding:
  FISH is two species and CHICKEN is one. Every other fish and bird in this
  ontology has a generated prefix or a literature citation, never a
  designation. IPD also has no `Bos taurus` row -- cattle are filed as
  `Bos sp. (BoLA)` -- so `Bota` is literature usage, not a committee
  assignment, and `Boin` has nothing behind it at all.

- **Fifteen prefixes established, 130 -> 146 designated, 46 -> 30 unknown.**
  Three from IPD (Gaga, Onmy, Sasa) and twelve read verbatim from the papers:
  Bota, Feca, Cyca, Coja, Saha, Xela, Modo, Anda, Dare, Ptal, Satr, and H2 from
  the committee report that named the mouse system.

- **`Iibi` is not a species prefix.** Greater prairie chicken carried it with
  the note "mhcseqs uses Iibi -- unusual but attested". Nothing attested it.
  PubMed has no occurrence; the nucleotide database has exactly one, GenBank
  JX971120.1, where it is a *gene* symbol:

      gene   complement(5622..6980)
             /gene="IIBI"
             /product="MHC class II antigen beta chain 2"

  Meanwhile `Tycu` names 80 GenBank records at allele level (`Tycu-BLB*26` and
  siblings) and is the Klein 2+2 code for the binomial. So `Tycu` is the
  prefix; `Iibi` stays as an `other prefix` so strings already emitted under it
  parse, but nothing is written with it. The same failure shape as `Caau`: a
  code that cannot be derived from the binomial did not belong to it.

- **A second authority on the six primate `_LA` codes.** The IPD-MHC NHP group
  lists 66 primates, every one with a 2+2 code, and none of ChLA/GoLA/MaLA/
  OmLA/OrLA/RhLA is among them -- agreeing with the de Groot report, which does
  not contain them either. Recorded next to the canary list.

- **Could not establish, and said so**: 30 entries remain, including Acda,
  Boin, Chpi, Crac, Crpo, Eqbu, Mega, Orcu, Pacr, Spau, Xetr and four
  *Ctenomys*. Each was searched and none returned a usable citation.

- **Measured:** 40 of 36,752 corpus names change, every one of them the
  Iibi -> Tycu rename. 16,352 tests pass.
- Bumped to 3.53.0.
