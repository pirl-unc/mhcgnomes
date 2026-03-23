#!/usr/bin/env python3
"""
Collect MHC allele names from GenBank feature annotations.

Queries NCBI for MHC sequences and extracts the /allele= qualifier,
/gene= qualifier, and organism metadata. These represent real-world
MHC nomenclature as submitted by individual researchers.

Usage:
    python paper/scripts/collect_genbank.py --query "MHC[Gene] AND Aves[Organism]" --max 500
    python paper/scripts/collect_genbank.py --query "MHC class I[Title] AND fish" --max 500
"""

import argparse
import csv
import sys
import time
from io import StringIO

try:
    from Bio import Entrez, SeqIO
except ImportError:
    print("Requires biopython: pip install biopython", file=sys.stderr)
    sys.exit(1)

Entrez.email = "mhcgnomes-paper@example.com"


def search_genbank(query, max_results=500):
    """Search GenBank and return accession IDs."""
    handle = Entrez.esearch(db="nucleotide", term=query, retmax=max_results)
    result = Entrez.read(handle)
    handle.close()
    return result["IdList"]


def fetch_records(ids, batch_size=20):
    """Fetch GenBank records in batches."""
    records = []
    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        handle = Entrez.efetch(db="nucleotide", id=batch, rettype="gb", retmode="text")
        text = handle.read()
        handle.close()
        for record in SeqIO.parse(StringIO(text), "genbank"):
            records.append(record)
        time.sleep(0.5)  # be polite to NCBI
    return records


def extract_mhc_names(records):
    """Extract MHC allele/gene names from GenBank records."""
    rows = []
    for record in records:
        organism = record.annotations.get("organism", "")
        accession = record.id

        for feature in record.features:
            allele = feature.qualifiers.get("allele", [None])[0]
            gene = feature.qualifiers.get("gene", [None])[0]
            product = feature.qualifiers.get("product", [None])[0]
            note = feature.qualifiers.get("note", [None])[0]

            # Collect any MHC-related name
            for name_source, name in [
                ("allele", allele),
                ("gene", gene),
                ("product", product),
            ]:
                if name and any(
                    kw in name.upper()
                    for kw in [
                        "MHC",
                        "HLA",
                        "H-2",
                        "H2-",
                        "RT1",
                        "CLASS I",
                        "CLASS II",
                        "HISTOCOMPATIBILITY",
                        "DRB",
                        "DQB",
                        "DPB",
                        "DAB",
                        "UAA",
                        "UBA",
                        "BLB",
                        "BF",
                        "TAP",
                        "B2M",
                    ]
                ):
                    rows.append(
                        {
                            "raw_string": name,
                            "expected_species": organism,
                            "source": f"genbank:{accession}",
                            "qualifier": name_source,
                        }
                    )

    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="GenBank search query")
    parser.add_argument("--max", type=int, default=500, help="Max results")
    parser.add_argument("--output", default="-", help="Output TSV file")
    args = parser.parse_args()

    print(f"Searching GenBank: {args.query}", file=sys.stderr)
    ids = search_genbank(args.query, args.max)
    print(f"Found {len(ids)} records", file=sys.stderr)

    if not ids:
        return

    print("Fetching records...", file=sys.stderr)
    records = fetch_records(ids)
    print(f"Fetched {len(records)} records", file=sys.stderr)

    rows = extract_mhc_names(records)
    print(f"Extracted {len(rows)} MHC names", file=sys.stderr)

    out = sys.stdout if args.output == "-" else open(args.output, "w")
    writer = csv.DictWriter(
        out,
        fieldnames=["raw_string", "expected_species", "source", "qualifier"],
        delimiter="\t",
    )
    writer.writeheader()
    writer.writerows(rows)

    if args.output != "-":
        out.close()


if __name__ == "__main__":
    main()
