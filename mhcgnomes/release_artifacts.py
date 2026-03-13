from __future__ import annotations

import csv
from pathlib import Path

from .species import species_name_to_species_object

SPECIES_FIELDS = (
    "species_name",
    "common_name",
    "species_prefix",
    "historic_prefix",
    "parent_species",
    "other_prefixes",
    "other_common_names",
    "num_genes",
    "num_class2_loci",
)

GENE_FIELDS = (
    "species_name",
    "species_prefix",
    "gene_name",
    "mhc_class",
    "class2_locus",
    "class2_chain_type",
    "aliases",
    "num_known_alleles",
)


def _species_objects():
    return sorted(species_name_to_species_object.values(), key=lambda species: species.name)


def species_rows():
    rows = []
    for species in _species_objects():
        rows.append(
            {
                "species_name": species.name,
                "common_name": species.common_name,
                "species_prefix": species.species_prefix,
                "historic_prefix": species.historic_mhc_prefix,
                "parent_species": species.parent.name if species.parent else "",
                "other_prefixes": ";".join(sorted(species.other_mhc_prefixes)),
                "other_common_names": ";".join(sorted(species.other_common_names)),
                "num_genes": len(species.gene_names),
                "num_class2_loci": len(species.class2_loci),
            }
        )
    return rows


def _class2_locus_for_gene(species, gene_name):
    for locus, gene_names in species.class2_locus_to_gene_names.items():
        if gene_name in gene_names:
            return locus
    return ""


def gene_rows():
    rows = []
    for species in _species_objects():
        for gene_name in sorted(species.gene_names, key=str):
            aliases = sorted(
                alias for alias, canonical in species.gene_aliases.items() if canonical == gene_name
            )
            aliases = [alias for alias in aliases if alias != gene_name]
            known_alleles = species.known_alleles.get(gene_name, ())
            rows.append(
                {
                    "species_name": species.name,
                    "species_prefix": species.species_prefix,
                    "gene_name": gene_name,
                    "mhc_class": species.gene_name_to_mhc_class[gene_name],
                    "class2_locus": _class2_locus_for_gene(species, gene_name),
                    "class2_chain_type": species.class2_gene_name_to_chain_type.get(gene_name, ""),
                    "aliases": ";".join(aliases),
                    "num_known_alleles": len(known_alleles),
                }
            )
    return rows


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_release_artifacts(output_dir: Path) -> dict[str, Path]:
    output_dir = Path(output_dir)
    species_path = output_dir / "mhcgnomes-species-ontology.csv"
    genes_path = output_dir / "mhcgnomes-gene-ontology.csv"
    _write_csv(species_path, SPECIES_FIELDS, species_rows())
    _write_csv(genes_path, GENE_FIELDS, gene_rows())
    return {
        "species": species_path,
        "genes": genes_path,
    }
