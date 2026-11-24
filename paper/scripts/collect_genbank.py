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

try:
    import biotite.database.entrez as entrez
    import biotite.sequence.io.genbank as genbank
except ImportError:
    print("Requires biotite: pip install biotite", file=sys.stderr)
    sys.exit(1)


class RawEntrezQuery(entrez.Query):
    """Wrap a raw NCBI Entrez query string for biotite.database.entrez.search."""

    def __init__(self, term):
        self.term = term

    def __str__(self):
        return self.term


def search_genbank(query, max_results=500):
    """Search GenBank and return accession IDs."""
    return entrez.search(RawEntrezQuery(query), "nuccore", number=max_results)


def fetch_records(ids, batch_size=20):
    """Fetch GenBank records in batches."""
    records = []
    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        handle = entrez.fetch_single_file(
            batch, None, "nuccore", ret_type="gb", ret_mode="text"
        )
        for record in genbank.MultiFile.read(handle):
            records.append(record)
        time.sleep(0.5)  # be polite to NCBI
    return records


def extract_organism(record):
    """Extract the organism name from a biotite GenBankFile record."""
    for feature in genbank.get_annotation(record):
        if feature.key == "source" and "organism" in feature.qual:
            return feature.qual["organism"]
    return genbank.get_source(record) or ""


def extract_mhc_names(records):
    """Extract MHC allele/gene names from GenBank records."""
    rows = []
    for record in records:
        organism = extract_organism(record)
        accession = genbank.get_accession(record)

        for feature in genbank.get_annotation(record):
            allele = feature.qual.get("allele")
            gene = feature.qual.get("gene")
            product = feature.qual.get("product")

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
