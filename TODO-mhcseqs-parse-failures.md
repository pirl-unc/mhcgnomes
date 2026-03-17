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

- [x] **Add YFV alias** — DONE: maps to YF1 (MHCY class I). YFV is a variant
  label from mhcseqs, not a distinct gene. Per PMC9635633, the MHCY region
  has 45 class I loci but YF1 is the primary characterized one.
- [x] **Add MHCY alias** — DONE: maps to YF1 as generic MHCY class I label.
- [ ] **Add BLB-related aliases** — BLB3, BLB4, etc.
- [ ] **Add any missing gene aliases** — check actual failing sequence names.

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

- [ ] **Add support for `Coja-II-01*01` numbering** — gene aliases mapping
  II-01 → DAB1, II-02 → DBB1, etc.
- [x] **Add class I genes** — DONE: A, B1-B2, C1-C4, D1-D4, E per
  Hosomichi et al. 1999 (PMID 10199914).

### Remaining 25 prefixes (~419 seqs)

- [ ] **Audit remaining known-species/unknown-gene failures**

---

## Cross-cutting parser issues

- [x] **Mhc prefix stripping** — DONE in 3.2.0
- [x] **mhc1/mhc2 gene prefix stripping** — DONE in 3.3.0
- [x] **5+5 and full latin name prefixes** — DONE in 3.5.0
- [ ] **Roman numeral class + number pattern** — `Coja-II-01*01` style.

---

## Follow-up items

- [ ] **Trov source documentation** — needs literature sources.
- [ ] **Paol DAB1-6 alias vs locus model** — needs source review.
- [ ] **Provenance**: machine-readable sources, gene alias provenance, CI checks.
