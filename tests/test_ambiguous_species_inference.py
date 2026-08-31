"""
Tests for how a species is chosen when the input string is ambiguous.

Two distinct sources of ambiguity are covered here:

1. A species prefix is inherited by every descendant, so a bare prefix matches
   an ancestor and everything under it ("BoLA" matches Bos sp. but also
   Bubalus bubalis). See https://github.com/pirl-unc/mhcgnomes/issues/103

2. A gene symbol with no species prefix can belong to many species, and the
   winner used to be the species with the most genes *visible* to it, which is
   inflated by whatever a broad parent group defines.
   See https://github.com/pirl-unc/mhcgnomes/issues/105
"""

import pytest

from mhcgnomes import MhcClass, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# 1. A bare species prefix should not silently pick a descendant species
# ---------------------------------------------------------------------------

# (prefix, expected latin name) for every prefix which an ancestor shares with
# its descendants. Each of these used to resolve to an arbitrary descendant,
# chosen by the alphabetical order of the repr string.
PREFIX_TO_EXPECTED_SPECIES = [
    ("BoLA", "Bos sp."),
    ("CELA", "Cetacea sp."),
    ("ChLA", "Pan sp."),
    ("MusSp", "Mus sp."),
    # NHP resolves to Primata sp., the node that owns the prefix. Homo sapiens
    # is a child of that node but does not answer to NHP, because it declares
    # its own "old prefix" and so never inherits the umbrella one (#122).
    ("NHP", "Primata sp."),
    ("OmLA", "Aotus sp."),
    ("RT1", "Rattus sp."),
    ("RhLA", "Macaca sp."),
]


@pytest.mark.parametrize("prefix,expected", PREFIX_TO_EXPECTED_SPECIES)
@pytest.mark.parametrize("mhc_class", ["I", "II"])
def test_class_only_string_keeps_the_prefix_owner_species(prefix, expected, mhc_class):
    result = parse(f"{prefix} class {mhc_class}")
    eq_(type(result), MhcClass)
    eq_(result.mhc_class, mhc_class)
    eq_(result.species.name, expected)


@pytest.mark.parametrize("prefix,expected", PREFIX_TO_EXPECTED_SPECIES)
def test_class_only_string_agrees_with_bare_prefix(prefix, expected):
    """
    "<prefix> class I" and "<prefix>" describe the same species, so they must
    not disagree about which one it is.
    """
    # pin both sides, otherwise a curation change that moved them together
    # would keep this passing
    eq_(Species.get(prefix).name, expected)
    eq_(parse(f"{prefix} class I").species, Species.get(prefix))


def test_bola_class_i_is_cattle_not_water_buffalo():
    """
    BoLA is the *Bovine* Leukocyte Antigen system. Water buffalo is a separate
    genus which inherits the BoLA prefix, and it used to win this parse.
    """
    result = parse("BoLA class I")
    eq_(result.species.name, "Bos sp.")
    assert result.species.name != "Bubalus bubalis"


def test_bola_class_i_agrees_with_bola_allele():
    """The reported symptom: an allele said Bos, the class-only string said Bubalus."""
    eq_(parse("BoLA class I").species, parse("BoLA-N*01301").species)
    eq_(parse("BoLA class II").species, parse("BoLA-DRB3*011:01").species)


def test_explicit_descendant_prefix_still_resolves_to_that_descendant():
    """Preferring the ancestor must not make descendants unreachable."""
    eq_(parse("Bubu-DQA").species.name, "Bubalus bubalis")
    eq_(parse("Bota-DRB3*011:01").species.name, "Bos taurus")


# ---------------------------------------------------------------------------
# 2. Unprefixed gene symbols shared across species
# ---------------------------------------------------------------------------


def test_bare_BLB2_allele_resolves_to_chicken():
    """
    BLB1/BLB2 are the chicken MHC-B class II beta genes. Japanese quail only
    has them by inheritance from "Galliformes sp." -- its own ontology entry
    uses the Coja-DAB1/DBB1/DCB1 nomenclature -- but its larger inherited gene
    count used to win the tie.
    """
    eq_(parse("BLB2*02").species.name, "Gallus gallus")
    eq_(parse("BLB1*02").species.name, "Gallus gallus")


def test_bare_BLB2_agrees_with_explicit_chicken_prefix():
    eq_(parse("BLB2*02"), parse("Gaga-BLB2*02"))


def test_bare_bird_class1_and_class2_genes_agree_on_species():
    """
    Within one bird MHC region, bare BF2 inferred chicken while bare BLB2
    inferred quail. Both are chicken genes.
    """
    eq_(parse("BLB2*02").species, parse("BF2*02:01").species)


def test_quail_genes_still_resolve_to_quail():
    """The quail's own gene names must be unaffected."""
    eq_(parse("Coja-DAB1").species.name, "Coturnix japonica")
    eq_(parse("Coja-BLB2*02").species.name, "Coturnix japonica")


def test_declares_gene_distinguishes_own_genes_from_inherited_ones():
    quail = Species.get_by_latin_name("Coturnix japonica")
    chicken = Species.get_by_latin_name("Gallus gallus")
    buffalo = Species.get_by_latin_name("Bubalus bubalis")
    cattle = Species.get_by_latin_name("Bos sp.")

    # both birds can see BLB2, only chicken declares it
    assert "BLB2" in quail.gene_names
    assert "BLB2" in chicken.gene_names
    assert not quail.declares_gene("BLB2")
    assert chicken.declares_gene("BLB2")

    # and the quail's own class II beta nomenclature belongs to the quail
    assert quail.declares_gene("DBB1")
    assert not chicken.declares_gene("DBB1")

    # water buffalo can see the BoLA genes but declares none of them
    assert "NC1" in buffalo.gene_names
    assert not buffalo.declares_gene("NC1")
    assert cattle.declares_gene("NC1")


def test_declares_gene_is_case_normalizing_but_case_aware():
    """
    Gene lookup normalizes case, so "Ia1" (Paralichthys olivaceus) and "IA1"
    (Chrysolophus pictus) are the same key. Both species declare their own
    spelling; only one matches a given query exactly.
    """
    flounder = Species.get_by_latin_name("Paralichthys olivaceus")
    pheasant = Species.get_by_latin_name("Chrysolophus pictus")

    assert flounder.declares_gene("Ia1")
    assert pheasant.declares_gene("Ia1")
    assert flounder.declares_gene_with_same_case("Ia1")
    assert not pheasant.declares_gene_with_same_case("Ia1")
    assert pheasant.declares_gene_with_same_case("IA1")


def test_bare_gene_resolves_to_a_species_that_declares_it():
    """
    Every candidate under a broad parent group can see that group's genes, so
    the winner must be one that actually uses the name rather than whichever
    inheritor happens to have the largest gene list.
    """
    for gene_name, expected in [
        ("BLB2", "Gallus gallus"),
        ("BLB1", "Gallus gallus"),
        ("BF2", "Gallus gallus"),
        # quail's own class II beta genes stay with the quail
        ("DBB1", "Coturnix japonica"),
        # these were reassigned to an inheriting group when the ranking
        # measured gene-list size instead of declaration
        ("DAB1", "Crocodylus porosus"),
        ("Ia1", "Paralichthys olivaceus"),
    ]:
        result = parse(gene_name)
        eq_(result.species.name, expected)
        assert result.species.declares_gene(gene_name), gene_name


# ---------------------------------------------------------------------------
# Patr-AL is non-classical
# https://github.com/pirl-unc/mhcgnomes/issues/107
# ---------------------------------------------------------------------------


def test_patr_AL_is_non_classical():
    """
    Adams, Cooper & Parham (PMID 11564803) named AL a nonclassical class I
    molecule in the title of the paper describing it: three allotypes, present
    on ~50% of chimpanzee haplotypes, low expression. Being MHC-A-related is
    why it gets filed under A, but that does not make it classical.
    """
    eq_(parse("Patr-AL").mhc_class, "Ib")
    eq_(parse("ChLA-AL").mhc_class, "Ib")


def test_patr_A_is_still_classical():
    eq_(parse("Patr-A*01:01").mhc_class, "Ia")


def test_non_classical_A_related_loci_agree_across_primates():
    """AL should sit with the E/F/G family the ontology already calls Ib."""
    for name in ["HLA-E", "HLA-F", "HLA-G", "Mamu-E*02:11", "Caja-E", "Patr-AL"]:
        eq_(parse(name).mhc_class, "Ib")
