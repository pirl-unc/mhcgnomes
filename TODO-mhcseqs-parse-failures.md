# mhcseqs Parse Failure TODO

Tracking fixes for 8,305 parse failures (51.2%) from 16,208 curated non-IMGT/IPD
sequences. Error report was run against mhcgnomes 3.1.0; many items have been
fixed in 3.2.0 and 3.3.0.

---

## Category (a): Unknown species prefix — 7,086 seqs, 560 prefixes

### Top-10 prefixes (by sequence count)

- [x] **Epco** — already in species.yaml pre-3.1.0+
- [x] **Fuat** — already in species.yaml pre-3.1.0+
- [x] **Satr** — already in species.yaml pre-3.1.0+
- [x] **Sthi** — already in species.yaml pre-3.1.0+
- [x] **Spma** — already in species.yaml pre-3.1.0+
- [x] **Trov** — added in 3.2.0 (UBA, DAA, DAB)
- [x] **Modo** — added in 3.3.0 (UA, UB, UC, UG, UK, UM, UT3, UT5, UT7, UT8, DAB)
- [x] **Saal** — added in 3.3.0 (UBA, UEA, UGA, DAB)
- [x] **Saha** — added in 3.3.0 (UA, UB, UC, UK, UM, DAB)

- [ ] **Zhom** — *Zhangixalus omeimontis* (Omei tree frog), amphibian, 162 seqs
  - Genes: Rhom-beta1 (old-genus-prefixed class II beta name)
  - Plan: Add species with gene alias Rhom-beta1 → DAB (or similar
    standard class II beta name). The old Rhacophorus genus prefix in the
    gene name is the main complication.

### Remaining ~550 prefixes

- [ ] **Bulk triage**: Sort remaining unknown prefixes by sequence count.
  Batch-add species entries for those with >20 sequences.

---

## Category (b): Known species, unknown gene — 1,219 seqs, 32 prefixes

### Chicken (Gaga) — 287 seqs

- [ ] **Add YFV gene** — blocked on reconciliation with MHCY-family naming.
- [ ] **Add MHCY gene(s)** — Rfp-Y / MHCY region genes.
- [ ] **Add BLB-related aliases** — BLB3, BLB4, etc.
- [ ] **Add any missing gene aliases** — check actual failing sequence names.

### Barn owl (Tyal) — 156 seqs

- [x] **Mhc prefix stripping** — DONE in 3.2.0 (generic parser-level fix).
- [ ] **Audit remaining failures** — need actual failing sequence names.

### Chinese egret (Egeu) — 141 seqs

- [x] **Add genes** — DONE in 3.2.0 (UAA, UBA, DRA, DAB1-6)
- [ ] **Verify gene set against PLOS ONE source** (10.1371/journal.pone.0108506)

### Japanese flounder (Paol) — 86 seqs

- [x] **Add numbered DAB variants** — DONE in 3.2.0 (DAB1-6 as aliases to DAB)
- [ ] **Verify alias vs canonical locus model** — need source review.

### Medaka (Orla) — 82 seqs

- [ ] **Resolve prefix collision** with orangutan OrLA, then add species.

### Zebrafish (Dare) — 61 seqs

- [x] **Add class II genes** — DONE in 3.2.0
- [x] **Generalize mhc1/mhc2 gene prefix stripping** — DONE in 3.3.0
- [ ] **Add more class I genes** — UCA, UDA, UEA, UFA, UGA, UHA, etc.

### Japanese quail (Coja) — 48 seqs

- [ ] **Add support for `Coja-II-01*01` numbering** — gene aliases mapping
  II-01 → DAB1, II-02 → DBB1, etc.
- [ ] **Add class I genes** — check quail literature for BF-like genes.

### Remaining 25 prefixes (~419 seqs)

- [ ] **Audit remaining known-species/unknown-gene failures**

---

## Cross-cutting parser issues

- [x] **Mhc prefix stripping** — DONE in 3.2.0
- [x] **mhc1/mhc2 gene prefix stripping** — DONE in 3.3.0
- [ ] **Roman numeral class + number pattern** — `Coja-II-01*01` style.

---

## Follow-up items

- [ ] **Trov source documentation** — needs literature sources.
- [ ] **Egeu source verification** — confirm DRA vs DAA against paper.
- [ ] **Paol DAB1-6 alias vs locus model** — needs source review.
- [ ] **Medaka (Orla) prefix collision** — resolve before adding species.
- [ ] **Provenance**: machine-readable sources, gene alias provenance, CI checks.
