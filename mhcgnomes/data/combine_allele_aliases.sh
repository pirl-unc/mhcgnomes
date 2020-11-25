#!/usr/bin/env bash

python3 combine_allele_aliases.py \
	--xml IPD-MHC-3.5.0.1.xml \
	--yaml curated_allele_aliases.yaml \
	--allele-history-input-file IMGT-HLA-Allelelist-history-3.42.0.txt \
	--csv-input-file IMGT-HLA-Deleted-alleles-3.42.0.txt IMGT-HLA-Suffix-changes-3.42.0.txt \
	--output allele_aliases.yaml
