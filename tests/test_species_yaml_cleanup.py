from pathlib import Path

import pytest
import yaml

from mhcgnomes import Gene, Species, parse

from .common import eq_


def load_raw_species_yaml():
    species_path = Path(__file__).parent.parent / "mhcgnomes" / "data" / "species.yaml"
    with species_path.open() as fd:
        return yaml.safe_load(fd)


TARGETED_REDUNDANT_DIRECT_GENE_BLOCKS_REMOVED = [
    "Balaenoptera musculus",
    "Balaenoptera acutorostrata",
    "Balaenoptera edeni",
    "Cephalorhynchus hectori",
    "Delphinus delphis",
    "Eubalaena australis",
    "Globicephala melas",
    "Grampus griseus",
    "Kogia breviceps",
    "Lagenorhynchus obscurus",
    "Mesoplodon densirostris",
    "Mesoplodon europaeus",
    "Mesoplodon grayi",
    "Megaptera novaeangliae",
    "Steno bredanensis",
    "Stenella coeruleoalba",
    "Tursiops truncatus",
    "Ziphius cavirostris",
    "Strigidae sp.",
    "Tyto alba",
    "Macaca silenus",
    "Macaca thibetana",
]


def test_targeted_subset_only_direct_gene_blocks_removed_from_raw_yaml():
    species_data = load_raw_species_yaml()
    for latin_name in TARGETED_REDUNDANT_DIRECT_GENE_BLOCKS_REMOVED:
        assert "genes" not in species_data[latin_name], latin_name


def test_goat_inherits_helper_genes_from_root():
    """Capra sp. no longer declares TAP1/TAP2/TAPBP/B2M directly;
    they are inherited from the Gnathostomata sp. root."""
    species_data = load_raw_species_yaml()
    goat_genes = species_data["Capra sp."]["genes"]
    assert "other" not in goat_genes
    # Verify they're still on the root
    root_genes = species_data["Gnathostomata sp."]["genes"]
    assert "other" in root_genes
    assert {"TAP1", "TAP2", "TAPBP", "B2M"}.issubset(set(root_genes["other"]))


def test_human_and_rabbit_do_not_use_generic_top_level_class_ii_bucket():
    species_data = load_raw_species_yaml()
    assert "II" not in species_data["Homo sapiens"]["genes"]
    assert "II" not in species_data["Oryctolagus sp."]["genes"]


def test_rat_a3_only_appears_in_class_ia_in_raw_yaml():
    species_data = load_raw_species_yaml()
    rat_genes = species_data["Rattus sp."]["genes"]
    assert "A3" in rat_genes["Ia"]
    assert "A3" not in rat_genes["I"]


@pytest.mark.parametrize(
    "species_prefix,gene_name",
    [
        ("Bamu", "DQA"),
        ("Baac", "S"),
        ("Tyal", "DAB1"),
        ("Stoc", "DAB2"),
        ("Masi", "DRB4"),
        ("Math", "DPB1"),
    ],
)
def test_targeted_cleanup_species_still_inherit_representative_genes(species_prefix, gene_name):
    gene = Gene.get(species_prefix, gene_name)
    assert gene is not None, f"Gene.get({species_prefix!r}, {gene_name!r}) returned None"
    eq_(parse(f"{species_prefix}-{gene_name}", raise_on_error=True), gene)


@pytest.mark.parametrize(
    "species_prefix,gene_name,expected_class",
    [
        ("CLA", "TAP1", "other"),
        ("CLA", "B2M", "other"),
        ("HLA", "DRB6", "IIa"),
        ("RLA", "DPA", "IIa"),
        ("RT1", "A3", "Ia"),
    ],
)
def test_runtime_gene_classes_match_cleaned_ontology(species_prefix, gene_name, expected_class):
    species = Species.get(species_prefix)
    eq_(species.get_mhc_class_of_gene(gene_name), expected_class)
