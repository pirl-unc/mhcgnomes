import pytest

from mhcgnomes import Allele, Pair, parse
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


@pytest.mark.parametrize("name", ["HLA-A*02:01", "BoLA-DRB3*001:01"])
def test_infer_class2_alpha_chain_leaves_other_inputs_unchanged(name):
    result = parse(name)

    assert infer_class2_alpha_chain(result) == result
