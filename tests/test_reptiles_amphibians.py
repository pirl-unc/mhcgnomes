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


def test_parse_frog_gene_xela_uba():
    expected = Gene.get("Xela", "UBA")
    assert expected is not None
    eq_(parse("Xela-UBA"), expected)


def test_parse_frog_gene_xela_uca():
    expected = Gene.get("Xela", "UCA")
    assert expected is not None
    eq_(parse("Xela-UCA"), expected)


def test_parse_frog_gene_xela_daa():
    expected = Gene.get("Xela", "DAA")
    assert expected is not None
    eq_(parse("Xela-DAA"), expected)


def test_parse_frog_gene_xela_dab():
    expected = Gene.get("Xela", "DAB")
    assert expected is not None
    eq_(parse("Xela-DAB"), expected)


def test_parse_frog_gene_xela_dma():
    expected = Gene.get("Xela", "DMA")
    assert expected is not None
    eq_(parse("Xela-DMA"), expected)


def test_parse_frog_allele_xela_uba_01_01():
    expected = Allele.get("Xela", "UBA", "01", "01")
    assert expected is not None
    eq_(parse("Xela-UBA*01:01"), expected)


def test_parse_frog_allele_xela_dab_01_01():
    expected = Allele.get("Xela", "DAB", "01", "01")
    assert expected is not None
    eq_(parse("Xela-DAB*01:01"), expected)


def test_parse_pilot_frog_species_xetr():
    expected = Species.get("Xetr")
    assert expected is not None
    eq_(parse("Xetr"), expected)
    eq_(Species.get("Xenopus tropicalis"), expected)


def test_parse_frog_gene_xetr_uaa():
    expected = Gene.get("Xetr", "UAA")
    assert expected is not None
    eq_(parse("Xetr-UAA"), expected)


def test_parse_frog_gene_xetr_uba():
    expected = Gene.get("Xetr", "UBA")
    assert expected is not None
    eq_(parse("Xetr-UBA"), expected)


def test_parse_frog_gene_xetr_uca():
    expected = Gene.get("Xetr", "UCA")
    assert expected is not None
    eq_(parse("Xetr-UCA"), expected)


def test_parse_frog_gene_xetr_daa():
    expected = Gene.get("Xetr", "DAA")
    assert expected is not None
    eq_(parse("Xetr-DAA"), expected)


def test_parse_frog_gene_xetr_dab():
    expected = Gene.get("Xetr", "DAB")
    assert expected is not None
    eq_(parse("Xetr-DAB"), expected)


def test_parse_frog_gene_xetr_dma():
    expected = Gene.get("Xetr", "DMA")
    assert expected is not None
    eq_(parse("Xetr-DMA"), expected)


def test_parse_frog_gene_xetr_tap1():
    expected = Gene.get("Xetr", "TAP1")
    assert expected is not None
    eq_(parse("Xetr-TAP1"), expected)


def test_parse_frog_allele_xetr_uaa_01_01():
    expected = Allele.get("Xetr", "UAA", "01", "01")
    assert expected is not None
    eq_(parse("Xetr-UAA*01:01"), expected)


def test_parse_frog_allele_xetr_dab_01_01():
    expected = Allele.get("Xetr", "DAB", "01", "01")
    assert expected is not None
    eq_(parse("Xetr-DAB*01:01"), expected)


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
