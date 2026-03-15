# mhcseqs Parse Failure TODO

Tracking fixes for 8,305 parse failures (51.2%) from 16,208 curated non-IMGT/IPD
sequences. Organized by category from the error report.

---

## Category (a): Unknown species prefix — 7,086 seqs, 560 prefixes

Each task: add species entry to `species.yaml` with genes, update
`underrepresented_taxa_source_registry.yaml`, add gene aliases if needed,
write tests.

### Top-10 prefixes (by sequence count)

- [ ] **Epco** — *Epinephelus coioides* (orange-spotted grouper), fish, 276 seqs
  - Genes: DAB, DBB, DAA
  - Plan: Add species entry with class II DA/DB loci. Research class I genes
    from literature/NCBI.

- [ ] **Fuat** — *Fulica atra* (Eurasian coot), bird, 267 seqs
  - Genes: DAB
  - Plan: Add species entry with class II DA locus (DAB). Check literature for
    class I genes.

- [ ] **Satr** — *Salmo trutta* (brown trout), fish, 246 seqs
  - Genes: DAB, DAA
  - Plan: Add species entry with class II DA locus. Related to Salmo salar
    (Sasa) — check if gene structure mirrors Atlantic salmon.

- [ ] **Modo** — *Monodelphis domestica* (gray short-tailed opossum), marsupial, 232 seqs
  - Genes: UT3, UG, UT8
  - Plan: Add species entry. Marsupial MHC uses non-standard gene names (UT/UG
    families). Research opossum MHC literature for complete gene inventory and
    class assignments.

- [ ] **Sthi** — *Sterna hirundo* (common tern), bird, 206 seqs
  - Genes: UA, DAB
  - Plan: Add species entry with class I UA gene and class II DA locus.

- [ ] **SAAL** — *Salvelinus alpinus* (Arctic char), fish, 200 seqs
  - Genes: UBA, UGA, UEA
  - Plan: Add species entry. Note uppercase prefix convention (SAAL) — may need
    alias or normalization check. Salmonid-style class I genes.

- [ ] **Zhom** — *Zhangixalus omeimontis* (Omei tree frog), amphibian, 162 seqs
  - Genes: Rhom-beta1
  - Plan: Add species entry. Note unusual gene naming (`Rhom-beta1` looks like
    a legacy/paper-local name). May need gene alias to map to standard class II
    beta gene.

- [ ] **Spma** — *Spheniscus magellanicus* (Magellanic penguin), bird, 157 seqs
  - Genes: DRB1
  - Plan: Add species entry with class II gene. DRB1 naming follows mammalian
    convention — verify this is correct for penguin or if it should be DAB.

- [ ] **Trov** — *Trachinotus ovatus* (golden pompano), fish, 153 seqs
  - Genes: DAA, DAB, UBA
  - Plan: Add species entry with class I (UBA) and class II DA locus.

- [ ] **Saha** — *Sarcophilus harrisii* (Tasmanian devil), marsupial, 112 seqs
  - Genes: I, DAB, UC
  - Plan: Add species entry. Another marsupial with non-standard naming. Gene
    "I" is likely a generic class I label. Research devil MHC literature.

### Remaining 550 prefixes

- [ ] **Bulk triage**: Sort remaining 550 unknown prefixes by sequence count.
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

Current state: Has UA (I), DAB/DAB1/DAB2 (IIa DA). Has aliases for
MhcTyal-DAB1, MhcTyal-DAB2, MHCIIB, DRB.

- [ ] **Investigate remaining failures** — 156 seqs still fail despite existing
  genes/aliases. Likely causes:
  - Double-prefix patterns like `MhcTyal-UA*01:01` (the `Mhc` prefix before
    the species code may confuse the parser)
  - Numbered UA variants (UA1, UA2) not in ontology
  - Other gene names in external datasets not yet aliased
- [ ] **Add parser support or aliases for `Mhc<Prefix>-` pattern** — this is a
  common convention in bird MHC literature. May affect multiple bird species.

### Chinese egret (Egeu) — 141 seqs

Current state: Species registered but **zero genes defined**.

- [ ] **Add genes**: DAB1-6, DRA, UAA, UBA based on error report
  - Class I: UAA, UBA
  - Class II alpha: DRA
  - Class II beta: DAB, DAB1, DAB2, DAB3, DAB4, DAB5, DAB6
  - Determine locus groupings from literature

### Japanese flounder (Paol) — 86 seqs

Current state: Has Ia1, Ia2 (Ia), DAA, DAB (IIa DA).

- [ ] **Add numbered DAB variants** — DAB1 through DAB6 as seen in mhcseqs
  data. Decide: are these separate genes in species.yaml, or aliases mapping
  to DAB?

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

Current state: Only has UBA (Ia). Missing non-standard nomenclature.

- [ ] **Add genes for non-standard nomenclature** — mhcseqs uses `mhc1uma`,
  `mhc2daa` style names. These need either:
  - Gene aliases mapping `mhc1uma` → an appropriate class I gene
  - Gene aliases mapping `mhc2daa` → a class II gene
  - Or new gene entries if these represent distinct loci (UMA, DAA, etc.)
- [ ] **Research zebrafish MHC** — Danio rerio has well-studied MHC. Add
  missing class I (UBA, UCA, UDA, UEA, UGA, UHA, etc.) and class II (DAA, DAB,
  etc.) genes from ZFIN/literature.

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

- [ ] **Lowercase concatenated gene names** — Zebrafish uses `mhc1uma`,
  `mhc2daa`. May appear in other fish species too. Determine if this is a
  parser-level fix or per-species aliasing.

- [ ] **Roman numeral class + number pattern** — `Coja-II-01*01` style. May
  appear in other bird species. Consider parser-level support.

---

## Execution order

Recommended priority (by impact × effort):

1. Bulk unknown-species additions (top 10 prefixes = ~2,011 seqs)
2. Chicken gene gaps (287 seqs, species already exists)
3. Chinese egret genes (141 seqs, species exists but empty)
4. Barn owl parser/alias fixes (156 seqs)
5. Zebrafish gene expansion (61 seqs)
6. Flounder DAB variants (86 seqs)
7. Medaka prefix collision + entry (82 seqs)
8. Quail numbering pattern (48 seqs)
9. Remaining 25 known-species/unknown-gene prefixes (~419 seqs)
10. Bulk triage of remaining 550 unknown prefixes
11. Cross-cutting parser fixes (Mhc-prefix, lowercase genes, Roman numerals)
