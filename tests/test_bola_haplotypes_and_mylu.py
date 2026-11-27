"""Tests for BoLA class I haplotypes and Myotis lucifugus class I alleles (#325)."""

import pytest

from mhcgnomes import Allele, Gene, Haplotype, Serotype, parse


@pytest.mark.parametrize(
    "raw, expected_name, expected_alleles",
    [
        ("BoLA-A10", "A10", ("BoLA-2*012:01", "BoLA-3*002:01")),
        ("BoLA-A12", "A12", ("BoLA-1*019:01", "BoLA-2*008:01")),
        (
            "BoLA-A14",
            "A14",
            ("BoLA-1*023:01", "BoLA-2*025:01", "BoLA-4*024:01", "BoLA-6*040:01"),
        ),
        ("BoLA-A15", "A15", ("BoLA-1*009:01", "BoLA-2*025:01", "BoLA-4*024:01")),
        ("BoLA-A19", "A19", ("BoLA-2*016:01", "BoLA-6*014:02")),
        ("BoLA-A20", "A20", ("BoLA-2*026:01", "BoLA-3*027:01")),
    ],
)
def test_bola_class1_haplotypes(raw, expected_name, expected_alleles):
    result = parse(raw)
    assert type(result) is Haplotype
    assert result.species.prefix == "BoLA"
    assert result.name == expected_name
    assert result.to_string() == raw
    assert tuple(a.to_string() for a in result.alleles) == expected_alleles
    assert all(a.is_class1 for a in result.alleles)
    assert result.species_source == "explicit"

    # Explicit haplotype / class I qualifiers also resolve cleanly
    with_word = parse(f"{raw} haplotype")
    assert with_word == result
    with_class = parse(f"{raw} class I")
    assert type(with_class) is Haplotype
    assert with_class.class_restriction == "I"
    assert tuple(a.to_string() for a in with_class.alleles) == expected_alleles


def test_existing_bola_serotypes_preserved():
    a18 = parse("BoLA-A18")
    assert type(a18) is Serotype
    assert a18.name == "A18"
    assert [a.to_string() for a in a18.alleles] == ["BoLA-6*013:01", "BoLA-6*013:02"]

    a11 = parse("BoLA-A11")
    assert type(a11) is Serotype
    assert a11.name == "A11"


@pytest.mark.parametrize(
    "raw, expected_fields",
    [
        ("Mylu-B*67:01", ("67", "01")),
        ("MyotLuci-B*67:01", ("67", "01")),
        ("MyotisLucifugus-B*67:01", ("67", "01")),
        ("Mylu-B*57:01", ("57", "01")),
    ],
)
def test_myotis_lucifugus_class1_b_alleles(raw, expected_fields):
    result = parse(raw, only_class1=True, require_explicit_species=True)
    assert type(result) is Allele
    assert result.species.name == "Myotis lucifugus"
    assert result.gene == Gene.get("Myotis lucifugus", "B")
    assert result.gene_name == "B"
    assert result.allele_fields == expected_fields
    assert result.mhc_class == "Ia"
    assert result.is_class1 is True
    assert result.species_source == "explicit"
