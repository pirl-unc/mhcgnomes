# mhcgnomes paper — validation data

This directory contains held-out validation data for evaluating mhcgnomes
on MHC nomenclature "in the wild" — strings from published papers and
databases that were **not used during library development**.

## Directory structure

```
paper/
├── README.md              # this file
├── validation/            # extracted allele lists (TSV, committed)
│   ├── sources.yaml       # metadata for each validation source
│   ├── candidate_papers.tsv  # PubMed search results for manual review
│   └── *.tsv              # one file per source, columns: raw_string, species, source
├── raw/                   # downloaded supplementary files (gitignored)
├── scripts/
│   ├── collect_pubmed.py  # systematic PubMed search for validation papers
│   ├── collect_genbank.py # extract MHC names from GenBank annotations
│   ├── scrape_paper.py    # extract MHC strings from Excel/CSV/text files
│   ├── batch_collect.sh   # download + scrape workflow
│   └── evaluate.py        # run mhcgnomes on validation data, measure parse rate + correctness
└── results/               # output from evaluation (gitignored)
```

## Quick start

```bash
# 1. Find candidate papers (already done — see validation/candidate_papers.tsv)
python paper/scripts/collect_pubmed.py

# 2. Download and scrape a paper's supplementary table
./paper/scripts/batch_collect.sh add "PMID:34567890" "Parus major" \
    https://example.com/supp_table_S1.xlsx

# 3. Or scrape a file you already downloaded
./paper/scripts/batch_collect.sh scrape "PMID:34567890" "Parus major" \
    paper/raw/PMID_34567890/table.xlsx

# 4. Collect MHC names from GenBank
python paper/scripts/collect_genbank.py \
    --query '"major histocompatibility" AND Aves[Organism]' \
    --max 500 --output paper/validation/genbank_birds.tsv

# 5. Evaluate all collected data
./paper/scripts/batch_collect.sh eval
```

## Systematic collection methodology

### Exclusion criteria

We specifically exclude data that mhcgnomes was developed or tuned against:
- IEDB allele lists and epitope exports
- IMGT/HLA allele lists
- IPD/MHC allele lists and sequence databases
- NetMHCpan/NetMHCIIpan allele lists
- mhcseqs/UniProt MHC sequence headers
- Any paper whose supplementary data was manually reviewed during
  mhcgnomes gene or species curation

### Source categories

Validation data comes from five independent source categories, chosen
to cover different species groups, nomenclature conventions, and levels
of curation:

| Category | What it tests | Expected messiness |
| --- | --- | --- |
| **A. GenBank annotations** | `/allele=`, `/gene=`, `/product=` qualifiers on MHC sequences submitted by individual researchers | High — no editorial normalization |
| **B. Published supplementary tables** | MHC allele lists from genotyping/diversity papers | Medium-high — author-chosen notation |
| **C. Population frequency databases** | AFND, HLA frequency surveys | Medium — lab-submitted names with some curation |
| **D. Clinical/vaccine literature** | HLA restrictions from trial protocols and immunology methods sections | Low-medium — mostly human, but notation varies by era and journal |
| **E. Sequence database headers** | FASTA deflines from GenBank/ENA MHC sequence submissions | High — free-text, no schema |

### Paper selection protocol

To collect a diverse and unbiased set of published MHC allele strings:

#### Step 1: Stratified PubMed search

Run one PubMed query per taxonomic stratum. Each query targets papers
that contain MHC genotyping data with allele-level results, published
2015–2025.

| Stratum | PubMed query template | Target N |
| --- | --- | --- |
| Human (clinical) | `"HLA typing" OR "HLA genotyping" AND (supplementary OR table)` | 10 papers |
| Human (population) | `"HLA frequency" OR "HLA distribution" AND population` | 10 papers |
| Non-human primates | `"MHC genotyping" AND (macaque OR chimpanzee OR marmoset)` | 5 papers |
| Rodents | `"MHC" AND (mouse OR rat) AND (haplotype OR genotyping) NOT review` | 5 papers |
| Birds | `"MHC diversity" AND (passerine OR raptor OR penguin OR waterfowl)` | 10 papers |
| Fish | `"MHC" AND (salmonid OR cichlid OR zebrafish OR carp) AND diversity` | 5 papers |
| Reptiles/amphibians | `"MHC" AND (turtle OR lizard OR snake OR frog) AND (class I OR class II)` | 5 papers |
| Livestock | `"MHC" OR "BoLA" OR "SLA" OR "OLA" AND (genotyping OR typing)` | 5 papers |
| Wildlife/conservation | `"MHC diversity" AND (endangered OR conservation OR bottleneck)` | 5 papers |

**Total target: ~60 papers, ~2000–5000 unique MHC strings.**

#### Step 2: Inclusion criteria for each paper

A paper is included if it meets ALL of:

1. Contains a table, supplementary file, or inline list of ≥10 MHC
   allele or gene names
2. The allele names are extractable (not embedded in figures only)
3. The paper was NOT cited in mhcgnomes source comments or used during
   curation
4. At least one non-human species OR at least one non-standard human
   HLA notation (older format, serotype, workshop name)

#### Step 3: Data extraction

For each included paper:

1. Download the supplementary table or copy the allele list from the paper
2. Extract all MHC-related strings into a TSV with columns:
   `raw_string`, `expected_species`, `source` (DOI or PMID)
3. Record the paper metadata in `sources.yaml`
4. Do NOT normalize or clean the strings — preserve exactly what the
   authors wrote

#### Step 4: Deduplication

- Keep duplicate strings from different papers (they test whether the
  same name is handled consistently)
- Remove exact-duplicate rows within a single paper (same string, same
  source)
- Record both raw and deduplicated counts

### GenBank collection protocol

For each taxonomic group, query GenBank for MHC sequences and extract
the `/allele=`, `/gene=`, and `/product=` qualifiers:

```bash
# Birds
python paper/scripts/collect_genbank.py \
  --query '"major histocompatibility" AND Aves[Organism]' \
  --max 500 --output paper/validation/genbank_birds.tsv

# Fish
python paper/scripts/collect_genbank.py \
  --query '"major histocompatibility" AND Actinopterygii[Organism]' \
  --max 500 --output paper/validation/genbank_fish.tsv

# Reptiles
python paper/scripts/collect_genbank.py \
  --query '"major histocompatibility" AND Reptilia[Organism]' \
  --max 500 --output paper/validation/genbank_reptiles.tsv

# Non-human mammals (excluding model organisms)
python paper/scripts/collect_genbank.py \
  --query '"MHC class" AND Mammalia[Organism] NOT Homo[Organism] NOT Mus[Organism]' \
  --max 500 --output paper/validation/genbank_mammals.tsv
```

Filter to only `/gene=` and `/allele=` qualifiers (exclude `/product=`
descriptions which are free-text sentences, not parseable allele names).

### AFND collection protocol

Download allele frequency tables from the Allele Frequency Net Database
(http://www.allelefrequencies.net/). AFND contains HLA allele names as
submitted by individual laboratories, before any normalization. Extract
the allele name column and record the population/study metadata.

## Evaluation metrics

1. **Parse rate**: % of strings that parse successfully, stratified by
   source category and taxonomic group
2. **Correctness**: For parsed strings, is the species/gene/allele correct?
   Manual audit of a stratified random sample (N=200, 25 per stratum)
3. **Normalization yield**: How many raw "unique" strings collapse to how
   many canonical alleles after parsing and `to_string()` normalization?
4. **Round-trip fidelity**: Does `parse(parse(x).to_string())` give the
   same object as `parse(x)`?
5. **Cross-species confusion rate**: Strings assigned to the wrong species
   (subset of correctness audit)
6. **Failure analysis**: Categorize unparsed strings into: unknown species,
   unknown gene, malformed format, genuine ambiguity, not-MHC

## Comparison baselines

- **Regex baseline**: Simple pattern matching (e.g., `HLA-[ABC]\*\d+:\d+`)
- **String matching**: Exact lookup against IMGT/HLA allele list
- **No-op baseline**: Accept everything as unparsed

These provide context for the parse rate numbers — a library that parses
everything trivially has 100% parse rate but 0% correctness on non-MHC
strings.
