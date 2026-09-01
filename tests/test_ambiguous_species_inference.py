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
    # NHP is its own node, sibling to Homo sapiens under Primata sp., because
    # IPD-MHC's NHP group means Non-Human Primates and so is not the primate
    # order (#122, #126).
    ("NHP", "NHP"),
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

    Ranking the declarers is only allowed to settle it when they lie in one
    lineage -- see test_bare_gene_shared_across_lineages_names_no_species,
    which took DBB1, DAB1 and Ia1 out of this list.
    """
    for gene_name, expected in [
        # a group node and its own descendant: one lineage
        ("BLB2", "Gallus gallus"),
        ("BLB1", "Gallus gallus"),
        # chicken and guineafowl are not one lineage, but the guineafowl's
        # BF2 is marked `context only`, leaving the chicken sole claimant
        ("BF2", "Gallus gallus"),
    ]:
        result = parse(gene_name)
        eq_(result.species.name, expected)
        assert result.species.declares_gene(gene_name), gene_name


# ---------------------------------------------------------------------------
# 3. A gene symbol shared across lineages names no species
# https://github.com/pirl-unc/mhcgnomes/issues/130
# ---------------------------------------------------------------------------

# The report: every one of these resolved to Macaca fascicularis, which
# declares the symbol and happened to have the longest gene list among the
# 45 species that do.
CLASS2_SYMBOLS_SHARED_ACROSS_SPECIES = [
    "DRB1*01:01",
    "DQA1*01:01",
    "DQB1*05:01",
    "DPA1*01:03",
    "DPB1*04:01",
]


@pytest.mark.parametrize("name", CLASS2_SYMBOLS_SHARED_ACROSS_SPECIES)
def test_shared_class2_symbol_names_no_species_on_its_own(name):
    eq_(parse(name, default_species=None, raise_on_error=False), None)


@pytest.mark.parametrize("name", CLASS2_SYMBOLS_SHARED_ACROSS_SPECIES)
def test_shared_class2_symbol_still_uses_the_default_species(name):
    # The fix must not touch the ordinary human case: a caller who left
    # default_species alone is asking for the human reading.
    result = parse(name)
    eq_(result.species.name, "Homo sapiens")
    eq_(result.species_source, "default")


@pytest.mark.parametrize(
    "gene_name,declarers",
    [
        # quail class II beta versus the ray-finned fish group node
        ("DBB1", ["Coturnix japonica", "Actinopterygii sp."]),
        # nine declarers across crocodiles, amphibians, birds, fish and
        # marsupials; the saltwater crocodile used to win on gene count
        ("DAB1", ["Crocodylus porosus", "Amphibia sp."]),
        # flounder "Ia1" and golden pheasant "IA1" normalize to one key, and
        # the tokenizer lower-cases before the parser ever sees the spelling,
        # so nothing can tell these apart. See #160.
        ("Ia1", ["Paralichthys olivaceus", "Chrysolophus pictus"]),
    ],
)
def test_bare_gene_shared_across_lineages_names_no_species(gene_name, declarers):
    for latin_name in declarers:
        species = Species.get_by_latin_name(latin_name)
        assert species.declares_gene(gene_name), f"{latin_name} no longer declares {gene_name}"
    eq_(parse(gene_name, raise_on_error=False), None)
    # naming the species still works, which is the whole point of refusing to
    # guess one
    eq_(
        parse(f"{Species.get_by_latin_name(declarers[0]).prefix}-{gene_name}").species.name,
        declarers[0],
    )


def test_guineafowl_bf2_is_real_but_does_not_claim_the_bare_name():
    """
    GenBank EU430728.1 and EF643463.1 are both "Numida meleagris MHC class I
    antigen (BF2) mRNA", so the gene is not a curation error. What the
    guineafowl does not have is the bare form: IEDB publishes chicken alleles
    as BF2*2101, BF2*0401 and so on, and nothing is published as a guineafowl
    BF2 allele.
    """
    guineafowl = Species.get_by_latin_name("Numida meleagris")
    assert guineafowl.declares_gene("BF2")
    assert guineafowl.gene_is_context_only("BF2")
    eq_(parse("NumiMele-BF2").species.name, "Numida meleagris")
    eq_(parse("NumiMele-BF2*01:01").species.name, "Numida meleagris")
    eq_(parse("BF2*02:01").species.name, "Gallus gallus")


def test_species_inferred_from_a_gene_name_is_not_reported_as_explicit():
    """
    `infer_species_from_prefix` falls back to a gene name unique to one
    species and returns an empty matched string to say so. `species_named_in`
    counted it anyway, so `require_explicit_species` -- whose entire job is
    rejecting an inferred species -- accepted "A8*01:01", where nothing names
    a species. 98 gene names took that route.
    """
    for name in ["A8*01:01", "BF2*02:01", "B12c*01:01"]:
        eq_(parse(name).species_source, "inferred")
        eq_(parse(name, require_explicit_species=True, raise_on_error=False), None)
    # and a string that does name its species is unaffected
    eq_(parse("Gaga-BLB2*02", require_explicit_species=True).species.name, "Gallus gallus")


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
