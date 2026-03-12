# Curation Guide

## Purpose

This document records the rules for placing curated data in `mhcgnomes`
and the source strategy for taxa that are not yet well served by stable
committee-curated MHC nomenclature.

Most of the concrete examples here come from reptiles, amphibians, and
other underrepresented vertebrate groups, but the same rules also apply
to unusual mammals or any other taxon where source quality is ahead of
stable nomenclature.

The key constraint is that `mhcgnomes` is strongest when it has:

1. stable species nomenclature,
2. stable gene nomenclature, and
3. a curated or at least reproducible source of allele strings.

For most reptiles and amphibians, item 3 is the weak link. There are now
good genome assemblies and several strong survey papers, but there is not
yet an `IPD-MHC`-style curated comparative allele registry for these clades.

## Current Repo State

Current reptile/amphibian coverage is minimal:

- snake: `Sistrurus catenatus` (`Sica`) with `DAA` / `DAB`
- frog: `Xenopus laevis` (`Xela`) with `UAA`

These live in `mhcgnomes/data/species.yaml` at:

- `mhcgnomes/data/species.yaml:479`
- `mhcgnomes/data/species.yaml:2251`

These entries parse, but they are not yet backed by a broader ingestion
strategy or dedicated tests across most underrepresented taxa.

This branch also introduces a structured curation ledger at:

- `mhcgnomes/data/underrepresented_taxa_source_registry.yaml`

The right design boundary is not "nonmammal". The right boundary is
"taxa that are not yet well served by stable IPD-style nomenclature and
therefore need source-aware ingestion rules". That can include unusual
mammals such as marsupials or monotremes.

## Partial Capture Policy

Not every useful source belongs in `mhcgnomes/data/species.yaml`.

When a source gives us real signal but not runtime-ready nomenclature, the
information should be captured in
`mhcgnomes/data/underrepresented_taxa_source_registry.yaml` instead.

That registry is now the place to preserve:

- candidate species that are not ready for runtime ontology
- observed gene-family structure from papers or genome annotations
- representative annotation URLs or accessions
- blockers that prevent runtime ingestion
- example species for under-reviewed clades, including unusual mammals

This keeps partial information from being lost while avoiding premature
canonization in runtime parsing tables.

## Data Placement Rules

The rule is: put data in the narrowest runtime file that matches its level of
stability.

### Runtime-loaded files

These are loaded by `mhcgnomes/data.py` and directly affect parser behavior.

| File | Put this here | Do not put this here |
| --- | --- | --- |
| `mhcgnomes/data/species.yaml` | Canonical species entries, canonical gene names, MHC class placement, stable parent/prefix relationships | Paper-local aliases, uncertain gene symbols, unresolved candidate loci |
| `mhcgnomes/data/gene_aliases.yaml` | Alternative gene spellings or retired/provisional names that normalize to an existing canonical gene in `species.yaml` | New genes that do not yet have a canonical destination in `species.yaml` |
| `mhcgnomes/data/allele_aliases.yaml` | Retired, shorthand, or formatting variants that normalize to a canonical allele string | New literature-only alleles with no stable canonical allele target |
| `mhcgnomes/data/known_alleles.yaml` | Curated known allele labels for a species/gene where the ontology already exists | A substitute for adding missing species or genes |
| `mhcgnomes/data/haplotypes.yaml` | Named haplotypes and their member alleles | Partial gene-family observations from papers |
| `mhcgnomes/data/serotypes.yaml` | Serotype-to-allele mappings | General class I / class II family structure |
| `mhcgnomes/data/heterodimers.yaml` | Explicit shorthand heterodimer mappings like `DQ2.5` | Speculative alpha/beta combinations from weak literature evidence |
| `mhcgnomes/data/supertypes.yaml` | Functional supertype groupings with clear representative alleles | Serotypes or paper-local functional clusters |

### Non-runtime curation files

These preserve source-backed information that is not yet ready to affect parser
behavior.

| File | Put this here | Why |
| --- | --- | --- |
| `mhcgnomes/data/underrepresented_taxa_source_registry.yaml` | Partial but useful source information: candidate species, observed gene-family structure, representative annotation URLs, blockers, example species | This is the holding area for real signal that is not stable enough for runtime ontology |
| `docs/curation.md` | Cross-file policy, source strategy, confidence tiers, implementation order | This explains decisions; it should not be the only place where concrete partial source facts live |

### Practical decision tree

1. If the species prefix and canonical gene names are stable, add them to `species.yaml`.
2. If a new string can normalize to an existing canonical gene, put it in `gene_aliases.yaml`.
3. If a new string can normalize to an existing canonical allele, put it in `allele_aliases.yaml`.
4. If the source only tells us "this clade probably has class I / class IIbeta / TAP genes" but not stable canonical names, capture it in `underrepresented_taxa_source_registry.yaml`.
5. If the source is a survey paper with paper-local allele IDs, do not put those IDs in runtime YAML unless they map cleanly onto stable canonical names.
6. If the data encodes a derived concept like a serotype, supertype, haplotype, or heterodimer shorthand, use the dedicated file for that concept rather than overloading `species.yaml`.

### Current special cases

- `mhcgnomes/data/default_alleles.yaml` exists but is currently minimal and not
  part of the main runtime loading path in `mhcgnomes/data.py`.
- `mhcgnomes/data/common_genes.yaml` is currently empty and should stay that way
  unless there is a concrete runtime feature that needs it.

## Source Inventory

### Tier 1: Official structured databases

These are the best sources for species normalization and, where available,
stable gene names.

| Source | What it is | Confidence | What we can use it for |
| --- | --- | --- | --- |
| `IPD-MHC` | Official curated comparative MHC database | High | Existing official groups, file formats, committee norms, future submission target |
| `NCBI Datasets` | Official genome/annotation/metadata download portal | High | Genome assemblies, annotations, proteins, transcripts, taxon metadata |
| `Xenbase` | Official Xenopus knowledgebase with downloads, BLAST, gene nomenclature | High | Frog gene names, genome coordinates, gene aliases, other amphibian genomes |
| `The Reptile Database` | Widely used reptile taxonomy authority | High for taxonomy | Species normalization and synonyms for snakes, lizards, turtles, crocodilians, tuatara |
| `Amphibian Species of the World` | Curated amphibian taxonomy reference | High for taxonomy | Species normalization and literature discovery for frogs and salamanders |

References:

- IPD-MHC home: https://www.ebi.ac.uk/ipd/mhc/
- IPD-MHC taxonomy: https://www.ebi.ac.uk/ipd/mhc/taxonomy/
- IPD-MHC downloads: https://www.ebi.ac.uk/ipd/mhc/download/
- NCBI Datasets: https://www.ncbi.nlm.nih.gov/datasets/
- Xenbase: https://www.xenbase.org/
- Xenbase data/download entry points: https://www.xenbase.org/xenbase/
- Reptile Database: https://www.reptile-database.org/
- Amphibian Species of the World: https://amphibiansoftheworld.amnh.org/

Notes:

- `IPD-MHC` is still the gold standard for canonical allele ingestion, but its
  current official groups do not yet cover reptiles or amphibians as first-class
  groups. The taxonomy page currently lists primates, felids, canids, salmonids,
  ovids, bovids, equids, suids, murids, `Gallus`, and cetaceans.
- `Xenbase` is the strongest structured source in this expansion set because it
  provides official gene nomenclature, gene search, BLAST, downloadable genomes,
  and "other amphibian genomes" links.
- `NCBI Datasets` is the best generic fallback when there is no clade-specific
  nomenclature database.

### Tier 2: Strong clade-specific papers

These papers are useful for deciding which species and gene families are worth
adding, but they are not automatically safe as canonical allele registries.

| Clade | Source | Evidence type | Best use |
| --- | --- | --- | --- |
| Sea turtles | Martin et al. 2026 | 4-species allele survey | Prioritize turtle species and coarse class I / class II support |
| Sea turtles | Martin et al. 2022 | Green/loggerhead class I survey | Backfill turtle class I alias handling |
| Crocodilians | Jaratlerdsiri et al. 2014 | Order-level class I evolution | Add crocodilian species/gene family aliases |
| Lizards | Miller et al. 2022 | Two `Anolis` genomes | Add genome-backed lizard gene metadata |
| Snakes | Kirsch et al. 2025 | Rattlesnake genomes | Add modern snake gene structure assumptions |
| Amphibians | Kiemnec-Tyburczy et al. 2018 | Review | Guide frog/salamander scope and terminology |
| Salamanders | Migalska et al. 2022 | 30-species class I survey | Do not ingest canonical alleles; use for architecture expectations |
| Salamanders | Palomar et al. 2021 | MHC-I/APG coevolution | Add APG expectations and nonclassical expansion notes |
| Tuatara | Miller et al. 2015 | Genome organization study | Useful "other reptile" pilot species |

References:

- Sea turtles, 4 species, class I and class II:
  https://pubmed.ncbi.nlm.nih.gov/41575191/
- Sea turtle class I disease-association study:
  https://pubmed.ncbi.nlm.nih.gov/35154791/
- Crocodylia class I evolution:
  https://pubmed.ncbi.nlm.nih.gov/24253731/
- Squamate MHC in two `Anolis` genomes:
  https://pubmed.ncbi.nlm.nih.gov/36425073/
- Rattlesnake MHC architecture:
  https://pubmed.ncbi.nlm.nih.gov/39704347/
- Amphibian MHC review:
  https://pubmed.ncbi.nlm.nih.gov/28695290/
- Salamander MHC-I survey:
  https://pubmed.ncbi.nlm.nih.gov/36000494/
- Salamander MHC-I/APG coevolution:
  https://pubmed.ncbi.nlm.nih.gov/34375431/
- Tuatara MHC organization:
  https://pubmed.ncbi.nlm.nih.gov/25953959/

## Diagnosis By Clade

### Frogs

What we know:

- `Xenopus laevis` already exists in the ontology as `Xela-UAA`.
- `Xenbase` has official gene search, gene nomenclature, downloads, and genome
  browsers for `X. laevis` and `X. tropicalis`.
- `Xenbase` also links to "other amphibian genomes", which makes it the best
  structured on-ramp for frog expansion.
- The amphibian review shows that both class I and class II are relevant to
  disease susceptibility, especially chytridiomycosis.

What can be confidently ingested:

- `Xenopus` species prefixes
- official Xenbase gene symbols and aliases
- antigen-processing genes (`TAP1`, `TAP2`, `TAPBP`, `B2M`) where they are
  clearly annotated
- model-organism frog genes, even without extensive allele catalogs

What is not yet safe as canonical allele ontology:

- broad allele-level frog nomenclature outside `Xenopus`
- amplicon-only literature alleles with no stable locus naming

Recommendation:

- Start with `Xenopus laevis` and `Xenopus tropicalis`.
- Use Xenbase plus NCBI annotations to add gene-level ontology, not paper-local
  allele catalogs.

### Salamanders

What we know:

- Salamanders show extreme class I expansion.
- One 30-species survey reported about 3000 class I variants and 2-22 gene copies
  per species.
- Salamanders also show coevolution between MHC-I and `TAP1` / `TAP2`.

What can be confidently ingested:

- species taxonomy
- coarse expectations that salamander MHC can include multigene class I families
- APG support (`TAP1`, `TAP2`, `TAPBP`, `PSMB8`, `PSMB9`) when genome annotations
  exist

What is not yet safe as canonical allele ontology:

- species-wide allele naming from large amplicon datasets
- locus-stable class I names across species

Recommendation:

- Treat salamanders as a later phase.
- Add species aliases and gene-family parsing only when genome annotations are
  available.
- Do not ingest paper-local salamander allele IDs as canonical `mhcgnomes`
  allele names.

### Snakes

What we know:

- The repo currently has only `Sica-DAA` / `Sica-DAB`.
- Recent rattlesnake genome work identifies highly duplicated class I and
  class IIbeta loci localized in gene clusters on chromosome 2.
- This implies the current repo snake model is underpowered and probably
  structurally outdated.

What can be confidently ingested:

- snake species prefixes from The Reptile Database
- gene-family level support for class I and class IIbeta in species with
  chromosome-level assemblies or strong annotations
- genome-backed aliases from rattlesnake papers and NCBI annotations

What is not yet safe as canonical allele ontology:

- generic cross-snake locus names that pretend all snake orthology is settled
- single-paper allele names with no stable accession-backed registry

Recommendation:

- Revisit snake support from scratch rather than extending the current
  `Sica-DAA` / `DAB` pattern blindly.
- Pilot on rattlesnakes with modern genome-backed gene structure first.

### Lizards

What we know:

- Two `Anolis` genomes show a core MHC region on chromosome 2 and include many
  homologs of mammalian core MHC genes.
- This is one of the clearest reptile cases for genome-backed, gene-level
  ingestion.
- The strongest current comparative paper is Card et al. 2022, which analyzes
  the green and brown anole MHC using genome structure, BAC evidence, and
  comparative annotation.

What can be confidently ingested:

- `Anolis carolinensis` and `Anolis sagrei` species entries
- genome-backed gene names and aliases from annotated assemblies
- core MHC framework genes and antigen-processing genes if annotation quality is
  good enough

What is not yet safe as canonical allele ontology:

- paper-specific lizard allele numbering not grounded in stable external records
- paper-local homolog numbering from Card et al. 2022
- homology-derived NCBI `LOC...` model records treated as if they were settled
  community locus names

What is ambiguous specifically for `Anolis`:

- The 2022 paper identifies `mhc1` and `mhc2β` homologs, but its phylogenies
  label homologs with sequential within-paper numbers and point readers to a
  supplementary mapping table. That is useful comparative biology, but not yet
  a community nomenclature standard.
- The same paper reports that one of two `mhc2β` homologs in each anole lacks
  exon 2, which means that even "gene copy count" is not equivalent to
  "intact canonical class IIbeta loci".
- NCBI annotations for these species are still mostly model-based and use names
  such as `LOC103282626` ("major histocompatibility complex class I-related gene
  protein-like") and `LOC132766334` ("RLA class II histocompatibility antigen,
  DP alpha-1 chain-like"). Those are useful evidence for gene-family presence,
  but they are not strong enough to canonize as runtime gene symbols in
  `mhcgnomes`.
- The green anole annotations have already moved between assemblies
  (`AnoCar2.0` to `rAnoCar3.1.pri`), which is a good sign for the assembly but a
  reason not to freeze unstable identifiers too early.

Recommendation:

- Lizards are one of the best first reptile targets because the source is genome
  structural, not just amplicon diversity.
- For `Anolis`, stay at species-level support until we curate a small set of
  exact gene symbols backed by stable accessions, not just model `LOC` records.

Primary sources for `Anolis`:

- Card et al. 2022, squamate MHC in two `Anolis` genomes:
  https://pubmed.ncbi.nlm.nih.gov/36425073/
- Eckalbar et al. 2013, green anole genome reannotation:
  https://pubmed.ncbi.nlm.nih.gov/23343042/
- NCBI green anole class I-like model gene example:
  https://www.ncbi.nlm.nih.gov/gene/103282626
- NCBI brown anole class II alpha-like model gene example:
  https://www.ncbi.nlm.nih.gov/gene/132766334

### Turtles

What we know:

- Sea turtles now have a strong 4-species class I / class II survey with 162
  functionally distinct class I alleles and 308 class II alleles across more
  than 300 individuals.
- Earlier work characterized class I variation in green and loggerhead turtles.
- This is strong evidence that turtle MHC diversity is tractable, but the nomenclature
  is still literature-driven rather than committee-curated.

What can be confidently ingested:

- turtle taxonomy from The Reptile Database
- species prefixes for common study species
- coarse gene-family parsing for class I and class II where locus names are
  explicitly given and stable
- paper aliases with provenance

What is not yet safe as canonical allele ontology:

- treating survey-paper alleles as if they were official, cross-study canonical
  names
- inferring stable locus orthology across all turtles from short amplicon studies

Recommendation:

- Turtles are a strong second-wave target after `Xenopus` and genome-backed
  reptiles.
- Start with species/prefix support plus paper-alias parsing, not canonical
  allele registries.

### Crocodilians

What we know:

- Crocodilian class I evolution has been studied across the order.
- Additional genome papers show structured MHC organization in crocodilians.
- This is enough to justify species and gene-family support, but still not enough
  for an `IPD-MHC`-style allele ontology.

What can be confidently ingested:

- crocodilian species prefixes from The Reptile Database
- class I and class II family-level genes from genome-backed sources
- accession-backed aliases from strong genomic studies

What is not yet safe as canonical allele ontology:

- broad allele naming across crocodilians from partial-exon studies
- pretending locus labels are standardized across the order when they are not

Recommendation:

- Make crocodilians a genome-backed parser target, not an official allele
  registry target.

### Tuatara and other reptiles

What we know:

- Tuatara has a mapped core MHC region with class I and class IIbeta copies on
  two chromosomes.
- This is useful as a design test case for handling reptiles with dispersed MHC
  architecture.

What can be confidently ingested:

- species prefix
- gene-family level support for class I and class IIbeta

What is not yet safe as canonical allele ontology:

- full allele sets from old BAC-based or clone-based studies unless matched to
  stable modern accessions

Recommendation:

- Keep tuatara as an "advanced architecture" pilot after the first reptile wave.

## Confidence Tiers For Ingestion

### Tier A: Safe to ingest as canonical ontology now

These have either official nomenclature support or strong gene-level database support.

- species taxonomy from The Reptile Database and Amphibian Species of the World
- `Xenopus` species and gene symbols from Xenbase
- genome-annotated genes from NCBI Datasets when the annotation uses stable gene
  names and there is no evidence of paper-local naming only

### Tier B: Safe to ingest as gene-level aliases, not canonical alleles

- genome-backed reptile genes from `Anolis`, rattlesnakes, crocodilians, and
  tuatara
- turtle gene-family labels from recent multi-species studies
- APG genes associated with MHC loci (`TAP1`, `TAP2`, `TAPBP`, `PSMB8`, `PSMB9`)

### Tier C: Not safe to ingest as canonical ontology without extra curation

- amplicon-only allele sets from survey papers
- study-local allele IDs that are not mirrored in GenBank or a curated database
- locus names with uncertain orthology across species
- copy-number-based labels that are not stable across assemblies or haplotypes

## What We Can Build Confidently First

### Phase 1: Taxonomy and source registry

Deliverables:

- add a source registry file for reptiles/amphibians
- define species prefixes using current scientific names and common aliases
- record provenance for every new species entry

Targets:

- frogs: `Xenopus laevis`, `Xenopus tropicalis`
- lizards: `Anolis carolinensis`, `Anolis sagrei`
- snakes: `Crotalus horridus` and close rattlesnake references from the genome paper
- turtles: `Caretta caretta`, `Chelonia mydas`, `Dermochelys coriacea`,
  `Lepidochelys kempii`
- crocodilians: `Crocodylus porosus` plus species from the Crocodylia survey
- other reptiles: `Sphenodon punctatus`

### Phase 2: Gene-level ontology only

Deliverables:

- species entries with gene families, not large allele registries
- tests for species parsing and representative gene parsing
- APG support where source annotation is clear

Targets:

- Xenopus genes from Xenbase
- `Anolis` core MHC genes from genome-backed annotations
- rattlesnake class I and class IIbeta family parsing
- crocodilian class I / class II family parsing

### Phase 3: Alias-level parsing for literature names

Deliverables:

- optional alias tables per clade
- provenance in comments or sidecar files
- tests from paper examples and GenBank-backed names

Targets:

- sea turtle class I / class II survey names
- selected crocodilian and salamander paper aliases

Constraint:

- these aliases should not be presented as official comparative nomenclature if
  they are only paper-local.

### Phase 4: Canonical allele ingestion only where a registry exists

This phase should happen only when one of the following is true:

- the clade enters `IPD-MHC`,
- the species has a stable curated allele registry,
- or we build a clearly provenance-annotated internal registry with accession-level
  traceability and conservative scope.

## Recommended First Implementation Order

1. `Xenopus` via Xenbase
2. `Anolis` via genome papers and NCBI Datasets
3. rattlesnakes via genome-backed class I / class IIbeta parsing
4. sea turtles as species + paper-alias support
5. crocodilians as species + gene-family support
6. salamanders only after a clear strategy for multigene class I handling
7. tuatara as an architecture stress-test species

## Design Constraints For mhcgnomes

To keep `mhcgnomes` coherent, new underrepresented-taxa ingestion should follow
these rules:

1. Separate canonical ontology from paper-local aliases.
2. Never invent stable allele names where the source community has not.
3. Prefer gene-family parsing over aggressive allele normalization when locus
   orthology is unresolved.
4. Keep provenance close to the data source.
5. Add one or more parser tests per source family before expanding breadth.

## Proposed Next Concrete Tasks

1. Add a source registry module or YAML sidecar for underrepresented taxa.
2. Add tests for existing `Sica` and `Xela` coverage so the current baseline is
   explicit.
3. Add `Xenopus tropicalis` and expand `Xenopus` gene metadata from Xenbase.
4. Add a first reptile pilot with `Anolis carolinensis`.
5. Add a second reptile pilot with `Crotalus horridus`.
6. Decide whether paper-local aliases should live in the main ontology or in
   separate alias tables.
