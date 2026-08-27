"""
Coverage of the two authorities that assign MHC names.

Species designations come from the Comparative MHC Nomenclature Committee via
IPD-MHC group listings; human gene names come from IMGT/HLA. These tests pin
the entries added from a sweep of both against the ontology.

https://github.com/pirl-unc/mhcgnomes/issues/111
https://github.com/pirl-unc/mhcgnomes/issues/113
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# IPD-MHC species designations
# ---------------------------------------------------------------------------

# (IPD prefix, latin name) — https://www.ebi.ac.uk/ipd/mhc/group/NHP/species
CAPUCHINS = [
    ("Ceal", "Cebus albifrons"),
    ("Ceap", "Cebus apella"),
    ("Ceca", "Cebus capucinus"),
    ("Ceim", "Cebus imitator"),
    ("Ceka", "Cebus kaapori"),
    ("Ceol", "Cebus olivaceus"),
    ("Saca", "Sapajus cay"),
    ("Sali", "Sapajus libidinosus"),
    ("Sama", "Sapajus apella macrocephalus"),
    ("Sani", "Sapajus nigritus"),
    ("Saxa", "Sapajus xanthosternos"),
]

# https://www.ebi.ac.uk/ipd/mhc/group/CeLA/species
CETACEANS = [
    ("Bamubr", "Balaenoptera musculus brevicauda"),
    ("Bari", "Balaenoptera ricei"),
    ("Esro", "Eschrichtius robustus"),
    ("Eugl", "Eubalaena glacialis"),
    ("Hyam", "Hyperoodon ampullatus"),
    ("Inge", "Inia geoffrensis"),
    ("Kosi", "Kogia sima"),
    ("Laal", "Lagenorhynchus albirostris"),
    ("Live", "Lipotes vexillifer"),
    ("Momo", "Monodon monoceros"),
    ("Phph", "Phocoena phocoena"),
    ("Phsi", "Phocoena sinus"),
]

# https://www.ebi.ac.uk/ipd/mhc/group/DLA/species
CANIDS = [
    ("Caad", "Canis adustus"),
    ("Caau", "Canis aureus"),
    ("Caba", "Canis lupus baileyi"),
    ("Cala", "Canis latrans"),
    ("Calu", "Canis lupus"),
    ("Came", "Canis mesomelas"),
    ("Caru", "Canis rufus"),
    ("Casi", "Canis simensis"),
    ("Cual", "Cuon alpinus"),
    ("Lypi", "Lycaon pictus"),
]

# https://www.ebi.ac.uk/ipd/mhc/group/SLA/species
SUIDS = [
    ("Phaf", "Phacochoerus africanus"),
    ("Sudo", "Sus domesticus"),
    ("Susc", "Sus scrofa"),
]

IPD_SPECIES = CAPUCHINS + CETACEANS + CANIDS + SUIDS


@pytest.mark.parametrize("prefix,latin_name", IPD_SPECIES)
def test_ipd_prefix_resolves_to_its_species(prefix, latin_name):
    species = Species.get(prefix)
    assert species is not None, f"Species.get({prefix!r}) returned None"
    eq_(species.name, latin_name)


@pytest.mark.parametrize("prefix,latin_name", IPD_SPECIES)
def test_ipd_species_reachable_by_latin_name(prefix, latin_name):
    eq_(Species.get_by_latin_name(latin_name).prefix, prefix)


# ---------------------------------------------------------------------------
# Genus boundaries
#
# Cuon, Lycaon and Phacochoerus are canids and suids but not Canis or Sus, so
# they must not inherit the DLA/SLA prefix or those genera's gene lists. That
# is the failure described in issue #109 for water buffalo under Bos sp.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "latin_name,family_node",
    [
        ("Cuon alpinus", "Canidae sp."),
        ("Lycaon pictus", "Canidae sp."),
        ("Phacochoerus africanus", "Suidae sp."),
    ],
)
def test_out_of_genus_species_hang_off_the_family_not_the_genus(latin_name, family_node):
    eq_(Species.get_by_latin_name(latin_name).parent_species.name, family_node)


@pytest.mark.parametrize("prefix", ["Cual", "Lypi"])
def test_non_canis_canids_do_not_answer_to_DLA(prefix):
    species = Species.get(prefix)
    assert "DLA" not in {p.upper() for p in species.all_mhc_prefixes}


def test_warthog_does_not_answer_to_SLA():
    species = Species.get("Phaf")
    assert "SLA" not in {p.upper() for p in species.all_mhc_prefixes}


@pytest.mark.parametrize("prefix,owner", [("DLA", "Canis sp."), ("SLA", "Sus sp.")])
def test_family_node_does_not_take_over_the_group_prefix(prefix, owner):
    """A taxonomic prefix is not inherited, so DLA and SLA keep their owners."""
    eq_(Species.get(prefix).name, owner)


def test_existing_group_alleles_are_unaffected():
    eq_(parse("DLA-DRB1*001:01").species.name, "Canis sp.")
    eq_(parse("SLA-1*01:01").species.name, "Sus sp.")


# ---------------------------------------------------------------------------
# IMGT/HLA gene names
# ---------------------------------------------------------------------------

IMGT_HLA_GENES_ADDED = [
    "DRB2",
    "DQB3",
    "DPA2",
    "DPA3",
    "DPB2",
    "MICC",
    "MICD",
    "MICE",
    "PSMB8",
    "PSMB9",
]


@pytest.mark.parametrize("gene_name", IMGT_HLA_GENES_ADDED)
def test_imgt_hla_gene_parses(gene_name):
    result = parse(f"HLA-{gene_name}", raise_on_error=False)
    assert result is not None, f"HLA-{gene_name} did not parse"
    eq_(result.species.name, "Homo sapiens")
    eq_(result.name, gene_name)


@pytest.mark.parametrize(
    "gene_name",
    ["DRB2", "DQB3", "DPA2", "DPA3", "DPB2", "MICC", "MICD", "MICE"],
)
def test_added_imgt_pseudogenes_are_marked_as_such(gene_name):
    assert parse(f"HLA-{gene_name}").is_pseudogene


def test_proteasome_subunits_keep_their_legacy_names():
    """LMP7/LMP2 are to PSMB8/PSMB9 what RING4/RING11 are to TAP1/TAP2."""
    eq_(parse("HLA-LMP7").name, "PSMB8")
    eq_(parse("HLA-LMP2").name, "PSMB9")


def test_single_letter_haplotype_shorthand_is_not_shadowed():
    """
    IMGT/HLA also names the class I fragments N, R, S, T, U, W, X, Y, Z. They
    are deliberately not in the ontology: adding them turns bare mouse and rat
    haplotype shorthand into human gene fragments. See issue #113.
    """
    eq_(parse("n").to_string(), "RT1-n")
    eq_(parse("u").to_string(), "H2-u")
    eq_(parse("s").to_string(), "H2-s")
    assert parse("HLA-Z*01:01", raise_on_error=False) is None
