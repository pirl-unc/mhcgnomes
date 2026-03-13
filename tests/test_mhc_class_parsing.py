import pytest

from mhcgnomes import (
    MhcClass,
    parse,
)


@pytest.mark.parametrize(
    "s",
    [
        "human class 1",
        "human class i",
        "human class I",
        "hla class 1",
        "hla class i",
        "hla class I",
        "HLA class 1",
        "HLA class i",
        "HLA class I",
    ],
)
def test_human_class_1(s):
    """Test parsing of human class I MHC strings."""
    expected_parsed_result = MhcClass.get("HLA", "I")
    expected_string_repr = "human class I"
    parsed_result = parse(s)
    assert parsed_result == expected_parsed_result, (
        f"Expected {expected_parsed_result} for parsing of '{s}' but got {parsed_result}"
    )
    normalized_str = parsed_result.to_string()
    assert normalized_str == expected_string_repr, (
        f"Expected '{expected_string_repr}' for normalized representation of '{s}' "
        f"but got '{normalized_str}'"
    )
    compact_str = parsed_result.compact_string()
    assert compact_str == expected_string_repr, (
        f"Expected '{expected_string_repr}' for compact representation of '{s}' "
        f"but got '{compact_str}'"
    )


def test_mhc_class_get_rejects_unknown_species_and_invalid_class():
    assert MhcClass.get("NOT_A_SPECIES", "I") is None
    assert MhcClass.get("HLA", "not a class") is None


def test_mhc_class_genes_returns_matching_gene_objects():
    result = MhcClass.get("HLA", "I")

    genes = result.genes()
    gene_names = {gene.name for gene in genes}

    assert "A" in gene_names
    assert "B" in gene_names
    assert "DRA" not in gene_names
    assert all(gene.species_prefix == "HLA" for gene in genes)
    assert all(gene.is_class1 for gene in genes)


def test_mhc_class_to_record_and_strings():
    result = MhcClass.get("HLA", "II")

    assert result is not None
    assert result.is_class2
    assert not result.is_class1
    assert result.to_string() == "human class II"
    assert result.to_string(include_species=False) == "class II"
    assert result.compact_string(include_species=False) == "class II"
    assert result.to_record() == {
        "species_prefix": "HLA",
        "species_name": "Homo sapiens",
        "mhc_class": "II",
    }
