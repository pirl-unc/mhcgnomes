#!/usr/bin/env python3
"""
Rebuild committed paper validation artifacts from local paper/raw downloads.

This is an offline refresh path for when scrape heuristics or parser behavior
changes and the committed paper artifacts need to be regenerated without
re-running the network collection workflow.

Usage:
    python paper/scripts/rebuild_local_validation.py
    python paper/scripts/rebuild_local_validation.py --prefix PMC_6155461
"""

import argparse
import csv
from pathlib import Path

from collect_all_v2 import ROOT, REVIEW_DIR, VAL_DIR, deduplicate_validation_rows, generate_review_file
from scrape_paper import SUPPORTED_SUFFIXES, process_file


RAW_DIR = ROOT / "paper" / "raw"


def source_from_safe_id(safe_id):
    kind, identifier = safe_id.split("_", 1)
    return f"{kind}:{identifier}"


def write_validation_rows(path, rows):
    with open(path, "w") as fd:
        writer = csv.DictWriter(
            fd,
            fieldnames=["raw_string", "expected_species", "source"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)


def raw_dirs(prefix=None):
    directories = sorted(path for path in RAW_DIR.iterdir() if path.is_dir())
    if prefix:
        directories = [path for path in directories if path.name.startswith(prefix)]
    return directories


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prefix",
        help="Only rebuild raw directories whose name starts with this prefix",
    )
    parser.add_argument(
        "--include-new-papers",
        action="store_true",
        help="Also create merged/review artifacts for PMC papers that were not already committed",
    )
    args = parser.parse_args()

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    VAL_DIR.mkdir(parents=True, exist_ok=True)

    pmid_rows = []
    pmc_rows = []
    processed_dirs = 0

    for directory in raw_dirs(args.prefix):
        input_files = sorted(
            path for path in directory.iterdir() if path.suffix.lower() in SUPPORTED_SUFFIXES
        )
        if not input_files:
            continue

        safe_id = directory.name
        source = source_from_safe_id(safe_id)
        paper_rows = []
        processed_dirs += 1
        print(f"Rebuilding {safe_id} ({len(input_files)} files)")

        for input_file in input_files:
            output_path = VAL_DIR / f"{safe_id}_{input_file.stem}.tsv"
            try:
                strings = process_file(input_file)
            except Exception as exc:
                print(f"  Skipping {input_file.name}: {exc}")
                continue
            rows = [
                {
                    "raw_string": raw_string,
                    "expected_species": "",
                    "source": source,
                }
                for raw_string in strings
            ]

            if rows or output_path.exists():
                write_validation_rows(output_path, rows)

            paper_rows.extend(rows)

        if safe_id.startswith("PMC_"):
            merged_rows = deduplicate_validation_rows(paper_rows)
            merged_path = VAL_DIR / f"{safe_id}_merged.tsv"
            review_path = REVIEW_DIR / f"{safe_id}_review.tsv"
            if args.include_new_papers or merged_path.exists() or review_path.exists():
                write_validation_rows(merged_path, merged_rows)
                generate_review_file(merged_path, review_path)
            pmc_rows.extend(merged_rows)
        elif safe_id.startswith("PMID_"):
            pmid_rows.extend(paper_rows)

    print(f"Rebuilt {processed_dirs} raw directories")
    if args.prefix:
        print("Skipped consolidated all_papers outputs because --prefix was set")
        return

    write_validation_rows(
        VAL_DIR / "all_papers.tsv",
        deduplicate_validation_rows(pmid_rows),
    )
    write_validation_rows(
        VAL_DIR / "all_papers_v2.tsv",
        deduplicate_validation_rows(pmc_rows),
    )

    print(f"Updated {VAL_DIR / 'all_papers.tsv'}")
    print(f"Updated {VAL_DIR / 'all_papers_v2.tsv'}")


if __name__ == "__main__":
    main()
