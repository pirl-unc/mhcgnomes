import pytest

from mhcgnomes import Allele, Mutation, Pair, parse
from mhcgnomes.parser import Parser

from .common import eq_


def test_allele_get_parses_mutation_strings():
    allele = Allele.get("HLA", "A", "02", "01", mutations="N80I")
    expected = Mutation.get(pos=80, aa_original="N", aa_mutant="I")
    eq_(allele.mutations, (expected,))
    assert allele.is_mutant
    assert allele.to_string().endswith("N80I mutant")


def test_mutation_get_preserves_raw_string():
    mutation = Mutation.get(pos=86, aa_original="G", aa_mutant="Y", raw_string="G86Y")
    eq_(mutation.raw_string, "G86Y")


@pytest.mark.parametrize(
    ("text", "reference"),
    [
        ("HLA-B*08:01 E76C mutant", "HLA-B*08:01:01:01"),
        ("HLA-B*08:01 E76C G86Y mutant", "HLA-B*08:01:01:01"),
        ("HLA-C*03:01 N80I mutant", "HLA-C*03:04:01:01"),
        # Synthetic substitution tests an existing gene-changing alias;
        # it does not assert that this mutant was observed biologically.
        ("Saha-I*27 N80I mutant", "Saha-UC*27"),
    ],
)
def test_allele_alias_preserves_explicit_mutations(text, reference):
    original = parse(text, use_allele_aliases=False)
    result = parse(text, use_allele_aliases=True)
    assert result.mutations == original.mutations
    assert result.is_mutant
    assert result.copy(mutations=()).to_string() == reference
    assert result.raw_string == text
    assert parse(result.to_string(), use_allele_aliases=True) == result


@pytest.mark.parametrize(
    ("text", "expected", "alpha_mutations", "beta_mutations"),
    [
        (
            "HLA-DRA*01:01/DRB1*01:01 C30S mutant",
            "HLA-DRA*01:01:01:01/DRB1*01:01:01:01 C30S mutant",
            (),
            (Mutation.parse("C30S"),),
        ),
        (
            "HLA-DRA*01:01 F54C mutant/DRB1*01:01",
            "HLA-DRA*01:01:01:01 F54C mutant/DRB1*01:01:01:01",
            (Mutation.parse("F54C"),),
            (),
        ),
    ],
)
def test_pair_alias_preserves_reported_chain_mutation(
    text, expected, alpha_mutations, beta_mutations
):
    result = parse(text, use_allele_aliases=True)
    assert result.to_string() == expected
    assert result.alpha.mutations == alpha_mutations
    assert result.beta.mutations == beta_mutations
    assert result.raw_string == text


def test_alias_transform_keeps_mutations_on_their_original_chains():
    alpha = Allele.get("HLA", "DRA", "01", "01", mutations="C30S")
    beta = Allele.get("HLA", "DRB1", "01", "01", mutations="G86Y")
    pair = Pair.get(alpha, beta, raw_string="explicitly constructed mutant pair")
    parser = Parser(use_allele_aliases=True)
    result = parser.transform_parse_candidate(pair)
    assert result.alpha.mutations == alpha.mutations
    assert result.beta.mutations == beta.mutations
    assert result.alpha.allele_fields == ("01", "01", "01", "01")
    assert result.beta.allele_fields == ("01", "01", "01", "01")
    assert result.raw_string == pair.raw_string
    assert parser.transform_parse_candidate(result) == result


def test_gene_unassigned_alias_does_not_discard_unrepresentable_mutation():
    # AlleleWithoutGene cannot carry mutations; retain the explicit input
    # rather than return a mutation-free alias target. This is synthetic.
    text = "Saha-I*49 N80I mutant"
    original = parse(text, use_allele_aliases=False)
    result = parse(text, use_allele_aliases=True)
    assert result == original
    assert result.is_mutant
    assert result.raw_string == text
