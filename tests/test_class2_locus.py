from mhcgnomes import Class2Locus, Gene, Species, parse

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


def test_parse_hla_dr_beta_chain_prefers_curated_alias():
    eq_(parse("HLA-DR beta chain"), Gene.get("HLA", "DRB1"))


def test_parse_hla_dq_chain_prefers_curated_aliases():
    eq_(parse("HLA-DQ alpha chain"), Gene.get("HLA", "DQA1"))
    eq_(parse("HLA-DQ beta chain"), Gene.get("HLA", "DQB1"))


def test_parse_rt1_d_beta_chain_prefers_curated_alias():
    eq_(parse("RT1-D beta chain"), Gene.get("RT1", "Db1"))
