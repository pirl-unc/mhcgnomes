"""Synthetic mutation strings test chain ownership, not biological occurrence."""

import pytest

from mhcgnomes import Pair, parse


@pytest.mark.parametrize("aliases", [False, True])
@pytest.mark.parametrize(
    "text, alpha, beta",
    [
        ("HLA-DRA*01:01/DRB1*01:01 alpha C30S mutant", ["C30S"], []),
        ("HLA-DRA*01:01/DRB1*01:01 beta G86Y mutant", [], ["G86Y"]),
        ("HLA-DRA*01:01/DRB1*01:01 alpha C30S beta G86Y mutant", ["C30S"], ["G86Y"]),
        ("HLA-DRA*01:01/DRB1*01:01 DRA:C30S DRB1:G86Y mutant", ["C30S"], ["G86Y"]),
        ("HLA-DRB1*01:01/DRA*01:01 alpha C30S beta G86Y mutant", ["C30S"], ["G86Y"]),
        ("HLA-DRA*01:01 F54C mutant/DRB1*01:01 alpha C30S mutant", ["C30S", "F54C"], []),
        ("HLA-DRA*01:01 F54C mutant/DRB1*01:01 G86Y mutant", ["F54C"], ["G86Y"]),
        # Preserve the legacy unqualified pair-level beta default; selecting
        # alpha must be explicit even when its name is written last.
        ("HLA-DRB1*01:01/DRA*01:01 C30S mutant", [], ["C30S"]),
    ],
)
def test_pair_mutation_selectors_preserve_both_chains(text, alpha, beta, aliases):
    result = parse(text, use_allele_aliases=aliases)
    assert isinstance(result, Pair)
    assert sorted(m.to_string() for m in result.alpha.mutations) == alpha
    assert sorted(m.to_string() for m in result.beta.mutations) == beta
    roundtrip = parse(result.to_string(), use_allele_aliases=aliases)
    assert roundtrip == result


@pytest.mark.parametrize(
    "text",
    [
        "HLA-DRB1*01:01 alpha C30S mutant",
        "HLA-DRB1*01:01 alpha C30S beta G86Y mutant",
        "HLA-DRA*01:01 beta G86Y mutant",
        "HLA-A*02:01 alpha C30S mutant",
    ],
)
def test_single_chain_cannot_silently_drop_an_opposite_chain_mutation(text):
    assert parse(text, raise_on_error=False) is None
