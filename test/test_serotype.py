from mhcgnomes import Serotype, parse, Species
from nose.tools import eq_

def test_HLA_A2_in_species_serotype_dictionary():
    human = Species.get("HLA")
    assert human is not None
    assert "A2" in human.serotypes


def test_parse_HLA_A2_serotype():
    result = parse("HLA-A2")
    assert result is not None
    eq_(result.name, "A2")
    eq_(result.species.prefix, "HLA")

