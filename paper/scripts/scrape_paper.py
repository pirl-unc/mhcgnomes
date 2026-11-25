#!/usr/bin/env python3
"""
Extract MHC allele strings from a published paper's supplementary data.

Supports:
  - Excel files (.xlsx, .xls)
  - CSV/TSV files
  - Word documents (.docx)
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
import functools
import re
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = (".xlsx", ".xls", ".csv", ".tsv", ".txt", ".docx")

# Fallback prefixes used only if mhcgnomes cannot be imported.
_FALLBACK_SPECIES_PREFIXES = frozenset(
    {
        "hla",
        "h2",
        "h-2",
        "rt1",
        "bola",
        "sla",
        "dla",
        "fla",
        "ela",
        "ola",
        "cla",
        "mamu",
        "mafa",
        "patr",
        "gogo",
        "popy",
        "gaga",
        "dare",
        "modo",
        "saha",
        "xela",
        "onmy",
        "sasa",
    }
)

# Unambiguous multi-letter MHC gene/locus names usable with novel 4-letter
# Klein-style species prefixes (e.g. "Newx-DAB1") not yet in the ontology.
_UNAMBIGUOUS_MHC_GENE_RE = re.compile(
    r"^(?:"
    r"D[RQPMOABCXYN][AB]\d*(?:-\d+)?"
    r"|U[A-H]A?\d*"
    r"|U[IJMOK]\d*"
    r"|UT\d+"
    r"|BLB\d*|BLA|BF\d+|YF\d+"
    r"|MICA|MICB|MIC\d+"
    r"|CD1[A-Ea-e]?"
    r"|NC\d+"
    r")$"
)

# Gene/locus/serotype tokens allowed after a known MHC species prefix when no
# '*' allele separator is present (e.g. HLA-A, HLA-A2, HLA-DRB1, SLA-1, Gaga-BF1).
_KNOWN_PREFIX_GENE_RE = re.compile(
    r"^(?:"
    r"D[RQPMOABCXYN][AB]?\d*(?:-\d+|(?:\.\d+))?"
    r"|U[A-Z]\d*"
    r"|U[A-H]A\d*"
    r"|BLB\d*|BLA|BF\d*|YF\d*"
    r"|MICA|MICB|MIC\d*|MR1|HFE|B2M|CD1[A-Ea-e]?"
    r"|NC\d+|Z[A-Z]A|L[A-Z]A"
    r"|Q\d+[a-z]?|T\d+[a-z]?|M\d+(?:[.-]\d+)?"
    r"|I[AE][ab]?\d*[a-z]?"
    r"|A[A-Za-z0-9]{0,4}|B[A-Za-z0-9]{0,4}|C[A-Za-z0-9]{0,4}"
    r"|[DEFGHJKLNPSTUVWYZ]\d{0,3}[a-z]?"
    r"|[1-9]\d?"
    r")$"
)

# Non-MHC suffix tokens that must never be accepted after a hyphen even if the
# prefix happens to collide with a species code (e.g. MHC-I, RIG-I, HLA-class).
_DISALLOWED_GENE_TOKENS = frozenset(
    {
        "I",
        "II",
        "III",
        "IV",
        "V",
        "MHC",
        "PCR",
        "DNA",
        "RNA",
        "SNP",
        "GWAS",
        "LIKE",
        "CLASS",
        "ALPHA",
        "BETA",
        "CHAIN",
        "GENE",
        "ALLELE",
        "LOCUS",
        "REGION",
        "NOT",
        "ROBO",
        "GAP",
        "COA",
        "GLCNAC",
        "DOL",
        "PRO",
        "GLY",
        "GDP",
        "GTP",
        "ATP",
        "EUROPEAN",
        "FRIESIAN",
        "AMERICAN",
        "AFRICAN",
        "ASIAN",
    }
)

# Specific MHC token patterns (ordered roughly from most specific to least).
MHC_PATTERNS = [
    # Slash-separated paired alleles with prefixes:
    # HLA-DRA*01:01/HLA-DRB1*01:01, Clgl-DQA*08:02/Clgl-DQA*08:01
    re.compile(
        r"\b(?:Mhc)?[A-Z][A-Za-z0-9]{1,15}-[A-Za-z0-9]{1,10}\*[\d:]+[A-Za-z]?"
        r"/(?:(?:Mhc)?[A-Z][A-Za-z0-9]{1,15}-)?[A-Za-z0-9]{1,10}\*[\d:]+[A-Za-z]?\b"
    ),
    # Standard allele with species prefix: HLA-A*02:01, Mamu-B*017:01, SLA-1*04:01, MhcPama-DAB1*01
    re.compile(r"\b(?:Mhc)?[A-Z][A-Za-z0-9]{1,15}-[A-Za-z0-9]{1,10}\*[\d:]+[A-Za-z]?\b"),
    # Bird / non-human MHC with explicit Mhc prefix: MhcPama-DAB1, MhcSphu_CLSI
    re.compile(r"\bMhc[A-Z][A-Za-z]{2,15}-[A-Za-z0-9]+(?:\*[\d:]+[A-Za-z]?)?\b"),
    # Mouse/rat style: H2-Kk, H2-Db, H-2-Qa1, H2-IAb, H2-b/d, RT1-Aa, RT1-A1*a
    re.compile(r"\bH-?2-(?:I[AE][a-z0-9]*|[A-Z][A-Za-z0-9]*(?:\*[\da-z:]+)?)\b"),
    re.compile(r"\bRT1-[A-Za-z0-9.]+(?:\*[\da-z:]+)?\b"),
    # Starred allele without species prefix: A*02:01, DRB1*01:01, BF*21, UAA*01, DAB*02:01
    re.compile(r"\b[A-Z][A-Za-z0-9]{0,6}\*[\d:]+[A-Za-z]?\b"),
    # HLA serotype/heterodimer/locus style: HLA-A2, HLA-B27, HLA-DQ2.5, HLA-DR15
    re.compile(r"\bHLA-(?:D[RQP][AB]?\d*(?:\.\d+)?|[A-Z]\d{0,3}[a-z]?)\b"),
    # Generic prefixed gene/locus (filtered by _is_valid_prefixed_mhc_token)
    re.compile(r"\b[A-Z][A-Za-z0-9]{1,15}-[A-Za-z0-9]{1,10}\b"),
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
    re.compile(r"^MHC-I{1,3}[ABab]?$", re.IGNORECASE),  # generic class labels like MHC-I, MHC-II
    re.compile(r"^IPD-MHC$", re.IGNORECASE),  # database name
]


@functools.lru_cache(maxsize=1)
def _known_species_prefixes():
    """Return lowercase known MHC species prefixes from mhcgnomes, with fallback."""
    try:
        from mhcgnomes.species import latin_name_to_species_object
    except Exception:
        return _FALLBACK_SPECIES_PREFIXES

    prefixes = set(_FALLBACK_SPECIES_PREFIXES)
    for sp in latin_name_to_species_object.values():
        for pref in (*sp.all_mhc_prefixes, *sp.context_only_mhc_prefixes):
            low = pref.lower()
            # Exclude bare generic labels that collide with English/biochem words.
            if low and low not in {"mhc", "nhp"}:
                prefixes.add(low)
    return frozenset(prefixes)


def _is_valid_prefixed_mhc_token(token):
    """Validate an unstarred ``<Prefix>-<Gene>`` candidate token."""
    if "*" in token or "/" in token:
        return True
    if token.startswith(("H2-", "H-2-", "RT1-", "Mhc")):
        return True
    if "-" not in token:
        return True

    prefix, _, gene = token.partition("-")
    if not prefix or not gene:
        return False
    if gene.upper() in _DISALLOWED_GENE_TOKENS:
        return False
    if prefix.upper() == "MHC":
        return bool(_UNAMBIGUOUS_MHC_GENE_RE.fullmatch(gene))
    if prefix.upper() in {"IPD", "IMGT", "UDP", "GDP", "CMP", "ATP", "GTP", "RNA", "DNA"}:
        return False

    known_prefixes = _known_species_prefixes()
    if prefix.lower() in known_prefixes:
        return bool(_KNOWN_PREFIX_GENE_RE.fullmatch(gene))

    # Allow novel Klein-style 4-letter mixed-case species prefixes (e.g. "Newx-DAB1")
    # only when paired with an unambiguous multi-letter MHC gene family.
    return bool(re.fullmatch(r"[A-Z][a-z]{3}", prefix) and _UNAMBIGUOUS_MHC_GENE_RE.fullmatch(gene))


def _is_valid_candidate(token):
    """Return True if a matched single token passes false-positive and prefix checks."""
    if len(token) < 3 or len(token) > 60:
        return False
    if any(fp.match(token) for fp in FALSE_POSITIVE_PATTERNS):
        return False
    return _is_valid_prefixed_mhc_token(token)


def looks_like_mhc(s):
    """Check if a whole cell string looks like an MHC allele/gene name."""
    s = s.strip()
    if len(s) < 3 or len(s) > 60:
        return False
    if any(ch.isspace() for ch in s):
        return False
    if not _is_valid_candidate(s):
        return False
    return any(pat.fullmatch(s) for pat in MHC_PATTERNS)


def extract_from_text(text):
    """Extract non-overlapping MHC-like tokens from free text.

    Prefers the longest match at any position so complete allele strings such as
    ``HLA-C*12:02`` do not also emit redundant substrings (``HLA-C``, ``C*12:02``)
    unless those shorter forms occur independently elsewhere in ``text``.
    """
    raw_matches = []
    for pat in MHC_PATTERNS:
        for match in pat.finditer(text):
            token = match.group()
            if _is_valid_candidate(token):
                raw_matches.append((match.start(), match.end(), token))

    # Prefer longest spans first, breaking ties by earliest start position.
    raw_matches.sort(key=lambda item: (-(item[1] - item[0]), item[0]))

    accepted_spans = []
    candidates = set()
    for start, end, token in raw_matches:
        if any(start < prev_end and end > prev_start for prev_start, prev_end in accepted_spans):
            continue
        accepted_spans.append((start, end))
        candidates.add(token)
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


def read_docx(path):
    """Read a .docx file and return paragraphs + table cells as text."""
    try:
        import xml.etree.ElementTree as ET
        import zipfile
    except ImportError:
        return []

    texts = []
    try:
        with zipfile.ZipFile(path) as z:
            # Read main document
            if "word/document.xml" in z.namelist():
                tree = ET.parse(z.open("word/document.xml"))
                for para in tree.iter(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
                ):
                    text = "".join(
                        node.text or ""
                        for node in para.iter(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
                        )
                    )
                    if text.strip():
                        texts.append(text.strip())
    except Exception:
        pass
    return texts


def process_file(path):
    """Read a file and extract MHC-like strings."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".xlsx", ".xls"):
        cells = read_excel(path)
    elif suffix in (".csv", ".tsv", ".txt"):
        cells = read_csv_tsv(path)
    elif suffix == ".docx":
        cells = read_docx(path)
    else:
        cells = read_text(path)

    mhc_strings = set()
    for cell in cells:
        cell = cell.strip()
        if not cell:
            continue
        # Strategy 1: whole cell is a single MHC token.
        if looks_like_mhc(cell):
            mhc_strings.add(cell)
        else:
            # Strategy 2: extract non-overlapping MHC tokens from multi-token text.
            mhc_strings.update(extract_from_text(cell))

    return sorted(mhc_strings)


def collect_input_files(input_file=None, input_dir=None):
    """Collect supported input files from a single path and/or directory."""
    input_files = []
    if input_file:
        input_files.append(Path(input_file))
    if input_dir:
        d = Path(input_dir)
        input_files.extend(
            sorted(p for p in d.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS)
        )
    return input_files


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", help="Single input file")
    parser.add_argument("--input-dir", help="Directory of input files")
    parser.add_argument("--species", default="", help="Expected species (latin name)")
    parser.add_argument("--source", required=True, help="Source identifier (PMID or DOI)")
    parser.add_argument("--output", default="-", help="Output TSV file (default: stdout)")
    args = parser.parse_args()

    if not args.input and not args.input_dir:
        parser.error("Provide --input or --input-dir")

    input_files = collect_input_files(input_file=args.input, input_dir=args.input_dir)

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
        writer.writerow(
            {
                "raw_string": s,
                "expected_species": args.species,
                "source": args.source,
            }
        )

    if args.output != "-":
        out.close()
        print(f"Written to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
