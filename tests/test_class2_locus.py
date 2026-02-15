from mhcgnomes import Class2Locus, Species, parse

from .common import eq_


def test_parse_HLA_DR():
    result = parse("HLA-DR")
    eq_(type(result), Class2Locus)
    expected = Class2Locus(species=Species.get("HLA"), name="DR")
    eq_(result, expected)


def test_class2_locus_to_string_without_species_has_no_leading_dash():
    locus = Class2Locus.get("HLA", "DR")
    assert locus is not None
    eq_(locus.to_string(include_species=False), "DR")


def test_class2_locus_compact_string_without_species_has_no_leading_dash():
    locus = Class2Locus.get("HLA", "DQ")
    assert locus is not None
    eq_(locus.compact_string(include_species=False), "DQ")
