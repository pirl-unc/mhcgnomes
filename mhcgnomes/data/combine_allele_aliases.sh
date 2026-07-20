#!/usr/bin/env bash

# generates allele_aliases.yaml from a combination of manually curated mappings
# and automatic extraction of old allele designations from IPD-MHC and IMGT-HLA
set -euo pipefail

data_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(cd "$data_dir/../.." && pwd)
external_data_dir=${MHCGNOMES_EXTERNAL_DATA_DIR:-"$repo_root/.external-data"}

cd "$repo_root"
python3 -m mhcgnomes data download \
    --group allele-aliases \
    --destination "$external_data_dir"

python3 "$data_dir/combine_allele_aliases.py" \
    --xml-input-file "$external_data_dir/IPD-MHC-3.8.0.0.xml" \
    --yaml-input-file "$data_dir/curated_allele_aliases.yaml" \
    --allele-history-input-file \
        "$external_data_dir/IMGT-HLA-Allelelist-history-3.42.0.txt" \
    --csv-input-file "$external_data_dir/IMGT-HLA-Deleted-alleles-3.42.0.txt" \
    --output "$data_dir/allele_aliases.yaml"
