# IPD-MHC and IMGT/HLA coverage gaps

Tracking issues: #111, #112, #113

Found by sweeping every IPD-MHC group species listing and the IMGT/HLA gene
list against `species.yaml`. That sweep found zero prefix mismatches across the
125 IPD species we already carried — everything below is absence, not error.

## Specification

- [x] Add the 26 remaining IPD-MHC species (2 of the 28 shipped in #108
      because they owned prefixes that were resolving to the wrong animal).
- [x] Keep out-of-genus species off the genus nodes, so they do not inherit a
      prefix and gene list that is not theirs.
- [x] Add the IMGT/HLA genes that can be added without regressing existing
      behaviour, with pseudogene status and legacy aliases.
- [x] Establish which IMGT/HLA genes cannot be added yet, and say why in the
      ontology rather than leaving it to be rediscovered.
- [x] Bump the version and run `./format.sh`, `./lint.sh`, and `./test.sh`.
- [x] Review the final diff and document the result below.

## Review

- **#111**, 26 species added: 10 capuchins (*Cebus*/*Sapajus*) under
  `Primata sp.`, 11 cetaceans under `Cetacea sp.`, and 2 jackals under
  `Canis sp.` Prefixes are the official Comparative MHC Nomenclature Committee
  designations; loci are not curated for any of them, so only the species
  designations are recorded.
- Three of the 26 are not in the genus of the group that lists them —
  *Cuon alpinus* and *Lycaon pictus* are canids but not *Canis*, and
  *Phacochoerus africanus* is a suid but not *Sus*. Filing them under
  `Canis sp.`/`Sus sp.` would hand them the DLA/SLA prefix and those genera's
  gene lists on no evidence, which is exactly the water buffalo problem in
  #109. Added `Canidae sp.` and `Suidae sp.` instead — real taxonomic ranks,
  the same shape as the existing `Cetacea sp.` and `Galliformes sp.` nodes,
  and what IPD-MHC's "Canids" and "Suids" groups actually cover. Their
  prefixes are taxonomic, so descendants do not inherit them: `DLA` still
  resolves to `Canis sp.` and `SLA` to `Sus sp.`
- **#113**, 10 of 19 genes added: class II pseudogenes DRB2, DQB3, DPA2, DPA3
  and DPB2; MIC pseudogenes MICC, MICD and MICE; and the immunoproteasome
  subunits PSMB8 and PSMB9, with LMP7/LMP2 as aliases in the same shape as the
  existing RING4/RING11 aliases for TAP1/TAP2. All eight pseudogenes carry
  `pseudogene: true`.
- The other 9 are **deliberately held back**. IMGT/HLA names the class I gene
  fragments N, R, S, T, U, W, X, Y and Z, and adding them regresses two things:
  bare `n`, `s`, `t`, `u` and `w` stop resolving to the mouse and rat haplotype
  shorthand they mean today and become human gene fragments, and allele-less
  fragments start accepting allele fields, so `Z*01:01` parses. Three existing
  tests assert `HLA-X` and `HLA-Z*01:01` are invalid. The same shadowing
  already affects H/J/K/L/P/V against H2-k and friends, so this wants deciding
  once for the whole letter series rather than being extended quietly. The
  reasoning is recorded next to the gene list in `species.yaml` and on #113.
- **Corrected #112 from the previous PR.** That fix gave `Caau` and `Hyam` to
  the species IPD-MHC designates, on the assumption that an official
  designation outranks a curated alias. It does not. The naming rule is
  mechanical, so several species derive the same code and only one is usually
  the one in print. `Caau-DAB` and `Caau-UFA` are published *Carassius
  auratus* designations, while IPD holds no allele sequences for *Canis
  aureus* at all — so the change broke `Caau-DAB1`, `Caau-UBA`, `Caau-DAB3`,
  `Hyam-DAB1` and `Hyam-UBA`, all of which parsed before. Reversed it: the
  attested species keeps the runtime prefix and the designation is recorded as
  `context only prefixes` on the species IPD names, which stays reachable by
  its own `CaniAure`/`HypeAmpu` prefix. The two existing tests that the
  previous PR rewrote are restored to their original assertions, which were
  right.
- Verified against the bundled netMHCpan/netMHCIIpan/IEDB corpora: no change
  beyond the single `B12 class I` correction that shipped in #108.
- Bumped 3.36.0 to 3.37.0.
- `./format.sh`: passed.
- `./lint.sh`: passed.
- `./test.sh`: passed (15,388 tests; 91% statement coverage).
