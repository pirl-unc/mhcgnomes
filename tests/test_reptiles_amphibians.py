from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_


def test_parse_existing_snake_species_sica():
    expected = Species.get("Sica")
    assert expected is not None
    eq_(parse("Sica"), expected)


def test_parse_existing_snake_gene_sica_daa():
    expected = Gene.get("Sica", "DAA")
    assert expected is not None
    eq_(parse("Sica-DAA"), expected)


def test_parse_existing_snake_allele_sica_daa_01_01():
    expected = Allele.get("Sica", "DAA", "01", "01")
    assert expected is not None
    eq_(parse("Sica-DAA*01:01"), expected)


def test_parse_existing_frog_species_xela():
    expected = Species.get("Xela")
    assert expected is not None
    eq_(parse("Xela"), expected)


def test_parse_existing_frog_gene_xela_uaa():
    expected = Gene.get("Xela", "UAA")
    assert expected is not None
    eq_(parse("Xela-UAA"), expected)


def test_parse_existing_frog_allele_xela_uaa_01_01():
    expected = Allele.get("Xela", "UAA", "01", "01")
    assert expected is not None
    eq_(parse("Xela-UAA*01:01"), expected)


def test_parse_pilot_frog_species_xetr():
    expected = Species.get("Xetr")
    assert expected is not None
    eq_(parse("Xetr"), expected)
    eq_(Species.get("Xenopus tropicalis"), expected)


def test_parse_pilot_lizard_species_anca():
    expected = Species.get("Anca")
    assert expected is not None
    eq_(parse("Anca"), expected)
    eq_(Species.get("Anolis carolinensis"), expected)


def test_parse_pilot_lizard_species_ansa():
    expected = Species.get("Ansa")
    assert expected is not None
    eq_(parse("Ansa"), expected)
    eq_(Species.get("Anolis sagrei"), expected)
