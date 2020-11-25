#!/usr/bin/env bash

# generates allele_aliases.yaml from a combination of manually curated mappings
# and automatic extraction of old allele designations from IPD-MHC and IMGT-HLA
python3 combine_allele_aliases.py \
	--xml IPD-MHC-3.5.0.1.xml \
	--yaml curated_allele_aliases.yaml \
	--allele-history-input-file IMGT-HLA-Allelelist-history-3.42.0.txt \
	--csv-input-file IMGT-HLA-Deleted-alleles-3.42.0.txt IMGT-HLA-Suffix-changes-3.42.0.txt \
	--output allele_aliases.yaml
