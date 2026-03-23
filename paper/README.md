# mhcgnomes paper — validation data

This directory contains held-out validation data for evaluating mhcgnomes
on MHC nomenclature "in the wild" — strings from published papers and
databases that were **not used during library development**.

## Directory structure

```
paper/
├── README.md              # this file
├── validation/            # raw allele lists from published sources
│   ├── sources.yaml       # metadata for each validation source
│   └── *.tsv              # one file per source, columns: raw_string, species, source
├── scripts/
│   ├── collect.py         # download/extract allele strings from sources
│   ├── evaluate.py        # run mhcgnomes on validation data, measure parse rate + correctness
│   └── summarize.py       # generate tables/figures for the paper
└── results/               # output from evaluation (gitignored)
```

## Validation sources

We specifically exclude data that mhcgnomes was developed against:
- IEDB allele lists
- IMGT/HLA allele lists
- IPD/MHC allele lists
- NetMHCpan/NetMHCIIpan allele lists
- mhcseqs/UniProt MHC sequence headers

Instead, we use:
- Supplementary tables from MHC genotyping papers
- Population genetics HLA frequency surveys
- Non-human MHC ecology/diversity studies (birds, fish, wildlife)
- GenBank `/allele=` qualifier annotations
- AFND (Allele Frequency Net Database) bulk data
- Clinical trial HLA restriction lists

## Evaluation metrics

1. **Parse rate**: % of strings that parse successfully
2. **Correctness**: For parsed strings, is the species/gene/allele correct?
   (Manual audit of stratified sample)
3. **Normalization yield**: How many raw "unique" strings collapse to how
   many canonical alleles?
4. **Round-trip fidelity**: `parse(x).to_string()` → `parse(result)` gives
   the same object
5. **Cross-species confusion rate**: Strings assigned to wrong species
