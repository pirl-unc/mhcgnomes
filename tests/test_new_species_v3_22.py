"""
Tests for species, gene aliases, and gene series added in v3.22.0.

Covers:
- Ctenomys tuco-tuco rodents (4 species with numbered DRB lineages)
- New birds: herons, egrets, petrel, penguin
- New fish: minnow, bream, pike
- New lizard: Ameiva ameiva
- Crocodilian DB series extension (DB10-DB55)
- Turdus thrush PFA series (PFA01-PFA30)
"""

import pytest

from mhcgnomes import Allele, Gene, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# Ctenomys tuco-tuco rodents
# ---------------------------------------------------------------------------

CTENOMYS_SPECIES = [
    ("Ctta", "Ctenomys talarum"),
    ("Ctau", "Ctenomys australis"),
    ("Ctto", "Ctenomys torquatus"),
    ("Ctpe", "Ctenomys pearsoni"),
]


@pytest.mark.parametrize("prefix, latin", CTENOMYS_SPECIES)
def test_ctenomys_species_parseable(prefix, latin):
    species = Species.get(prefix)
    assert species is not None, f"Species not found for prefix {prefix}"
    assert species.latin_name == latin


@pytest.mark.parametrize("prefix, latin", CTENOMYS_SPECIES)
def test_ctenomys_latin_name_lookup(prefix, latin):
    species = Species.get(latin)
    assert species is not None, f"Species not found for latin name {latin}"


def test_ctenomys_talarum_DRB01():
    # DRB01 is an allele lineage (DRB*01), not a separate gene
    eq_(parse("Ctta-DRB01"), Allele.get("Ctta", "DRB", "01"))


def test_ctenomys_talarum_DQB():
    eq_(parse("Ctta-DQB"), Gene.get("Ctta", "DQB"))


def test_ctenomys_pearsoni_DRB03():
    # DRB03 is an allele lineage (DRB*03), not a separate gene
    eq_(parse("Ctpe-DRB03"), Allele.get("Ctpe", "DRB", "03"))


def test_ctenomys_torquatus_inherits_rodentia_DRB1():
    """Ctenomys species should also inherit standard DRB1 from Rodentia sp."""
    gene = Gene.get("Ctta", "DRB1")
    assert gene is not None


# ---------------------------------------------------------------------------
# New bird species
# ---------------------------------------------------------------------------

NEW_BIRDS = [
    ("ArdeCine", "Ardea cinerea"),
    ("HaloCaer", "Halobaena caerulea"),
    ("BubuIbis", "Bubulcus ibis"),
    ("EgreSacr", "Egretta sacra"),
    ("EudyChrys", "Eudyptes chrysocome"),
]


@pytest.mark.parametrize("prefix, latin", NEW_BIRDS)
def test_new_bird_species_parseable(prefix, latin):
    species = Species.get(prefix)
    assert species is not None, f"Species not found for prefix {prefix}"
    assert species.latin_name == latin


@pytest.mark.parametrize("prefix, latin", NEW_BIRDS)
def test_new_bird_latin_name_lookup(prefix, latin):
    species = Species.get(latin)
    assert species is not None


def test_new_bird_short_prefix_lookup():
    """Short prefixes in 'other prefixes' should also resolve."""
    assert Species.get("Arci") is not None
    assert Species.get("Haca") is not None
    assert Species.get("Buib") is not None
    assert Species.get("Egsa") is not None
    assert Species.get("Euch") is not None


def test_ardea_cinerea_inherits_DAB1():
    eq_(parse("Arci-DAB1"), Gene.get("Arci", "DAB1"))


def test_egretta_sacra_inherits_DAB():
    eq_(parse("Egsa-DAB"), Gene.get("Egsa", "DAB"))


def test_eudyptes_chrysocome_HA1F():
    eq_(parse("Euch-HA1F"), Gene.get("Euch", "HA1F"))


def test_eudyptes_chrysocome_DMB():
    eq_(parse("Euch-DMB"), Gene.get("Euch", "DMB"))


# ---------------------------------------------------------------------------
# New fish species
# ---------------------------------------------------------------------------

NEW_FISH = [
    ("HyboAmar", "Hybognathus amarus"),
    ("MegaAmbl", "Megalobrama amblycephala"),
    ("EsoxLuci", "Esox lucius"),
]


@pytest.mark.parametrize("prefix, latin", NEW_FISH)
def test_new_fish_species_parseable(prefix, latin):
    species = Species.get(prefix)
    assert species is not None, f"Species not found for prefix {prefix}"
    assert species.latin_name == latin


def test_hybognathus_amarus_inherits_DAB1():
    # Addressed by its own prefix: Hyam is Hyperoodon ampullatus in IPD-MHC,
    # and the minnow keeps Hyam only as a context-only alias (see #112).
    eq_(parse("HyboAmar-DAB1"), Gene.get("HyboAmar", "DAB1"))


def test_megalobrama_inherits_UA():
    eq_(parse("Meam-UA"), Gene.get("Meam", "UA"))


def test_esox_lucius_HA2B():
    eq_(parse("Eslu-HA2B"), Gene.get("Eslu", "HA2B"))


def test_esox_lucius_HB2D():
    eq_(parse("Eslu-HB2D"), Gene.get("Eslu", "HB2D"))


# ---------------------------------------------------------------------------
# New reptile: Ameiva ameiva
# ---------------------------------------------------------------------------


def test_ameiva_species_parseable():
    species = Species.get("AmeiAmei")
    assert species is not None
    assert species.latin_name == "Ameiva ameiva"


def test_ameiva_short_prefix():
    assert Species.get("Amam") is not None


def test_ameiva_LC1():
    eq_(parse("Amam-LC1"), Gene.get("Amam", "LC1"))


def test_ameiva_LC13():
    eq_(parse("Amam-LC13"), Gene.get("Amam", "LC13"))


# ---------------------------------------------------------------------------
# Crocodilian DB series extension (DB10-DB55)
# ---------------------------------------------------------------------------


def test_crocodylia_DB10_defined():
    """DB10 should be inherited by all crocodilians."""
    gene = Gene.get("Crpo", "DB10")
    assert gene is not None


def test_crpo_DB50():
    eq_(parse("Crpo-DB50"), Gene.get("Crpo", "DB50"))


def test_crpo_DB55():
    eq_(parse("Crpo-DB55"), Gene.get("Crpo", "DB55"))


def test_crni_inherits_DB30():
    """Nile crocodile should also inherit extended DB series."""
    gene = Gene.get("CrocNilo", "DB30")
    assert gene is not None


# ---------------------------------------------------------------------------
# Turdus thrush PFA series (PFA01-PFA30)
# ---------------------------------------------------------------------------


def test_turdus_sp_defined():
    species = Species.get("Turdus")
    assert species is not None


def test_turdus_merula_parent_is_turdus_sp():
    species = Species.get("TurdMeru")
    assert species is not None
    assert species.parent.latin_name == "Turdus sp."


def test_turdus_merula_PFA01():
    eq_(parse("TurdMeru-PFA01"), Gene.get("TurdMeru", "PFA01"))


def test_turdus_merula_PFA15():
    eq_(parse("TurdMeru-PFA15"), Gene.get("TurdMeru", "PFA15"))


def test_turdus_merula_PFA30():
    eq_(parse("TurdMeru-PFA30"), Gene.get("TurdMeru", "PFA30"))


def test_turdus_naumanni_inherits_PFA():
    gene = Gene.get("TurdNaum", "PFA10")
    assert gene is not None


def test_turdus_merula_still_inherits_aves_DAB():
    """Re-parenting to Turdus sp. should not break Aves inheritance."""
    gene = Gene.get("TurdMeru", "DAB")
    assert gene is not None
