#!/usr/bin/env python3
"""
Comprehensive audit of species.yaml and gene_aliases.yaml for:
1. Duplicate gene detection (child redefines parent's gene)
2. Gene duplication across siblings (candidates for promotion)
3. Suspicious gene names
4. Taxonomy sanity checks
5. Orphaned gene aliases
6. Class II loci chain completeness
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "mhcgnomes" / "data"

# ─── helpers ────────────────────────────────────────────────────────────

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def extract_genes(gene_dict):
    """
    Walk a genes: dict and return:
      - flat set of gene names
      - dict mapping locus_family -> set of gene names
      - dict mapping gene_name -> mhc_class
    """
    genes = set()
    locus_map = {}  # locus_family -> {gene, ...}
    gene_class = {}  # gene -> class label (Ia, Ib, IIa, IIb, ...)

    if not gene_dict:
        return genes, locus_map, gene_class

    for mhc_class, value in gene_dict.items():
        if value is None:
            continue
        if isinstance(value, list):
            for g in value:
                genes.add(str(g))
                gene_class[str(g)] = mhc_class
        elif isinstance(value, dict):
            for locus_family, locus_genes in value.items():
                if locus_genes is None or (isinstance(locus_genes, dict) and not locus_genes):
                    continue
                if isinstance(locus_genes, list):
                    if locus_family not in locus_map:
                        locus_map[locus_family] = set()
                    for g in locus_genes:
                        genes.add(str(g))
                        locus_map[locus_family].add(str(g))
                        gene_class[str(g)] = mhc_class
                elif isinstance(locus_genes, dict):
                    # nested further
                    pass
    return genes, locus_map, gene_class


def parse_species(data):
    """
    Parse the flat species.yaml dict into structured entries.
    Returns dict: species_key -> {parent, prefix, genes_raw, ...}
    """
    entries = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        entry = {
            "key": key,
            "parent": value.get("parent"),
            "prefix": value.get("prefix"),
            "other_prefixes": value.get("other prefixes", []),
            "context_only_prefixes": value.get("context only prefixes", []),
            "name": value.get("name"),
            "genes_raw": value.get("genes", {}),
        }
        genes, locus_map, gene_class = extract_genes(entry["genes_raw"])
        entry["own_genes"] = genes
        entry["own_locus_map"] = locus_map
        entry["gene_class"] = gene_class
        entries[key] = entry
    return entries


def resolve_parent(entries, key):
    """Return parent key (default root)."""
    entry = entries[key]
    if entry["parent"]:
        return entry["parent"]
    if key != "Gnathostomata sp.":
        return "Gnathostomata sp."
    return None


def get_inherited_genes(entries, key, _seen=None):
    """Recursively collect genes inherited from the parent chain."""
    if _seen is None:
        _seen = set()
    if key in _seen:
        return set()
    _seen.add(key)

    parent_key = resolve_parent(entries, key)
    if parent_key is None:
        return set()
    if parent_key not in entries:
        return set()

    parent_genes = entries[parent_key]["own_genes"].copy()
    parent_genes |= get_inherited_genes(entries, parent_key, _seen)
    return parent_genes


def get_inherited_locus_map(entries, key, _seen=None):
    """Recursively collect locus maps inherited from the parent chain."""
    if _seen is None:
        _seen = set()
    if key in _seen:
        return {}
    _seen.add(key)

    parent_key = resolve_parent(entries, key)
    if parent_key is None:
        return {}
    if parent_key not in entries:
        return {}

    result = {}
    # First get grandparent's loci
    grandparent_loci = get_inherited_locus_map(entries, parent_key, _seen)
    for locus, genes in grandparent_loci.items():
        result.setdefault(locus, set()).update(genes)
    # Then overlay parent's own loci
    for locus, genes in entries[parent_key]["own_locus_map"].items():
        result.setdefault(locus, set()).update(genes)
    return result


# ─── main ───────────────────────────────────────────────────────────────

def main():
    species_data = load_yaml(DATA_DIR / "species.yaml")
    aliases_data = load_yaml(DATA_DIR / "gene_aliases.yaml")

    entries = parse_species(species_data)
    findings = []

    def report(category, msg):
        findings.append((category, msg))

    # ── 1. Duplicate gene detection ──────────────────────────────────
    print("=" * 80)
    print("1. DUPLICATE GENE DETECTION (child redefines parent gene)")
    print("=" * 80)
    count = 0
    for key, entry in entries.items():
        inherited = get_inherited_genes(entries, key)
        overlap = entry["own_genes"] & inherited
        if overlap:
            for g in sorted(overlap):
                report("dup_inherit", f"  {key}: gene '{g}' is explicitly defined but already inherited from parent chain")
                count += 1
    for _, msg in sorted(findings):
        print(msg)
    if count == 0:
        print("  (none found)")
    print(f"\n  Total: {count} redundant gene definitions\n")

    # ── 2. Gene duplication across siblings ──────────────────────────
    findings2 = []
    print("=" * 80)
    print("2. GENE DUPLICATION ACROSS SIBLINGS (candidates for parent promotion)")
    print("=" * 80)

    # Build parent -> children mapping
    parent_children = defaultdict(list)
    for key, entry in entries.items():
        parent_key = resolve_parent(entries, key)
        if parent_key:
            parent_children[parent_key].append(key)

    count = 0
    for parent_key, children in sorted(parent_children.items()):
        if len(children) < 2:
            continue
        parent_genes = entries[parent_key]["own_genes"] if parent_key in entries else set()
        # Count gene occurrences across children
        gene_counts = defaultdict(list)
        for child_key in children:
            for g in entries[child_key]["own_genes"]:
                if g not in parent_genes:
                    gene_counts[g].append(child_key)
        for g, child_keys in sorted(gene_counts.items()):
            if len(child_keys) >= 2:
                findings2.append(
                    f"  Parent '{parent_key}': gene '{g}' defined on {len(child_keys)}/{len(children)} "
                    f"children: {', '.join(child_keys)}"
                )
                count += 1
    for msg in findings2:
        print(msg)
    if count == 0:
        print("  (none found)")
    print(f"\n  Total: {count} candidate genes for promotion\n")

    # ── 3. Suspicious gene names ─────────────────────────────────────
    print("=" * 80)
    print("3. SUSPICIOUS GENE NAMES")
    print("=" * 80)

    # 3a. Single lowercase letters
    print("\n  3a. Single lowercase letters:")
    count3a = 0
    for key, entry in sorted(entries.items()):
        for g in sorted(entry["own_genes"]):
            if re.match(r'^[a-z]$', g):
                print(f"    {key}: gene '{g}' — single lowercase letter")
                count3a += 1
    if count3a == 0:
        print("    (none found)")

    # 3b. Gene names that look like alleles (letters followed by digits)
    print(f"\n  3b. Gene names that look like allele designations:")
    count3b = 0
    # Patterns: UHA103, B01, B5, DRB01, etc. — but NOT standard patterns like DRB1, A1
    # Flag things that look like they have zero-padded numbers, or long digit suffixes
    allele_like = re.compile(r'^[A-Za-z]+0\d+$')  # zero-padded: B01, DRB01, etc.
    for key, entry in sorted(entries.items()):
        for g in sorted(entry["own_genes"]):
            if allele_like.match(g):
                print(f"    {key}: gene '{g}' — looks like zero-padded allele designation")
                count3b += 1
    # Also check for things like UHA103
    big_digits = re.compile(r'^[A-Za-z]+\d{3,}$')
    for key, entry in sorted(entries.items()):
        for g in sorted(entry["own_genes"]):
            if big_digits.match(g) and not allele_like.match(g):
                print(f"    {key}: gene '{g}' — has 3+ digit suffix, may be allele/clone ID")
                count3b += 1
    if count3b == 0:
        print("    (none found)")

    # 3c. Unusual characters
    print(f"\n  3c. Gene names with unusual characters:")
    count3c = 0
    normal = re.compile(r'^[A-Za-z0-9_\-\.]+$')
    for key, entry in sorted(entries.items()):
        for g in sorted(entry["own_genes"]):
            if not normal.match(g):
                print(f"    {key}: gene '{g}' — contains unusual characters")
                count3c += 1
    if count3c == 0:
        print("    (none found)")

    # 3d. Very long gene names (>10 chars)
    print(f"\n  3d. Very long gene names (>10 chars):")
    count3d = 0
    for key, entry in sorted(entries.items()):
        for g in sorted(entry["own_genes"]):
            if len(g) > 10:
                print(f"    {key}: gene '{g}' (len={len(g)})")
                count3d += 1
    if count3d == 0:
        print("    (none found)")

    print()

    # ── 4. Taxonomy sanity checks ────────────────────────────────────
    print("=" * 80)
    print("4. TAXONOMY SANITY CHECKS")
    print("=" * 80)

    # Known taxonomic groups for biological-sense checking
    fish_groups = {"Actinopterygii sp.", "Salmonidae sp.", "Cyprinidae sp.",
                   "Xiphophorus sp.", "Coregonus sp.", "Tropheus sp."}
    bird_groups = {"Aves sp.", "Galliformes sp.", "Accipitriformes sp.",
                   "Gruiformes sp.", "Strigidae sp.", "Ardeidae sp.",
                   "Falco sp.", "Turdus sp."}
    reptile_groups = {"Reptilia sp.", "Testudines sp.", "Crocodylia sp."}
    mammal_groups = {"Marsupialia sp.", "Notamacropus sp.", "Rodentia sp.",
                     "Ctenomys sp.", "Octodon sp.", "Chiroptera sp.",
                     "Primata sp.", "Macaca sp.", "Pan sp.", "Gorilla sp.",
                     "Pongo sp.", "Aotus sp.", "Callithrix sp.",
                     "Mus sp.", "Rattus sp.",
                     "Canis sp.", "Felis sp.",
                     "Bos sp.", "Ovis sp.", "Capra sp.", "Equus sp.",
                     "Sus sp.", "Cetacea sp.", "Oryctolagus sp.", "Falco sp."}
    amphibian_groups = {"Amphibia sp."}
    shark_groups = {"Chondrichthyes sp."}

    # 4a. Nodes with only 1 child
    print("\n  4a. Intermediate 'sp.' nodes with only 1 child:")
    count4a = 0
    for parent_key, children in sorted(parent_children.items()):
        if "sp." in parent_key and len(children) == 1:
            print(f"    '{parent_key}' has only 1 child: '{children[0]}'")
            count4a += 1
    if count4a == 0:
        print("    (none found)")

    # 4b. Identical prefix values
    print(f"\n  4b. Duplicate prefix values:")
    prefix_owners = defaultdict(list)
    for key, entry in entries.items():
        if entry["prefix"]:
            prefix_owners[entry["prefix"]].append(key)
        for p in (entry.get("other_prefixes") or []):
            prefix_owners[p].append(key)
    count4b = 0
    for prefix, owners in sorted(prefix_owners.items()):
        if len(owners) > 1:
            print(f"    Prefix '{prefix}' used by: {', '.join(owners)}")
            count4b += 1
    if count4b == 0:
        print("    (none found)")

    # 4c. Case-insensitive prefix collisions
    print(f"\n  4c. Case-insensitive prefix collisions:")
    ci_prefix = defaultdict(list)
    for key, entry in entries.items():
        if entry["prefix"]:
            ci_prefix[entry["prefix"].lower()].append((entry["prefix"], key))
        for p in (entry.get("other_prefixes") or []):
            ci_prefix[p.lower()].append((p, key))
    count4c = 0
    for lower_prefix, owners in sorted(ci_prefix.items()):
        # Check if different species share the same case-insensitive prefix
        species_set = set(o[1] for o in owners)
        if len(species_set) > 1:
            details = [f"{p} ({s})" for p, s in owners]
            print(f"    '{lower_prefix}': {', '.join(details)}")
            count4c += 1
    if count4c == 0:
        print("    (none found)")

    # 4d. Species without a parent that look like they should have one
    print(f"\n  4d. Species parented directly to root (Gnathostomata sp.) — may need better parent:")
    count4d = 0
    for key, entry in sorted(entries.items()):
        if key == "Gnathostomata sp.":
            continue
        parent = resolve_parent(entries, key)
        if parent == "Gnathostomata sp.":
            print(f"    '{key}' (prefix: {entry['prefix']}) — no explicit parent, defaults to root")
            count4d += 1
    if count4d == 0:
        print("    (none found)")

    # 4e. Missing parents (parent references non-existent node)
    print(f"\n  4e. Missing parent nodes:")
    count4e = 0
    for key, entry in sorted(entries.items()):
        if entry["parent"] and entry["parent"] not in entries:
            print(f"    '{key}' references parent '{entry['parent']}' which does not exist")
            count4e += 1
    if count4e == 0:
        print("    (none found)")

    # 4f. Duplicate NC8 in Bos sp.
    print(f"\n  4f. Duplicate gene names within a single species:")
    count4f = 0
    for key, value in species_data.items():
        if not isinstance(value, dict) or "genes" not in value:
            continue
        # Flatten all gene names and look for duplicates
        all_genes_list = []
        def walk_genes(obj):
            if isinstance(obj, list):
                for item in obj:
                    all_genes_list.append(str(item))
            elif isinstance(obj, dict):
                for v in obj.values():
                    walk_genes(v)
        walk_genes(value["genes"])
        seen = {}
        for g in all_genes_list:
            if g in seen:
                print(f"    '{key}': gene '{g}' appears multiple times")
                count4f += 1
            seen[g] = True
    if count4f == 0:
        print("    (none found)")

    print()

    # ── 5. Orphaned gene aliases ─────────────────────────────────────
    print("=" * 80)
    print("5. ORPHANED GENE ALIASES")
    print("=" * 80)

    # Map prefix -> species key
    prefix_to_species = {}
    for key, entry in entries.items():
        if entry["prefix"]:
            prefix_to_species[entry["prefix"]] = key
        for p in (entry.get("other_prefixes") or []):
            prefix_to_species[p] = key

    count5 = 0
    for alias_prefix, alias_map in (aliases_data or {}).items():
        if not isinstance(alias_map, dict):
            continue
        # Find which species this alias block corresponds to
        species_key = prefix_to_species.get(alias_prefix)
        if species_key is None:
            # Try case-insensitive
            for p, s in prefix_to_species.items():
                if p.lower() == alias_prefix.lower():
                    species_key = s
                    break

        if species_key is None:
            # Check if it's a "Gnathostomata" level
            if alias_prefix == "Gnathostomata sp.":
                species_key = "Gnathostomata sp."
            else:
                # Not a recognized species prefix in species.yaml
                # This itself may be worth reporting
                pass

        if species_key and species_key in entries:
            # Get all genes available (own + inherited)
            all_available = entries[species_key]["own_genes"] | get_inherited_genes(entries, species_key)
            for alias_name, target_gene in alias_map.items():
                if isinstance(target_gene, str) and target_gene not in all_available:
                    print(f"  Alias prefix '{alias_prefix}': alias '{alias_name}' -> '{target_gene}' "
                          f"but '{target_gene}' is not a known gene on '{species_key}'")
                    count5 += 1
        elif species_key is None:
            print(f"  Alias block prefix '{alias_prefix}' does not match any species prefix in species.yaml")
            count5 += 1

    if count5 == 0:
        print("  (none found)")
    print(f"\n  Total: {count5} issues\n")

    # ── 6. Class II loci chain completeness ──────────────────────────
    print("=" * 80)
    print("6. CLASS II LOCI CHAIN COMPLETENESS")
    print("=" * 80)
    print("  Checking if each class II locus has both alpha and beta chain genes.\n")

    # Class II locus naming conventions:
    # Standard: DRA/DRB, DQA/DQB, DPA/DPB, DMA/DMB, DOA/DOB, DNA/DNB, DYA/DYB, DZA/DZB
    # Mouse: AA/AB, EA/EB, PA/PB, OA/OB
    # Rat: Da/Db, Ba/Bb, Ha/Hb, DOa/DOb
    # Chicken: BLA/BLB, DMA/DMB
    # Non-mammalian: DAA/DAB, DBA/DBB, DCA/DCB, DDA/DDB, DXA/DXB

    count6 = 0
    for key, entry in sorted(entries.items()):
        locus_map = entry.get("own_locus_map", {})
        # Also get inherited locus map
        inherited_locus = get_inherited_locus_map(entries, key)

        # Merge own + inherited
        all_loci = {}
        for locus, genes in inherited_locus.items():
            all_loci.setdefault(locus, set()).update(genes)
        for locus, genes in locus_map.items():
            all_loci.setdefault(locus, set()).update(genes)

        for locus, genes in sorted(locus_map.items()):
            # Skip DM/DO — those are accessory
            # Focus on classical class II loci under IIa
            if not genes:
                continue

            # Determine if this locus is IIa (classical)
            gene_classes = set()
            for g in genes:
                if g in entry.get("gene_class", {}):
                    gene_classes.add(entry["gene_class"][g])

            # Only check loci that have IIa genes
            if "IIa" not in gene_classes and "IIb" not in gene_classes:
                continue

            # Check for alpha and beta chains
            has_alpha = False
            has_beta = False

            all_locus_genes = all_loci.get(locus, genes)

            for g in all_locus_genes:
                g_upper = g.upper()
                # Standard naming: ends with A/A1/A2 = alpha, B/B1/B2 = beta
                # Mouse: AA = alpha, AB = beta, EA = alpha, EB = beta
                if locus in ("A", "E", "P"):
                    # Mouse convention: second letter A=alpha, B=beta
                    if g.endswith("A") or g.endswith("a"):
                        has_alpha = True
                    elif g.endswith("B") or g.endswith("b") or re.search(r'B\d', g) or re.search(r'b\d', g):
                        has_beta = True
                elif locus in ("D", "B", "H"):
                    # Rat convention: Da/Db, Ba/Bb, Ha/Hb
                    if g.endswith("a"):
                        has_alpha = True
                    elif g.endswith("b") or re.search(r'b\d', g):
                        has_beta = True
                elif locus == "BL":
                    # Chicken: BLA=alpha, BLB=beta
                    if "BLA" in g_upper:
                        has_alpha = True
                    elif "BLB" in g_upper or "B12c" in g or re.match(r'B-LB', g):
                        has_beta = True
                elif locus == "HB":
                    # Special pike locus
                    continue
                else:
                    # Standard: DRA=alpha, DRB=beta, DAA=alpha, DAB=beta, etc.
                    # Alpha genes typically contain 'A' at the end or before digits
                    # Beta genes typically contain 'B' at the end or before digits
                    alpha_pattern = re.compile(
                        r'(?:^' + re.escape(locus) + r'A)|'  # e.g., DRA, DQA, DAA
                        r'(?:A\d*$)|'  # ends with A or A+digits
                        r'(?:A-\d+$)|'  # DAA-1 style
                        r'(?:^DRA)',  # DRA specifically
                        re.IGNORECASE
                    )
                    beta_pattern = re.compile(
                        r'(?:^' + re.escape(locus) + r'B)|'  # e.g., DRB, DQB, DAB
                        r'(?:B\d*$)|'  # ends with B or B+digits
                        r'(?:^DRB)',  # DRB specifically
                        re.IGNORECASE
                    )

                    # More specific: check the gene name structure
                    g_stripped = g.upper()
                    if any(g_stripped.startswith(pre + "A") for pre in
                           [locus.upper(), "D" + locus.upper()[1:] if len(locus) > 1 else ""]):
                        has_alpha = True
                    elif any(g_stripped.startswith(pre + "B") for pre in
                             [locus.upper(), "D" + locus.upper()[1:] if len(locus) > 1 else ""]):
                        has_beta = True
                    # For loci like DR: DRA=alpha, DRB*=beta
                    elif g_stripped.startswith("DR"):
                        if "DRA" in g_stripped:
                            has_alpha = True
                        elif "DRB" in g_stripped:
                            has_beta = True
                    elif g_stripped.startswith("DQ"):
                        if "DQA" in g_stripped:
                            has_alpha = True
                        elif "DQB" in g_stripped:
                            has_beta = True
                    elif g_stripped.startswith("DP"):
                        if "DPA" in g_stripped:
                            has_alpha = True
                        elif "DPB" in g_stripped:
                            has_beta = True
                    elif g_stripped.startswith("DA"):
                        if re.match(r'DAA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DAB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DB"):
                        if re.match(r'DBA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DBB', g_stripped) or re.match(r'DB\d', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DC"):
                        if re.match(r'DCA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DCB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DD"):
                        if re.match(r'DDA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DDB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DX"):
                        if re.match(r'DXA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DXB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DZ"):
                        if re.match(r'DZA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DZB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DI"):
                        if re.match(r'DIA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DIB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DY"):
                        if re.match(r'DYA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DYB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DN"):
                        if re.match(r'DNA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DNB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DO"):
                        if re.match(r'DOA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DOB', g_stripped):
                            has_beta = True
                    elif g_stripped.startswith("DM"):
                        if re.match(r'DMA', g_stripped):
                            has_alpha = True
                        elif re.match(r'DMB', g_stripped):
                            has_beta = True

            # Only report if the locus is defined on THIS species (own_locus_map)
            if locus in entry["own_locus_map"]:
                if not has_alpha and has_beta:
                    gene_list = sorted(all_locus_genes)
                    print(f"  {key}: locus '{locus}' has beta but NO alpha chain genes: {gene_list}")
                    count6 += 1
                elif has_alpha and not has_beta:
                    gene_list = sorted(all_locus_genes)
                    print(f"  {key}: locus '{locus}' has alpha but NO beta chain genes: {gene_list}")
                    count6 += 1

    if count6 == 0:
        print("  (none found)")
    print(f"\n  Total: {count6} incomplete class II loci\n")

    # ── Summary ──────────────────────────────────────────────────────
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total species entries: {len(entries)}")
    print(f"  Total 'sp.' intermediate nodes: {sum(1 for k in entries if 'sp.' in k)}")
    total_genes = sum(len(e['own_genes']) for e in entries.values())
    print(f"  Total gene definitions (across all species): {total_genes}")


if __name__ == "__main__":
    main()
