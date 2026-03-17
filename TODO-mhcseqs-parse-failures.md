# mhcseqs Parse Failure TODO

Tracking fixes for 8,305 parse failures (51.2%) from 16,208 curated non-IMGT/IPD
sequences. Error report was run against mhcgnomes 3.1.0; most items now fixed.

---

## DONE

- [x] Top-10 unknown prefixes (Epco, Fuat, Satr, Sthi, Spma, Trov, Modo, Saal, Saha, Zhom)
- [x] Chicken aliases (YFV, MHCY, Y15, BFw, BFz, B-F-S, MHCY2B, B-DMB1)
- [x] Barn owl Mhc prefix stripping
- [x] Chinese egret genes (UAA, UBA, DAB1-6; DRA removed)
- [x] Flounder DAB1-6 aliases
- [x] Medaka prefix collision (Oryl)
- [x] Zebrafish genes + mhc1/mhc2 stripping
- [x] Quail class I genes + II-01 numbering
- [x] Mhc prefix stripping (parser-level)
- [x] mhc1/mhc2 gene prefix stripping (parser-level)
- [x] 5+5 and full latin name prefixes
- [x] Latin name as canonical species identity
- [x] Old genus aliases (Brre→Dare, Trsi→Pesi, Gran→Anan, Chni→Anni, Raca→Lica, Racl→Licl, Maeu→Noeu)
- [x] 30+ batch species (raptors, cranes, passerines, fish, amphibians, sharks, tuatara)
- [x] 20+ archosaur species (crocodilians, turtles, ratites)

---

## Remaining

- [ ] **~190 more species from mhcseqs P2** — batch import from UniProt
- [ ] **Remaining gene gaps** — croc DB01-DB08, turtle scaffold IDs, Saha numbered format
- [ ] **Barn owl remaining failures** — need actual sequence names
- [ ] **Paol alias vs locus model** — needs source review
- [ ] **Trov source documentation**
- [ ] **Provenance** — machine-readable sources, gene alias provenance, CI checks
