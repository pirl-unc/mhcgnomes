#!/usr/bin/env python3
"""
Extract MHC allele strings from a published paper's supplementary data.

Supports:
  - Excel files (.xlsx, .xls)
  - CSV/TSV files
  - Plain text (one allele per line or whitespace-separated)

The script scans all columns/cells for strings that look like MHC allele
names and outputs a validation TSV.

Usage:
    # Single file with known species
    python paper/scripts/scrape_paper.py \
        --input supp_table_S1.xlsx \
        --species "Parus major" \
        --source "PMID:12345678" \
        --output paper/validation/pmid_12345678.tsv

    # Auto-detect species from column headers
    python paper/scripts/scrape_paper.py \
        --input supp_table.csv \
        --source "doi:10.1234/example" \
        --output paper/validation/example.tsv

    # Batch: process all files in a directory
    python paper/scripts/scrape_paper.py \
        --input-dir paper/raw/pmid_12345678/ \
        --species "Gallus gallus" \
        --source "PMID:12345678" \
        --output paper/validation/pmid_12345678.tsv
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Patterns that look like MHC allele/gene names
MHC_PATTERNS = [
    # Standard allele: HLA-A*02:01, Mamu-B*017:01, BoLA-DRB3*01:01
    re.compile(
        r"\b[A-Z][A-Za-z0-9]{1,15}-[A-Za-z]{1,10}\*[\d:]+[A-Za-z]?\b"
    ),
    # Gene with prefix: HLA-A, Gaga-BF1, Dare-UBA, Modo-UA1
    re.compile(
        r"\b[A-Z][A-Za-z0-9]{1,15}-[A-Z][A-Za-z0-9]{0,8}\b"
    ),
    # Allele without prefix: A*02:01, DRB1*01:01, BF*21
    re.compile(r"\b[A-Z][A-Za-z0-9]{0,6}\*[\d:]+[A-Za-z]?\b"),
    # Mouse/rat style: H2-Kk, H2-Db, H-2Kb, RT1-Aa
    re.compile(r"\bH-?2-[A-Z][a-z0-9]*\b"),
    re.compile(r"\bRT1-[A-Za-z0-9.]+\b"),
    # Bird MHC with Mhc prefix: MhcPama-DAB1*01
    re.compile(r"\bMhc[A-Z][A-Za-z]+-[A-Za-z0-9*:]+\b"),
    # Non-mammalian: UAA*01, DAB*02:01, BLB1*04
    re.compile(r"\b(?:UA[A-Z]?|UB[A-Z]?|DA[AB]|DB[AB]|DC[AB]|DR[AB]|BLB|BF)\d?\*[\d:]+\b"),
    # Serotype-style: HLA-A2, HLA-B27, A2, B44
    re.compile(r"\bHLA-[A-Z]\d{1,3}\b"),
]

# Strings that match patterns but are NOT MHC names
FALSE_POSITIVE_PATTERNS = [
    re.compile(r"^\d+$"),  # bare numbers
    re.compile(r"^[A-Z]-\d+$"),  # plate coordinates like A-1
    re.compile(r"^rs\d+$"),  # SNP IDs
    re.compile(r"^chr\d", re.IGNORECASE),  # chromosome names
    re.compile(r"^ENSG\d"),  # Ensembl IDs
    re.compile(r"^LOC\d"),  # NCBI LOC IDs
    re.compile(r"^p\.\w+$"),  # protein changes
]


def looks_like_mhc(s):
    """Check if a string looks like an MHC allele/gene name."""
    s = s.strip()
    if len(s) < 3 or len(s) > 60:
        return False
    for fp in FALSE_POSITIVE_PATTERNS:
        if fp.match(s):
            return False
    for pat in MHC_PATTERNS:
        if pat.search(s):
            return True
    return False


def extract_from_text(text):
    """Extract MHC-like strings from free text."""
    candidates = set()
    for pat in MHC_PATTERNS:
        for match in pat.finditer(text):
            s = match.group()
            if not any(fp.match(s) for fp in FALSE_POSITIVE_PATTERNS):
                candidates.add(s)
    return candidates


def read_excel(path):
    """Read all sheets of an Excel file, return list of cell values."""
    try:
        import openpyxl
    except ImportError:
        print("Requires openpyxl: pip install openpyxl", file=sys.stderr)
        sys.exit(1)

    cells = []
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is not None:
                    cells.append(str(cell.value))
    wb.close()
    return cells


def read_csv_tsv(path):
    """Read a CSV or TSV file, return list of cell values."""
    cells = []
    with open(path, newline="", errors="replace") as f:
        # Sniff delimiter
        sample = f.read(4096)
        f.seek(0)
        if "\t" in sample:
            delimiter = "\t"
        elif "," in sample:
            delimiter = ","
        else:
            # Treat as one-per-line
            return [line.strip() for line in f if line.strip()]

        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            cells.extend(row)
    return cells


def read_text(path):
    """Read a plain text file, return list of lines/words."""
    with open(path, errors="replace") as f:
        return [line.strip() for line in f if line.strip()]


def process_file(path):
    """Read a file and extract MHC-like strings."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".xlsx", ".xls"):
        cells = read_excel(path)
    elif suffix in (".csv", ".tsv", ".txt"):
        cells = read_csv_tsv(path)
    else:
        cells = read_text(path)

    # Strategy 1: check if whole cells are MHC names
    mhc_strings = set()
    for cell in cells:
        cell = cell.strip()
        if looks_like_mhc(cell):
            mhc_strings.add(cell)

    # Strategy 2: extract MHC patterns from longer text cells
    for cell in cells:
        if len(cell) > 20:  # likely a sentence or description
            mhc_strings.update(extract_from_text(cell))

    return sorted(mhc_strings)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", help="Single input file")
    parser.add_argument("--input-dir", help="Directory of input files")
    parser.add_argument("--species", default="", help="Expected species (latin name)")
    parser.add_argument("--source", required=True, help="Source identifier (PMID or DOI)")
    parser.add_argument(
        "--output", default="-", help="Output TSV file (default: stdout)"
    )
    args = parser.parse_args()

    if not args.input and not args.input_dir:
        parser.error("Provide --input or --input-dir")

    # Collect input files
    input_files = []
    if args.input:
        input_files.append(Path(args.input))
    if args.input_dir:
        d = Path(args.input_dir)
        input_files.extend(
            sorted(
                p
                for p in d.iterdir()
                if p.suffix.lower() in (".xlsx", ".xls", ".csv", ".tsv", ".txt")
            )
        )

    if not input_files:
        print("No input files found.", file=sys.stderr)
        return 1

    # Extract from all files
    all_strings = set()
    for path in input_files:
        print(f"Processing {path}...", file=sys.stderr)
        strings = process_file(path)
        print(f"  Found {len(strings)} MHC-like strings", file=sys.stderr)
        all_strings.update(strings)

    print(f"\nTotal unique MHC strings: {len(all_strings)}", file=sys.stderr)

    # Write output
    out = sys.stdout if args.output == "-" else open(args.output, "w")
    writer = csv.DictWriter(
        out,
        fieldnames=["raw_string", "expected_species", "source"],
        delimiter="\t",
    )
    writer.writeheader()
    for s in sorted(all_strings):
        writer.writerow({
            "raw_string": s,
            "expected_species": args.species,
            "source": args.source,
        })

    if args.output != "-":
        out.close()
        print(f"Written to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
