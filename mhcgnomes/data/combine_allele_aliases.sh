#!/usr/bin/env bash

python3 combine_allele_aliases.py \
	--xml IPD-MHC-3.5.0.1.xml \
	--yaml curated_allele_aliases.yaml \
	--output test.yaml
