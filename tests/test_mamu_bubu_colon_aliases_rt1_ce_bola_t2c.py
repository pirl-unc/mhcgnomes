"""Tests for Mamu-A / Bubu-DQA / Bogr-DQA colon aliases, RT1-CE family, and BoLA-T2c (#339)."""

import pytest

from mhcgnomes import (
    Allele,
    AlleleWithoutGene,
    ParseError,
    Species,
    infer_mhc_class,
    parse,
    parse_gene_class,
)


@pytest.mark.parametrize(
    "colon_name,compact_name,expected",
    [
        ("Mamu-A*01:02", "Mamu-A*0102", "Mamu-A1*001:02"),
        ("Mamu-A*01:03", "Mamu-A*0103", "Mamu-A1*001:03"),
        ("Mamu-A*06:02", "Mamu-A*0602", "Mamu-A1*006:02"),
        ("Mamu-A*07:01", "Mamu-A*0701", "Mamu-A1*007:01"),
        ("Mamu-A*07:02", "Mamu-A*0702", "Mamu-A1*007:02"),
        ("Mamu-A*07:03", "Mamu-A*0703", "Mamu-A1*007:03"),
        ("Mamu-A*16:02", "Mamu-A*1602", "Mamu-A1*016:01"),
        ("Mamu-A*21:02", "Mamu-A*2102", "Mamu-A1*003:07"),
        ("Mamu-A*22:01", "Mamu-A*2201", "Mamu-A1*022:01"),
        ("Mamu-A*26:01", "Mamu-A*2601", "Mamu-A1*026:01"),
    ],
)
def test_mamu_a_colon_form_aliases_match_compact_forms(colon_name, compact_name, expected):
    # Default parsing preserves legacy spelling without opt-in aliases.
    assert parse(colon_name).to_string() == colon_name
    # Under use_allele_aliases=True, colon and compact forms deduplicate identically.
    resolved_colon = parse(colon_name, use_allele_aliases=True)
    resolved_compact = parse(compact_name, use_allele_aliases=True)
    assert resolved_colon.to_string() == expected
    assert resolved_colon == resolved_compact


@pytest.mark.parametrize(
    "colon_name,compact_name,expected",
    [
        ("Bubu-DQA*01:01", "Bubu-DQA*0101", "Bubu-DQA*001:01"),
        ("Bubu-DQA*01:10", "Bubu-DQA*0110", "Bubu-DQA*001:10"),
        ("Bubu-DQA*02:05", "Bubu-DQA*0205", "Bubu-DQA*002:05"),
        ("Bubu-DQA*20:01", "Bubu-DQA*2001", "Bubu-DQA*020:01"),
        ("Bubu-DQA*22:02", "Bubu-DQA*2202", "Bubu-DQA*022:02"),
        ("Bubu-DQA*29:01", "Bubu-DQA*2901", "Bubu-DQA*029:01"),
        ("Bogr-DQA1*01:01", "Bogr-DQA1*0101", "Bogr-DQA1*001:01"),
        ("Bogr-DQA2*01:01", "Bogr-DQA2*0101", "Bogr-DQA2*001:01"),
    ],
)
def test_bubu_and_bogr_dqa_colon_aliases_dedup_without_corrupting_two_digit_current_alleles(
    colon_name, compact_name, expected
):
    assert parse(colon_name).to_string() == colon_name
    resolved_colon = parse(colon_name, use_allele_aliases=True)
    resolved_compact = parse(compact_name, use_allele_aliases=True)
    assert resolved_colon.to_string() == expected
    assert resolved_colon == resolved_compact


def test_bubu_and_bogr_two_digit_ipd_current_alleles_are_preserved():
    # IPD-MHC 3.17.0.0 BOLA09846 (Bubu-DQA*22:02:02) and BOLA09847 (Bogr-DQA1*11:02)
    # carry 2-digit first fields and must not be blindly zero-padded.
    for name in ("Bubu-DQA*22:02:02", "Bogr-DQA1*11:02"):
        for use_aliases in (False, True):
            assert parse(name, use_allele_aliases=use_aliases).to_string() == name


@pytest.mark.parametrize("raw", ["RT1-CE*l", "RT1-CE*a", "RT1-CE*u", "Rano-CE*l"])
def test_rt1_ce_family_class_inference_without_inventing_strict_gene(raw):
    # Strict parsing does not invent a single locus for the multi-gene RT1-CE cluster.
    assert parse(raw, raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(raw)

    info = parse_gene_class(raw)
    assert info.gene_name == "CE"
    assert info.mhc_class == "I"
    assert info.chain == "alpha"
    assert info.non_mhc is False
    assert info.source == "ontology_family"
    assert infer_mhc_class(raw) == "I"


def test_bola_t2c_alias_and_known_allele_class_metadata():
    # Without allele aliases, BoLA-T2C parses as a class Ia AlleleWithoutGene.
    for spelling in ("BoLA-T2C", "BoLA-T2c"):
        parsed = parse(spelling)
        assert isinstance(parsed, AlleleWithoutGene)
        assert parsed.to_string() == "BoLA-T2c"
        assert parsed.mhc_class == "Ia"
        assert parsed.is_class1 is True
        assert parsed.is_class2 is False
        assert parse(spelling, only_class1=True) == parsed
        assert parse(spelling, only_class2=True, raise_on_error=False) is None
        info = parse_gene_class(spelling)
        assert info.mhc_class == "Ia"
        assert info.chain == "alpha"
        assert info.source == "parsed_allele"
        assert infer_mhc_class(spelling) == "Ia"

        # With use_allele_aliases=True, resolves to IPD-MHC BOLA10192 (BoLA-1*100:01).
        aliased = parse(spelling, use_allele_aliases=True)
        assert isinstance(aliased, Allele)
        assert aliased.to_string() == "BoLA-1*100:01"
        assert aliased.mhc_class == "Ia"


@pytest.mark.parametrize(
    "name,expected_class",
    [
        ("BoLA-HD6", "Ia"),
        ("BoLA-JSP.1", "Ia"),
        ("BoLA-D18.4", "Ia"),
        ("BoLA-AW10", "Ia"),
        ("BoLA-T2a", "Ia"),
        ("BoLA-T2b", "Ia"),
        ("BoLA-T2c", "Ia"),
        ("BoLA-T5", "I"),
        ("BoLA-T7", "I"),
        ("BoLA-gb1.7", None),
        ("BoLA-amani.1", None),
    ],
)
def test_bola_known_alleles_preserve_sourced_class_and_leave_unsourced_none(name, expected_class):
    parsed = parse(name)
    assert isinstance(parsed, AlleleWithoutGene)
    assert parsed.mhc_class == expected_class
    assert infer_mhc_class(name) == expected_class
    assert (parse(name, only_class1=True, raise_on_error=False) is not None) is (
        expected_class is not None
    )
    assert parse(name, only_class2=True, raise_on_error=False) is None


def test_bola_known_alleles_membership_backwards_compatible():
    cow = Species.get("BoLA")
    assert "T2c" in cow.known_alleles[None]
    assert cow.get_known_allele_mhc_class(None, "T2C") == "Ia"
    assert cow.get_known_allele_mhc_class(None, "T5") == "I"
    assert cow.get_known_allele_mhc_class(None, "gb1.7") is None
