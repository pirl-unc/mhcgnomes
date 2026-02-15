from mhcgnomes import AlleleWithoutGene

from .common import eq_


def test_to_string_with_species():
    result = AlleleWithoutGene.get("BoLA", "T2C")
    assert result is not None
    eq_(result.to_string(include_species=True), "BoLA-T2C")


def test_to_string_without_species_has_no_leading_dash():
    result = AlleleWithoutGene.get("BoLA", "T2C")
    assert result is not None
    eq_(result.to_string(include_species=False), "T2C")


def test_compact_string_with_species_flag_stays_compact():
    result = AlleleWithoutGene.get("BoLA", "T2C")
    assert result is not None
    eq_(result.compact_string(include_species=True), "T2C")
