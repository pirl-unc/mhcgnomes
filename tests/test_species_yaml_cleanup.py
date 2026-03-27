from pathlib import Path

import pytest
import yaml

from mhcgnomes import Gene, parse

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
