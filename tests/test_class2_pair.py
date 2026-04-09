import pytest

from mhcgnomes import Allele, Gene, Pair, parse
from mhcgnomes.pair import infer_class2_alpha_chain

from .common import eq_


def test_restrict_num_allele_fields_HLA_DRA_01_01_01_01_DRB1_01_01_01_01():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    eq_(type(result), Pair)
    eq_(result.alpha.allele_fields, ("01", "01", "01", "01"))
    eq_(result.beta.allele_fields, ("01", "01", "01", "01"))

    result2 = result.restrict_allele_fields(2)
    eq_(
        result2.alpha.allele_fields,
        (
            "01",
            "01",
        ),
    )
    eq_(
        result2.beta.allele_fields,
        (
            "01",
            "01",
        ),
    )


def test_annotation_null_HLA_DRA_01_01_01_01_DRB1_01_01_01_01N():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    eq_(type(result), Pair)
    assert not result.annotation_null

    result = parse("DRA*01:01:01:01/DRB*01:01:01:01N")
    eq_(type(result), Pair)
    assert result.annotation_null


@pytest.mark.parametrize(
    "annotation, property_name",
    [
        ("C", "annotation_cystosolic"),
        ("S", "annotation_secreted"),
        ("Q", "annotation_questionable"),
        ("L", "annotation_low_expression"),
        ("A", "annotation_aberrant_expression"),
        ("G", "annotation_group"),
        ("Ps", "annotation_pseudogene"),
        ("Sp", "annotation_splice_variant"),
    ],
)
def test_pair_annotation_flags_propagate_from_component_alleles(annotation, property_name):
    alpha = Allele.get("HLA", "DRA", "01", "01", "01", "01")
    beta = Allele.get("HLA", "DRB1", "01", "01", "01", "01", annotation=annotation)
    result = Pair.get(alpha, beta)

    assert result is not None
    assert getattr(result, property_name)


def test_pair_get_rejects_invalid_inputs():
    beta = Allele.get("HLA", "DRB1", "01", "01")

    assert Pair.get(None, beta) is None
    assert Pair.get(beta, None) is None
    assert Pair.get("not-an-allele", beta) is None
    assert Pair.get(beta, "not-an-allele") is None


def test_pair_to_record_and_string_include_gene_and_mhc_class():
    result = parse("HLA-DRA*01:01/DRB1*01:01")

    assert result.to_string() == "HLA-DRA*01:01/DRB1*01:01"
    assert result.gene_name == "DRA/DRB1"
    assert result.to_record() == {
        "gene": "DRA/DRB1",
        "mhc_class": "IIa",
        "is_mutant": False,
        "allele": "HLA-DRA*01:01/DRB1*01:01",
    }


def test_infer_class2_alpha_chain_for_hla_beta_allele_returns_pair():
    beta = Allele.get("HLA", "DRB1", "01", "01")
    result = infer_class2_alpha_chain(beta)

    assert type(result) is Pair
    assert result.alpha == Allele.get("HLA", "DRA", "01", "01")
    assert result.beta == beta


def test_infer_class2_alpha_chain_leaves_class1_unchanged():
    result = parse("HLA-A*02:01")
    assert infer_class2_alpha_chain(result) == result


@pytest.mark.parametrize(
    "name, expected_alpha_gene",
    [
        # DR locus across species
        ("Patr-DRB1*03:08", "DRA"),
        ("BoLA-DRB3*001:01", "DRA"),
        ("Mamu-DRB1*03:03", "DRA"),
        ("Mamu-DRB*w2:01", "DRA"),
        # DQ locus
        ("Patr-DQB1*02:01", "DQA1"),
        ("BoLA-DQB1*02:01", "DQA1"),
        # Mouse H2 A and E loci
        ("H2-Ab*b", "AA"),
        ("H2-Eb*b", "EA"),
    ],
)
def test_infer_class2_alpha_chain_for_non_human_species(name, expected_alpha_gene):
    """Non-human Class II beta alleles should pair with the matching alpha Gene."""
    result = parse(name, infer_class2_pairing=True)
    assert type(result) is Pair, f"Expected Pair for {name}, got {type(result).__name__}"
    assert type(result.alpha) is Gene
    eq_(result.alpha.name, expected_alpha_gene)
    assert type(result.beta) is Allele


def test_infer_class2_alpha_chain_leaves_alpha_allele_unchanged():
    """Alpha chain alleles should not be wrapped in a Pair."""
    for name in ["HLA-DRA*01:01", "HLA-DQA1*01:02"]:
        result = parse(name)
        assert infer_class2_alpha_chain(result) is result


def test_infer_class2_alpha_chain_leaves_pair_unchanged():
    """An already-paired result should pass through unchanged."""
    result = parse("HLA-DRA*01:01/DRB1*01:01")
    assert type(result) is Pair
    assert infer_class2_alpha_chain(result) is result


def test_infer_class2_alpha_chain_leaves_gene_unchanged():
    """A bare Gene (not Allele) should not be paired."""
    result = parse("HLA-DRB1")
    assert type(result) is Gene
    assert infer_class2_alpha_chain(result) is result
