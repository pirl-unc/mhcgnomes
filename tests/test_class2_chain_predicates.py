"""
Which chain a class II result names, and the parses that depend on it.

`Gene` is a sibling of `ResultWithGene` rather than a subclass, so before
3.43.0 it fell through to `Result`'s `return False` stubs: every class II gene
reported neither chain, even with the chain type sitting in the species table.
That also broke parsing, because the parser gates chain-suffixed candidates on
these predicates while listing `Gene` among the candidate types.

https://github.com/pirl-unc/mhcgnomes/issues/137
"""

import pytest

from mhcgnomes import Gene, parse

from .common import eq_, ok_

ALPHA_GENES = ["DRA", "DQA1", "DPA1"]
BETA_GENES = ["DRB1", "DQB1", "DPB1"]


@pytest.mark.parametrize("gene_name", ALPHA_GENES)
def test_class2_alpha_gene_reports_alpha(gene_name):
    gene = parse(f"HLA-{gene_name}", required_result_types=[Gene])
    ok_(gene.is_class2)
    eq_(gene.class2_chain_type, "alpha")
    ok_(gene.is_class2_alpha)
    ok_(not gene.is_class2_beta)


@pytest.mark.parametrize("gene_name", BETA_GENES)
def test_class2_beta_gene_reports_beta(gene_name):
    gene = parse(f"HLA-{gene_name}", required_result_types=[Gene])
    eq_(gene.class2_chain_type, "beta")
    ok_(gene.is_class2_beta)
    ok_(not gene.is_class2_alpha)


@pytest.mark.parametrize("gene_name", ALPHA_GENES + BETA_GENES)
def test_gene_and_allele_agree_on_chain(gene_name):
    """
    Allele got the real implementation from ResultWithGene while Gene got the
    stub, so the two disagreed about the same locus.
    """
    gene = parse(f"HLA-{gene_name}", required_result_types=[Gene])
    allele = parse(f"HLA-{gene_name}*01:01")
    eq_(gene.class2_chain_type, allele.class2_chain_type)
    eq_(gene.is_class2_alpha, allele.is_class2_alpha)
    eq_(gene.is_class2_beta, allele.is_class2_beta)


# A bare gene plus a chain word. Every one of these raised ParseError before
# 3.43.0, while the *less* specific "HLA-DR alpha" parsed, because that takes
# the Class2Locus branch instead of the Gene branch.
CHAIN_SUFFIXED = [
    ("HLA-DRA alpha", "HLA-DRA"),
    ("HLA-DRB1 beta", "HLA-DRB1"),
    ("HLA-DQA1 alpha", "HLA-DQA1"),
    ("HLA-DQB1 beta", "HLA-DQB1"),
    ("HLA-DPA1 alpha", "HLA-DPA1"),
    ("HLA-DPB1 beta", "HLA-DPB1"),
]


@pytest.mark.parametrize("name,expected", CHAIN_SUFFIXED)
def test_chain_suffixed_gene_parses(name, expected):
    eq_(parse(name).to_string(), expected)


@pytest.mark.parametrize(
    "name", ["HLA-DR alpha", "H2-IA alpha", "HLA-DRA*01:01 alpha", "HLA-DQA1*01:01 alpha"]
)
def test_paths_that_already_worked_still_work(name):
    assert parse(name, raise_on_error=False) is not None


@pytest.mark.parametrize("name", ["HLA-DRA beta", "HLA-DRB1 alpha", "HLA-DQA1 beta", "HLA-A beta"])
def test_a_mismatched_chain_word_is_still_rejected(name):
    """The point is to answer the chain question, not to accept any suffix."""
    eq_(parse(name, raise_on_error=False), None)


def test_class1_gene_is_not_a_class2_chain():
    gene = parse("HLA-A", required_result_types=[Gene])
    eq_(gene.class2_chain_type, None)
    ok_(not gene.is_class2_alpha)
    ok_(not gene.is_class2_beta)


def test_pair_names_no_single_chain():
    """A Pair has an alpha and a beta, so it is neither."""
    pair = parse("HLA-DQA1*01:01/DQB1*02:01")
    eq_(pair.class2_chain_type, None)
    ok_(not pair.is_class2_alpha)
    ok_(not pair.is_class2_beta)


def test_unknown_chain_type_reports_none_instead_of_raising():
    """
    The old implementation indexed the chain table with `[]`, so a class II
    gene with no curated chain type would have raised KeyError. Nothing in the
    ontology hits that today, so this exercises the property against a stand-in
    rather than mutating a cached Species -- which would leak the missing entry
    into every test that ran afterwards.
    """
    from mhcgnomes.result_with_mhc_class import ResultWithMhcClass

    class FakeSpecies:
        class2_gene_name_to_chain_type = {}

    class ClassIIResultWithNoChainType:
        gene_name = "DRA"
        species = FakeSpecies()
        is_class2 = True
        class2_chain_type = ResultWithMhcClass.class2_chain_type

    eq_(ClassIIResultWithNoChainType().class2_chain_type, None)


def test_the_real_ontology_gives_every_class2_gene_a_chain_type():
    """The companion to the test above: today the .get never misses."""
    from mhcgnomes.species import latin_name_to_species_object

    missing = [
        (species.name, gene_name)
        for species in latin_name_to_species_object.values()
        for gene_name in species.gene_names
        if species.get_mhc_class_of_gene(gene_name) in ("II", "IIa", "IIb")
        and gene_name not in species.class2_gene_name_to_chain_type
    ]
    eq_(missing, [], f"class II genes with no curated chain type: {missing[:5]}")
