from mhcgnomes import Haplotype, parse, Species, Parser

def test_H2_a_in_species_haplotypes_dictionary():
    species = Species.get("H2")
    assert species is not None
    assert "a" in species.haplotypes

def test_get_H2a_haplotype():
    parser = Parser()
    result = parser.get_haplotype("H2", "a")
    assert result is not None
    assert result.name == "a"
    assert result.species.is_mouse


def test_parse_H2a_haplotype():
    result = parse("H2a")
    assert result is not None
    assert result.name == "a"
    assert result.species.is_mouse

def test_parse_BF19_haplotype():
    result = parse("BF19")
    print(result)
    assert result is not None
    assert type(result) == Haplotype
    assert result.name == "BF19"
    assert result.species.is_chicken