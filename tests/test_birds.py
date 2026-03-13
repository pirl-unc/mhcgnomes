from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_


def test_parse_great_reed_warbler_species_Acar():
    expected = Species.get("Acar")
    assert expected is not None
    eq_(parse("Acar", raise_on_error=True), expected)


def test_parse_great_reed_warbler_UA_gene_and_allele():
    expected_gene = Gene.get("Acar", "UA")
    expected_allele = Allele.get("Acar", "UA", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Acar-UA", raise_on_error=True), expected_gene)
    eq_(parse("Acar-UA*01:01", raise_on_error=True), expected_allele)


def test_parse_sedge_warbler_species_Acsc():
    expected = Species.get("Acsc")
    assert expected is not None
    eq_(parse("Acsc", raise_on_error=True), expected)


def test_parse_sedge_warbler_UA_gene_and_allele():
    expected_gene = Gene.get("Acsc", "UA")
    expected_allele = Allele.get("Acsc", "UA", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Acsc-UA", raise_on_error=True), expected_gene)
    eq_(parse("Acsc-UA*01:01", raise_on_error=True), expected_allele)


def test_parse_common_yellowthroat_species_Getr():
    expected = Species.get("Getr")
    assert expected is not None
    eq_(parse("Getr", raise_on_error=True), expected)


def test_parse_common_yellowthroat_DAB_gene_and_allele():
    expected_gene = Gene.get("Getr", "DAB")
    expected_allele = Allele.get("Getr", "DAB", "01", "01")
    assert expected_gene is not None
    assert expected_allele is not None
    eq_(parse("Getr-DAB", raise_on_error=True), expected_gene)
    eq_(parse("Getr-DAB*01:01", raise_on_error=True), expected_allele)


def test_common_yellowthroat_does_not_expose_generic_MHC_gene_alias():
    species = Species.get("Getr")
    assert species is not None
    assert species.find_matching_gene_name("MHC") is None


def test_do_not_parse_ambiguous_bird_strings():
    for s in ["Gaga-BF", "Gaga-B-LB", "Gaga-YFV"]:
        assert parse(s, raise_on_error=False) is None
