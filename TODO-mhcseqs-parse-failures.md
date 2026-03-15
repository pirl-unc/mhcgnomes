# mhcseqs Parse Failure TODO

Tracking fixes for 8,305 parse failures (51.2%) from 16,208 curated non-IMGT/IPD
sequences. Organized by category from the error report (run against mhcgnomes 3.1.0).

NOTE: Several species from the error report were already added to current main
after 3.1.0. These are marked DONE below.

---

## Category (a): Unknown species prefix — 7,086 seqs, 560 prefixes

Each task: add species entry to `species.yaml` with genes, update
`underrepresented_taxa_source_registry.yaml`, add gene aliases if needed,
write tests.

### Top-10 prefixes (by sequence count)

- [x] **Epco** — already in species.yaml (DAA, DAB, DBB) — DONE pre-3.1.0+
- [x] **Fuat** — already in species.yaml (DAB) — DONE pre-3.1.0+
- [x] **Satr** — already in species.yaml (UBA, DAB) — DONE pre-3.1.0+
- [x] **Sthi** — already in species.yaml (UA, DAB) — DONE pre-3.1.0+
- [x] **Spma** — already in species.yaml (DRB1) — DONE pre-3.1.0+
- [x] **Trov** — added in this branch (UBA, DAA, DAB)

- [ ] **Modo** — *Monodelphis domestica* (gray short-tailed opossum), marsupial, 232 seqs
  - Genes: UT3, UG, UT8
  - Status: In backlog_clades/unusual_mammals, blocked on species-specific
    source review and stable gene symbols.
  - Plan: Research opossum MHC literature for complete gene inventory and
    class assignments. UT/UG families need source-backed canonical names.

- [ ] **Saal** — *Salvelinus alpinus* (Arctic char), fish, 200 seqs
  - Genes: UBA, UGA, UEA
  - Status: registry_only, blocked on accession-backed confirmation.
  - Plan: Find stable accessions for Saal-UBA, Saal-UGA, Saal-DAB.
    Negative test already exists preventing premature parsing.

- [ ] **Zhom** — *Zhangixalus omeimontis* (Omei tree frog), amphibian, 162 seqs
  - Genes: Rhom-beta1
  - Status: registry_only, blocked on canonical name decision.
  - Plan: Map old-genus `Rhom-beta1` label onto standard class II beta gene name.

- [ ] **Saha** — *Sarcophilus harrisii* (Tasmanian devil), marsupial, 112 seqs
  - Genes: I, DAB, UC
  - Status: registry_only, blocked on alias policy for generic class I labels.
  - Plan: Research devil MHC loci (UA, UB, UC, UK, UM). Define stable alias
    policy for bare "I" strings in marsupials.

### Remaining ~550 prefixes

- [ ] **Bulk triage**: Sort remaining unknown prefixes by sequence count.
  Batch-add species entries for those with >20 sequences first, working down.
  For each batch:
  1. Verify scientific name and 4-letter prefix against taxonomy databases
  2. Look up MHC gene structure from NCBI/UniProt/literature
  3. Add to species.yaml with conservative gene set
  4. Add tests for species + gene parsing

---

## Category (b): Known species, unknown gene — 1,219 seqs, 32 prefixes

### Chicken (Gaga) — 287 seqs

Current state: Has BF/BF1/BF2 (Ia), YF1/YF2 (Ib), CD1-1/CD1-2 (Id),
BLA/BLB/BLB1/BLB2/B12c (IIa BL), DMA/DMB1/DMB2 (IIb DM).

- [ ] **Add YFV gene** — appears in mhcseqs data; currently blocked on
  reconciliation with MHCY-family naming per registry notes. Investigate
  whether YFV is a distinct locus or alias for existing YF1/YF2.
- [ ] **Add MHCY gene(s)** — Rfp-Y / MHCY region genes. Determine which
  specific loci exist and whether they map to existing YF genes or are separate.
- [ ] **Add BLB-related aliases** — check if external datasets use BLB3, BLB4,
  or other numbered variants beyond BLB1/BLB2/B12c.
- [ ] **Add any missing gene aliases** — check what 287 failing sequence names
  actually look like and add appropriate aliases in gene_aliases.yaml.

### Barn owl (Tyal) — 156 seqs

- [x] **Add MhcTyal-UA and MhcTyal-DAB aliases** — DONE. The parser infers
  species from gene aliases, so standalone `MhcTyal-UA*01:01` now works.
- [ ] **Audit remaining failures** — The MhcTyal-UA/DAB aliases fix the main
  gap, but some of the 156 seqs may use other patterns (UA1, UA2, etc.).
  Need actual failing sequence names to triage further.

### Chinese egret (Egeu) — 141 seqs

- [x] **Add genes** — DONE: added UAA, UBA (I), DRA, DAB, DAB1-6 (IIa DA)

### Japanese flounder (Paol) — 86 seqs

- [x] **Add numbered DAB variants** — DONE: DAB1-6 as aliases to DAB

### Medaka (Orla) — 82 seqs

Current state: **Not registered.** The prefix `Orla` collides with orangutan
(`Pongo sp.` uses prefix `OrLA`). Normalization is case-insensitive, so
`Orla` == `OrLA`.

- [ ] **Resolve prefix collision** — Options:
  1. Use alternative prefix for medaka (e.g., `Oryl` from *Or*yzias *l*atipes,
     or `Orla` and change orangutan to a different prefix)
  2. Check what prefix mhcseqs actually uses for medaka
  3. Check IPD/literature for established medaka MHC prefix convention
- [ ] **Add species entry** with genes: UGA, UAA, UBA, UHA (lineage genes per
  error report)

### Zebrafish (Dare) — 61 seqs

- [x] **Add class II genes** — DONE: added DAA, DAB
- [x] **Add ZFIN-style aliases** — DONE: mhc1uba→UBA, mhc2daa→DAA, mhc2dab→DAB
- [ ] **Research additional class I genes** — Danio rerio has many U-lineage
  genes (UCA, UDA, UEA, UFA, UGA, UHA, etc.). Add as needed if mhcseqs
  sequences reference them.

### Japanese quail (Coja) — 48 seqs

Current state: Has DAB1, DBB1, DCB1, DDB1, DEB1, DFB1, DGB1 (all IIa beta).

- [ ] **Add support for `Coja-II-01*01` numbering** — this appears to be a
  paper-local naming convention using Roman numeral class + number. Options:
  - Add gene aliases mapping II-01 → DAB1, II-02 → DBB1, etc.
  - Or add parser support for this naming pattern
- [ ] **Add class I genes** — currently has zero class I genes. Check quail
  literature for BF-like genes.

### Remaining 25 prefixes (~419 seqs)

- [ ] **Audit remaining known-species/unknown-gene failures** — For each of
  the remaining 25 prefixes:
  1. Check what gene names appear in failing sequences
  2. Determine if genes should be added to species.yaml or gene_aliases.yaml
  3. Add tests

---

## Cross-cutting parser issues

- [ ] **`Mhc<Prefix>-Gene` double-prefix pattern** — Common in bird MHC
  literature (e.g., `MhcTyal-DAB1`). Currently handled via per-species aliases,
  but a general parser rule could fix this for all species at once. Investigate
  feasibility.

- [x] **Lowercase concatenated gene names** — DONE for zebrafish (Dare aliases).
  May need similar treatment for other fish species.

- [ ] **Roman numeral class + number pattern** — `Coja-II-01*01` style. May
  appear in other bird species. Consider parser-level support.

---

## Execution order (updated)

Next priorities:
1. Chicken gene gaps — 287 seqs, needs research on YFV/MHCY naming
2. Barn owl alias/parser fixes — 156 seqs
3. Medaka prefix collision — 82 seqs
4. Quail numbering pattern — 48 seqs
5. Blocked species (Modo, Saal, Zhom, Saha) — need source research
6. Remaining 25 known-species/unknown-gene prefixes (~419 seqs)
7. Bulk triage of remaining ~550 unknown prefixes
8. Cross-cutting parser fixes (Mhc-prefix, Roman numerals)
