# `Allele.is_allele_group`: one allele or an allele group? (#215)

GitHub issue: #215

## Evidence

- [x] Check whether "one numeric field = group" holds, against the registries
  rather than by assumption. It does not. In the pinned IPD-IMGT/HLA 3.42.0,
  85 MICA, 25 MICB and 3 HFE current names have one field (`MICA*001`). In
  IPD-MHC 3.8.0.0, 174 names across 110 genes do, many of them numeric
  (`Papa-B*03`, `Mamu-G*05`, `Patr-DPB1*18`).
- [x] Check the other direction. `SLA-1*15XX` parses as one non-numeric field
  (`15xx`), yet it names every allele in group 15: Hammer et al. 2021
  (PMC8362188), as already cited in haplotypes.yaml. A "letters = one
  molecule" rule would call it one allele, a silent wrong answer.
- [x] Check whether alias data can tell old names apart. Not safely: the HLA
  table has `MICA*008 -> MICA*008:01:01` (IMGT history), but `MICA*008` is also
  the current group. So the property does not consult aliases; old names are
  recognized by resolving them (`use_allele_aliases=True`, fixed in #216).

## Implementation

- [x] `scripts/generate_single_field_alleles.py` writes
  `mhcgnomes/data/single_field_alleles.yaml`: complete names with one numeric
  field (185 across 19 prefixes), from the pinned allele-aliases inputs. The
  External data CI job regenerates it and fails on drift. The script is in
  `scripts/`, not the package, so the wheel does not ship it (#221).
- [x] `Allele.is_allele_group`: True for an `NNXX` field, or for a single
  numeric field (optionally `W`-prefixed) that is not a registry name.
  Otherwise False. Errors only toward "group".
- [x] Docs: "One allele or an allele group?" in docs/parsing.md, doctested.
- [x] Tests: the issue's examples; IPD lineages; XX; provisional names;
  registry names and their siblings; G/P; NetMHC short names with and without
  aliases; every registry entry parses to a non-group and resolves to a
  species and gene; the generator's filter and YAML round-trip.
- [x] Bump to 3.65.0 (new public API); run `./format.sh`, `./lint.sh`,
  `./test.sh`.

## Review

- I had suggested a True/False/None result. With the registry list, the
  remaining unknowns are old names the alias table does not cover (e.g.
  chicken `Gaga-BF2*21`, #199). Every such case comes out as True, which is
  the safe direction for a caller that needs one molecule, so a plain bool
  suffices and a None would only push a policy choice back onto every caller.
