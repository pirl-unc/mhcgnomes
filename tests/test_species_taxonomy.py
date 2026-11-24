"""Tests for verified NCBI Taxonomy IDs and vertebrate clades on Species (#276)."""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.data import species as raw_species_dict
from mhcgnomes.data import species_taxonomy as raw_species_taxonomy_dict
from mhcgnomes.species import VERTEBRATE_CLADES, latin_name_to_species_object

from .common import eq_


def test_every_species_has_a_taxonomy_entry_and_no_orphans_exist():
    species_keys = set(raw_species_dict)
    taxonomy_keys = set(raw_species_taxonomy_dict)
    assert taxonomy_keys == species_keys, (
        f"missing={sorted(species_keys - taxonomy_keys)}, "
        f"extra={sorted(taxonomy_keys - species_keys)}"
    )


def test_all_loaded_species_have_valid_taxid_and_clade():
    multi_clade_nodes = {"Gnathostomata sp.", "Primata sp.", "Rodentia sp."}
    paraphyletic_nodes = {"NHP", "Reptilia sp."}

    for sp in latin_name_to_species_object.values():
        if sp.name in paraphyletic_nodes:
            assert sp.ncbi_taxid is None, f"{sp.name} should not claim a single NCBI taxid"
        else:
            assert isinstance(sp.ncbi_taxid, int) and not isinstance(sp.ncbi_taxid, bool)
            assert sp.ncbi_taxid > 0, f"{sp.name} has invalid ncbi_taxid={sp.ncbi_taxid!r}"

        if sp.name in multi_clade_nodes:
            assert sp.clade is None, f"Multi-clade node {sp.name} should have clade=None"
        else:
            assert sp.clade in VERTEBRATE_CLADES, f"{sp.name} has unexpected clade={sp.clade!r}"


@pytest.mark.parametrize(
    "query,expected_taxid,expected_clade",
    [
        ("Homo sapiens", 9606, "human"),
        ("Macaca mulatta", 9544, "nhp"),
        ("Pan troglodytes", 9598, "nhp"),
        ("NHP", None, "nhp"),
        ("Primata sp.", 9443, None),
        ("Mus musculus", 10090, "murine"),
        ("Rattus norvegicus", 10116, "murine"),
        ("Bos taurus", 9913, "ungulate"),
        ("Bos sp.", 9903, "ungulate"),
        ("Sus scrofa", 9823, "ungulate"),
        ("Equus caballus", 9796, "ungulate"),
        ("Equus burchelli", 89252, "ungulate"),
        ("Ovis aries", 9940, "ungulate"),
        ("Capra hircus", 9925, "ungulate"),
        ("Tursiops truncatus", 9739, "cetacean"),
        ("Cetacea sp.", 9721, "cetacean"),
        ("Canis lupus familiaris", 9615, "carnivore"),
        ("Canis lupus", 9612, "carnivore"),
        ("Canis sp.", 9611, "carnivore"),
        ("Felis catus", 9685, "carnivore"),
        ("Felis sp.", 9682, "carnivore"),
        ("Pteropus alecto", 9402, "bat"),
        ("Monodelphis domestica", 13616, "marsupial"),
        ("Sarcophilus harrisii", 9305, "marsupial"),
        ("Ornithorhynchus anatinus", 9258, "monotreme"),
        ("Tachyglossus aculeatus", 9261, "monotreme"),
        ("Oryctolagus cuniculus", 9986, "other_mammal"),
        ("Cavia porcellus", 10141, "other_mammal"),
        ("Gallus gallus", 9031, "bird"),
        ("Anas platyrhynchos", 8839, "bird"),
        ("Crocodylus porosus", 8502, "reptile"),
        ("Chelonia mydas", 8469, "reptile"),
        ("Reptilia sp.", None, "reptile"),
        ("Xenopus laevis", 8355, "amphibian"),
        ("Lithobates catesbeianus", 8400, "amphibian"),
        # Regression checks for mhcseqs#127 (newts & paddlefish)
        ("Lissotriton vulgaris", 8324, "amphibian"),
        ("Triturus cristatus", 8323, "amphibian"),
        ("Ichthyosaura alpestris", 54263, "amphibian"),
        ("Polyodon spathula", 7913, "bony_fish"),
        ("Danio rerio", 7955, "bony_fish"),
        ("Salmo salar", 8030, "bony_fish"),
        ("Ginglymostoma cirratum", 7801, "shark_ray"),
        ("Squalus acanthias", 7797, "shark_ray"),
        ("Gnathostomata sp.", 7776, None),
    ],
)
def test_representative_species_taxid_and_clade(query, expected_taxid, expected_clade):
    sp = Species.get(query)
    assert sp is not None, f"Species.get({query!r}) returned None"
    eq_(sp.ncbi_taxid, expected_taxid)
    eq_(sp.clade, expected_clade)


def test_get_by_ncbi_taxid():
    eq_(Species.get_by_ncbi_taxid(9606), Species.get("Homo sapiens"))
    eq_(Species.get_by_ncbi_taxid("9606"), Species.get("Homo sapiens"))
    eq_(Species.get_by_ncbi_taxid(" 9615 "), Species.get("Canis lupus familiaris"))
    eq_(Species.get_by_ncbi_taxid(9612), Species.get("Canis lupus"))
    eq_(Species.get_by_ncbi_taxid(7913), Species.get("Polyodon spathula"))
    # Synonym pair sharing NCBI 10100 resolves to canonical Mus macedonicus
    eq_(Species.get_by_ncbi_taxid(10100), Species.get("Mus macedonicus"))

    for bad in (None, True, False, 0, -1, "", "abc", 999999999, 9606.0):
        assert Species.get_by_ncbi_taxid(bad) is None


def test_parsed_result_exposes_species_taxid_and_clade():
    allele = parse("HLA-A*02:01")
    eq_(allele.species.ncbi_taxid, 9606)
    eq_(allele.species.clade, "human")

    cat = parse("FLA-E*003:01")
    eq_(cat.species.ncbi_taxid, 9682)
    eq_(cat.species.clade, "carnivore")
