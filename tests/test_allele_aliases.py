import pytest

from mhcgnomes import parse

from .common import eq_


def test_parse_C0301_use_allele_aliases():
    allele = parse("C0301", use_allele_aliases=True)
    eq_(allele.to_string(), "HLA-C*03:04:01:01")


def test_parse_C0301_no_allele_aliases():
    allele = parse("C0301", use_allele_aliases=False)
    eq_(allele.to_string(), "HLA-C*03:01")


def test_exact_alias_can_rescue_an_otherwise_unparseable_legacy_name():
    allele = parse("Caja-PS*02:01", use_allele_aliases=True)

    assert allele.to_string() == "Caja-PS2*01"
    assert allele.raw_string == "Caja-PS*02:01"
    assert allele.is_pseudogene


def test_unparseable_legacy_alias_remains_opt_in():
    assert parse("Caja-PS*02:01", use_allele_aliases=False, raise_on_error=False) is None


@pytest.mark.parametrize(
    "near_miss",
    [
        "Caja-PS*02:02",
        "Caja-PS*03:01",
        "Caja-PS3*01",
        "MaLA-PS*02:01",
        "Capy-PS*02:01",
    ],
)
def test_caja_ps2_alias_does_not_generalize_to_near_misses_or_other_species(near_miss):
    assert parse(near_miss, use_allele_aliases=True, raise_on_error=False) is None
