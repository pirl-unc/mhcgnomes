import pytest

from mhcgnomes import Allele, Species, Supertype, parse


def test_supertype_strings_and_record_include_representative_allele():
    result = parse("A2 supertype")

    assert result.to_string() == "HLA A02 supertype"
    assert result.compact_string() == "A02"
    assert result.compact_string(include_species=True) == "HLA-A02"
    assert result.to_record() == {
        "species_prefix": "HLA",
        "species_name": "Homo sapiens",
        "supertype": "A02",
        "supertype_string": "HLA A02 supertype",
        "representative_allele": "HLA-A*02:01",
    }


def test_supertype_inherited_multiple_allele_helpers():
    allele = Allele.get("HLA", "A", "24", "02", annotation="L")
    result = Supertype(
        species=Species.get("HLA"),
        name="A24",
        alleles=[allele],
        representative=allele,
    )

    assert result.num_alleles == 1
    assert result.gene_name == "A"
    assert result.collapse_if_possible() == allele
    assert result.has_allele
    assert result.is_class1
    assert not result.is_class2
    assert result.annotation_low_expression


def test_supertype_restrict_allele_fields_returns_updated_copy():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01")
    result = Supertype(
        species=Species.get("HLA"),
        name="A02",
        alleles=[allele],
        representative=allele,
    )

    restricted = result.restrict_allele_fields(2)

    assert restricted is not result
    assert restricted.alleles[0].allele_fields == ("02", "01")
    assert restricted.representative == allele


def test_supertype_rejects_mixed_species_alleles():
    with pytest.raises(ValueError):
        Supertype(
            species=Species.get("HLA"),
            name="bad",
            alleles=[
                Allele.get("HLA", "A", "02", "01"),
                Allele.get("BoLA", "NC11", "001", "01"),
            ],
        )
