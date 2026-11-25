#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

download_if_missing() {
    local url="$1"
    local dest="$2"
    if [[ ! -f "$dest" ]]; then
        curl -fsSL -o "$dest" "$url"
    fi
}

# IEDB T-cell export
download_if_missing \
    "https://www.iedb.org/downloader.php?file_name=doc/tcell_full_v3.zip" \
    "tcell.zip"
if [[ ! -f "tcell.csv" ]]; then
    unzip -o tcell.zip
    mv tcell_full_v3.csv tcell.csv
fi

# IEDB MHC ligand export
download_if_missing \
    "https://www.iedb.org/downloader.php?file_name=doc/mhc_ligand_full_single_file.zip" \
    "mhc_ligand_full_single_file.zip"
if [[ ! -f "mhc_ligand_full.csv" ]]; then
    unzip -o mhc_ligand_full_single_file.zip
fi

# Mouse reference FASTAs used by 1 - Create data files.ipynb
UNIPROT_ACCESSIONS=(
    P01899 P01900 P14427 P14426 Q31145 Q31170  # H-2 D
    P01901 P01902 P04223 P14428 Q64272 Q61642  # H-2 K
    P01897 Q31151                              # H-2 L
    P14429 P14430 P14431 P01898 Q8HWB0         # non-classical H-2 Q / MR1
)
for acc in "${UNIPROT_ACCESSIONS[@]}"; do
    download_if_missing \
        "https://rest.uniprot.org/uniprotkb/${acc}.fasta" \
        "${acc}.fasta"
done

# IPD-IMGT/HLA and IPD-MHC protein FASTAs read from ../.external-data/
(cd .. && mhcgnomes data download --group validation)
