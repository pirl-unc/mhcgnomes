from mhcgnomes import parse, Allele, Gene, Species, Pair
from nose.tools import eq_

def test_parse_trout_species_Onmy():
    expected = Species.get("Onmy")
    assert expected is not None
    result = parse("Onmy", raise_on_error=True)
    assert result is not None
    eq_(result, expected)

def test_parse_trout_gene_Onmy_DAB():
    result = parse("Onmy-DAB", raise_on_error=True)
    expected = Gene.get("Onmy", "DAB")
    assert expected is not None
    eq_(result, expected)

def test_parse_trout_allele_Onmy_DAB_0501():
    result = parse("Onmy-DAB*0501", raise_on_error=True)
    expected = Allele.get("Onmy", "DAB", ["05", "01"])
    assert expected is not None
    eq_(result, expected)


def test_parse_trout_allele_Onmy_DAB_050101():
    result = parse("Onmy-DAB*050101", raise_on_error=True)
    expected = Allele.get("Onmy", "DAB", ["05", "01", "01"])
    assert expected is not None
    eq_(result, expected)

def test_parse_grass_carp_B2M_1_ii_star_sep():
    expected = Allele.get("Ctid", "B2M-1", "ii")
    result = parse("Ctid-B2M-1*ii")
    eq_(result, expected)


def test_parse_grass_carp_B2M_1_ii_dash_sep():
    expected = Allele.get("Ctid", "B2M-1", "ii")
    result = parse("Ctid-B2M-1-ii")
    eq_(result, expected)

def test_parse_grass_carp_mhc1_pair_UAA_B2M_1_ii_dash_sep():
    expected = Pair(
        alpha=Gene.get("Ctid", "UAA"),
        beta=Allele.get("Ctid", "B2M-1", "ii"))
    result = parse("Ctid-UAA/B2M-1-ii")
    eq_(result, expected)

def test_parse_grass_carp_mhc1_pair_UAA_B2M_1_ii_star_sep():
    expected = Pair(
        alpha=Gene.get("Ctid", "UAA"),
        beta=Allele.get("Ctid", "B2M-1", "ii"))
    result = parse("Ctid-UAA/B2M-1*ii")
    eq_(result, expected)

