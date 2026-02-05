#!/usr/bin/env python3
"""
Generate serotype-to-allele mappings from the IPD-IMGT/HLA dictionary.

Source: https://www.ebi.ac.uk/ipd/imgt/hla/alleles/dictionary/
The HLA dictionary contains WHO-assigned serotypes for HLA alleles.

This script parses the Excel file and generates YAML mappings.
"""

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml


def parse_serotype(serotype_str: str) -> list[str]:
    """
    Parse a serotype string, handling complex formats.

    Examples:
        "A1" -> ["A1"]
        "A23(9)" -> ["A23"]  # Split of A9
        "A2/19" -> ["A2", "A19"]  # Multiple assignments
        "Low A24(9)" -> ["A24"]  # Ignore "Low" prefix
        "-" -> []  # No assignment
        "Null" -> []  # Null allele
        "Not expressed" -> []
        "?B44(12)" -> []  # Skip uncertain assignments
        "Soluble" -> []  # Skip soluble designation
        "Cw9(w3)" -> ["Cw9"]  # Handle workshop split notation
    """
    if not serotype_str or serotype_str in ["-", "Null", "Not expressed", "Soluble"]:
        return []

    # Skip uncertain assignments (starting with ?)
    if serotype_str.startswith("?"):
        return []

    # Remove "Low " prefix
    serotype_str = re.sub(r"^Low\s+", "", serotype_str)

    # Handle split serotypes like "A23(9)" or "Cw9(w3)" -> extract base serotype
    # The content in parens is the broad serotype it splits from
    serotype_str = re.sub(r"\([wW]?\d+\)", "", serotype_str)

    # Handle percentage confidence like "A1 [98-100]" -> "A1"
    serotype_str = re.sub(r"\s*\[[\d\-]+\]", "", serotype_str)

    # Split on "/" for multiple assignments
    parts = serotype_str.split("/")

    serotypes = []
    for part in parts:
        part = part.strip()
        # Skip if it's just a number (like in "A2/19" where 19 means A19)
        if part.isdigit():
            continue
        # Skip empty or "blank"
        if not part or part.lower() == "blank":
            continue
        serotypes.append(part)

    return serotypes


def normalize_allele_name(allele: str) -> str:
    """
    Normalize allele name to two-field format for consistency.

    Examples:
        "A*01:01:01:01" -> "A*0101"
        "A*01:01:02N" -> "A*0101"  # Remove suffix
        "DRB1*01:01" -> "DRB1*0101"
        "B*15:102" -> "B*15102"  # Three-digit second field (kept as-is)
    """
    # Remove any suffix (N for null, L for low, etc.)
    allele = re.sub(r"[NLSQA]$", "", allele)

    # Parse the allele format
    match = re.match(r"([A-Z0-9]+)\*(\d+):(\d+)", allele)
    if match:
        gene = match.group(1)
        field1 = match.group(2).zfill(2)
        field2 = match.group(3)
        # Keep 3-digit second fields as-is (e.g., 102, 103)
        # For 1-2 digit fields, pad to 2 digits
        if len(field2) <= 2:
            field2 = field2.zfill(2)
        return f"{gene}*{field1}{field2}"

    return allele


def load_hla_dictionary(xlsx_path: Path) -> pd.DataFrame:
    """Load the HLA dictionary Excel file."""
    return pd.read_excel(xlsx_path, sheet_name="A")


def build_serotype_mappings(df: pd.DataFrame) -> dict[str, dict[str, list[str]]]:
    """
    Build serotype-to-allele mappings from the HLA dictionary.

    Returns a nested dict: {gene: {serotype: [alleles]}}
    """
    # Group alleles by their WHO-assigned serotype
    serotype_to_alleles: dict[str, set[str]] = defaultdict(set)

    for _, row in df.iterrows():
        allele = row["HLA Allele"]
        who_serotype = row.get("WHO Assigned Type", "")

        # Skip if no WHO assignment
        if pd.isna(who_serotype):
            continue

        serotypes = parse_serotype(str(who_serotype))
        if not serotypes:
            continue

        # Normalize the allele name
        normalized = normalize_allele_name(allele)

        for serotype in serotypes:
            serotype_to_alleles[serotype].add(normalized)

    # Organize by gene prefix (A, B, C, DR, DQ, DP)
    result: dict[str, dict[str, list[str]]] = {}

    for serotype, alleles in sorted(serotype_to_alleles.items()):
        # Sort alleles for consistent output
        sorted_alleles = sorted(alleles)
        result[serotype] = sorted_alleles

    return result


def generate_yaml(mappings: dict[str, list[str]], existing_yaml_path: Path) -> str:
    """Generate YAML output, preserving non-HLA entries and manually curated HLA entries."""
    # Load existing YAML to preserve non-HLA entries and manual HLA curation
    with open(existing_yaml_path) as f:
        existing = yaml.safe_load(f)

    # Extract non-HLA entries
    non_hla = {k: v for k, v in existing.items() if k != "HLA"}

    # Build HLA section
    hla_section = {}

    # Add special entries first (Bw4, Bw6, Aw68, Aw69)
    # These are public epitopes/workshop antigens that we'll preserve manually
    special_serotypes = ["Aw68", "Aw69", "Bw4", "Bw6"]
    if "HLA" in existing:
        for special in special_serotypes:
            if special in existing["HLA"]:
                hla_section[special] = existing["HLA"][special]

    # Add WHO-assigned serotypes from dictionary
    for serotype, alleles in sorted(mappings.items()):
        if serotype not in special_serotypes:
            hla_section[serotype] = alleles

    # Preserve existing HLA entries that aren't in the dictionary
    # (e.g., DP workshop serotypes, some C serotypes)
    if "HLA" in existing:
        for serotype, alleles in existing["HLA"].items():
            if serotype not in hla_section:
                hla_section[serotype] = alleles

    # Build output
    output = {"HLA": hla_section}
    output.update(non_hla)

    return output


def main():
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "mhcgnomes" / "data"
    xlsx_path = data_dir / "hla_dictionary.xlsx"
    yaml_path = data_dir / "serotypes.yaml"

    print(f"Loading HLA dictionary from {xlsx_path}")
    df = load_hla_dictionary(xlsx_path)
    print(f"Loaded {len(df)} alleles")

    print("Building serotype mappings...")
    mappings = build_serotype_mappings(df)
    print(f"Found {len(mappings)} serotypes")

    for serotype, alleles in sorted(mappings.items())[:10]:
        print(f"  {serotype}: {len(alleles)} alleles")
    print("  ...")

    print(f"Generating YAML, preserving non-HLA from {yaml_path}")
    output = generate_yaml(mappings, yaml_path)

    # Write to a new file for review
    output_path = data_dir / "serotypes_generated.yaml"

    # Custom YAML dump for better formatting
    with open(output_path, "w") as f:
        f.write(
            """############################################################
#
# Serotypes and the list of alleles they contain.
# Generated from IPD-IMGT/HLA Dictionary:
# https://www.ebi.ac.uk/ipd/imgt/hla/alleles/dictionary/
#
# The WHO Assigned Type column is used for serotype assignments.
#
############################################################

"""
        )

        # Write HLA section
        f.write("HLA:\n")
        hla = output["HLA"]

        # Write special serotypes first with comments
        special_with_comments = {
            "Aw68": "  # Old workshop serotype (now A68)",
            "Aw69": "  # Old workshop serotype (now A69)",
            "Bw4": "  # Public epitope (supertype)",
            "Bw6": "  # Public epitope (supertype)",
        }

        for special, comment in special_with_comments.items():
            if special in hla:
                f.write(f"  {special}:{comment}\n")
                for allele in hla[special]:
                    f.write(f"    - {allele}\n")
                f.write("\n")

        # Write remaining serotypes
        for serotype in sorted(hla.keys()):
            if serotype in special_with_comments:
                continue
            alleles = hla[serotype]
            f.write(f"  {serotype}:\n")
            for allele in alleles:
                f.write(f"    - {allele}\n")

        # Write non-HLA sections
        for species, serotypes in output.items():
            if species == "HLA":
                continue
            f.write(f"\n{species}:\n")
            for serotype, alleles in serotypes.items():
                if alleles:
                    f.write(f"  {serotype}:\n")
                    for allele in alleles:
                        f.write(f"    - {allele}\n")
                else:
                    f.write(f"  {serotype}: []\n")

    print(f"Written to {output_path}")
    print("\nReview the generated file, then copy to serotypes.yaml if correct.")


if __name__ == "__main__":
    main()
