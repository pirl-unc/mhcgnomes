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


def test_num_own_genes_excludes_inherited_genes():
    quail = Species.get_by_latin_name("Coturnix japonica")
    chicken = Species.get_by_latin_name("Gallus gallus")
    buffalo = Species.get_by_latin_name("Bubalus bubalis")

    # quail sees more genes than chicken only because of what it inherits
    assert quail.num_genes > chicken.num_genes
    assert quail.num_own_genes < chicken.num_own_genes

    # water buffalo declares only DQA/DQA1/DQB itself
    eq_(buffalo.num_own_genes, 3)
    assert buffalo.num_genes > buffalo.num_own_genes
