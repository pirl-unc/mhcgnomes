# mhcseqs Parse Failure TODO

Tracking fixes for 8,305 parse failures (51.2%) from 16,208 curated non-IMGT/IPD
sequences. Error report was run against mhcgnomes 3.1.0; many items fixed since.

---

## Category (a): Unknown species prefix — 7,086 seqs, 560 prefixes

### Top-10 prefixes — ALL DONE

- [x] Epco, Fuat, Satr, Sthi, Spma — pre-3.1.0+
- [x] Trov — 3.2.0
- [x] Modo, Saal, Saha — 3.3.0
- [x] Zhom — 3.4.0

### Remaining ~550 prefixes

- [ ] **Bulk triage**: Sort remaining unknown prefixes by sequence count.
  Batch-add species entries for those with >20 sequences.

---

## Category (b): Known species, unknown gene — 1,219 seqs, 32 prefixes

### Chicken (Gaga) — 287 seqs

- [x] **Add YFV/MHCY/Y15 aliases** — DONE in 3.6.0-3.7.0
- [x] **Add BFw/BFz/B-F-S aliases** — DONE in 3.7.0
- [x] **Add MHCY2B/MHCY2B1/MHCY2B2 aliases** — DONE in 3.7.0
- [x] **Add B-DMB1 alias** — DONE in 3.7.0

### Barn owl (Tyal) — 156 seqs

- [x] **Mhc prefix stripping** — DONE in 3.2.0
- [ ] **Audit remaining failures** — need actual failing sequence names.

### Chinese egret (Egeu) — 141 seqs

- [x] **Add genes** — DONE (UAA, UBA, DAB1-6)
- [x] **Remove unattested DRA** — DONE in 3.5.0 (source-verified)

### Japanese flounder (Paol) — 86 seqs

- [x] **Add numbered DAB variants** — DONE in 3.2.0
- [ ] **Verify alias vs canonical locus model** — need source review.

### Medaka — 82 seqs

- [x] **Resolve prefix collision** — DONE in 3.4.0 (prefix Oryl)

### Zebrafish (Dare) — 61 seqs

- [x] **Add class II genes** — DONE in 3.2.0
- [x] **Generalize mhc1/mhc2 gene prefix stripping** — DONE in 3.3.0
- [x] **Add UEA, UGA, UMA** — DONE in 3.3.0-3.4.0

### Japanese quail (Coja) — 48 seqs

- [x] **Add II-01 through II-07 numbering** — DONE in 3.7.0: gene aliases
  mapping II-01→DAB1, II-02→DBB1, ..., II-07→DGB1. II-13/16/17 remain
  held back (unmapped paper-local labels).
- [x] **Add class I genes** — DONE in 3.6.0

### Remaining 25 prefixes (~419 seqs)

- [ ] **Audit remaining known-species/unknown-gene failures**

---

## Cross-cutting parser issues

- [x] **Mhc prefix stripping** — DONE in 3.2.0
- [x] **mhc1/mhc2 gene prefix stripping** — DONE in 3.3.0
- [x] **5+5 and full latin name prefixes** — DONE in 3.5.0
- [x] **Roman numeral class + number pattern** — DONE in 3.7.0 (Coja aliases)

---

## Follow-up items

- [ ] **Trov source documentation** — needs literature sources.
- [ ] **Paol DAB1-6 alias vs locus model** — needs source review.
- [ ] **Provenance**: machine-readable sources, gene alias provenance, CI checks.
