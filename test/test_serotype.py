from mhcgnomes import Serotype, parse, Species

def test_HLA_A2_in_species_serotype_dictionary():
    human = Species.get("HLA")
    assert human is not None
    assert "A2" in human.serotypes


def test_parse_HLA_A2_serotype():
    result = parse("HLA-A2")
    assert result is not None
    assert result.name == "A2"
    assert result.species.prefix == "HLA"

