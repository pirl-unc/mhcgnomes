"""
Tests for species and gene additions in v3.23.0.

Covers:
- Notamacropus rufogriseus (wallaby) with Maru prefix
- Kryptolebias marmoratus killifish class I genes (A1-H1) and Krma prefix
- Additional Ctenomys tuco-tuco species
- Batch rodent species (Dipodomys, Octodon, Heterocephalus, etc.)
- Batch fish species (Merluccius, Liparis, Oncorhynchus nerka, etc.)
- New bird/reptile/amphibian species
"""

import pytest

from mhcgnomes import Gene, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# All new species with their prefixes and optional alt-prefixes
# ---------------------------------------------------------------------------

NEW_SPECIES = [
    # Wallaby
    ("NotaRufo", "Notamacropus rufogriseus", ["Maru"]),
    # Ctenomys
    ("CtenHaig", "Ctenomys haigi", []),
    ("CtenArge", "Ctenomys argentinus", []),
    ("CtenFrat", "Ctenomys frater", []),
    ("CtenOpim", "Ctenomys opimus", []),
    # Rodents
    ("DipoOrdi", "Dipodomys ordii", []),
    ("OctoDegu", "Octodon degus", []),
    ("HeteGlab", "Heterocephalus glaber", []),
    ("NannGali", "Nannospalax galili", []),
    ("PeroMani", "Peromyscus maniculatus", []),
    ("PeroLeuc", "Peromyscus leucopus", []),
    ("JacuJacu", "Jaculus jaculus", []),
    ("SigmHisp", "Sigmodon hispidus", []),
    ("CricBara", "Cricetulus barabensis", []),
    ("CynoGunn", "Cynomys gunnisoni", []),
    ("DeloSubl", "Delomys sublineatus", []),
    ("RattFusc", "Rattus fuscipes", []),
    # Mus species
    ("MusMinu", "Mus minutoides", []),
    ("MusPaha", "Mus pahari", []),
    ("MusSpic", "Mus spicilegus", []),
    ("MusShor", "Mus shortridgei", []),
    ("MusGrat", "Mus gratus", []),
    ("MusSetu", "Mus setulosus", []),
    ("MusTerr", "Mus terricolor", []),
    # Fish
    ("MerlPoll", "Merluccius polli", ["Mepo"]),
    ("LipaTana", "Liparis tanakae", []),
    ("TripTibe", "Triplophysa tibetana", []),
    ("AuloHans", "Aulonocara hansbaenschi", []),
    ("OdonPota", "Odontobutis potamophilus", []),
    ("HippErec", "Hippocampus erectus", []),
    ("OncoNerk", "Oncorhynchus nerka", []),
    ("PolySpat", "Polyodon spathula", []),
    # Bird / Reptile / Amphibian
    ("HaliAlbi", "Haliaeetus albicilla", []),
    ("TiliRugo", "Tiliqua rugosa", []),
    ("ConoSubc", "Conolophus subcristatus", []),
    ("EspaPros", "Espadarana prosoblepon", []),
]


@pytest.mark.parametrize(
    "prefix, latin, alt_prefixes",
    NEW_SPECIES,
    ids=[s[0] for s in NEW_SPECIES],
)
def test_new_species_parseable(prefix, latin, alt_prefixes):
    species = Species.get(prefix)
    assert species is not None, f"Species not found for prefix {prefix}"
    assert species.latin_name == latin


@pytest.mark.parametrize(
    "prefix, latin, alt_prefixes",
    NEW_SPECIES,
    ids=[s[0] for s in NEW_SPECIES],
)
def test_new_species_latin_name_lookup(prefix, latin, alt_prefixes):
    species = Species.get(latin)
    assert species is not None, f"Species not found for latin name {latin}"


@pytest.mark.parametrize(
    "prefix, latin, alt_prefixes",
    [s for s in NEW_SPECIES if s[2]],
    ids=[s[0] for s in NEW_SPECIES if s[2]],
)
def test_new_species_alt_prefix(prefix, latin, alt_prefixes):
    for alt in alt_prefixes:
        species = Species.get(alt)
        assert species is not None, f"Alt prefix {alt} not found for {latin}"
        assert species.latin_name == latin


# ---------------------------------------------------------------------------
# Wallaby: Notamacropus rufogriseus
# ---------------------------------------------------------------------------


def test_maru_DAB():
    eq_(parse("Maru-DAB"), Gene.get("Maru", "DAB"))


def test_maru_UA():
    eq_(parse("Maru-UA"), Gene.get("Maru", "UA"))


def test_maru_DBB():
    eq_(parse("Maru-DBB"), Gene.get("Maru", "DBB"))


# ---------------------------------------------------------------------------
# Killifish: Kryptolebias marmoratus class I genes
# ---------------------------------------------------------------------------


def test_krma_A1():
    eq_(parse("Krma-A1"), Gene.get("Krma", "A1"))


def test_krma_B1():
    eq_(parse("Krma-B1"), Gene.get("Krma", "B1"))


def test_krma_C1():
    eq_(parse("Krma-C1"), Gene.get("Krma", "C1"))


def test_krypmarm_H1():
    eq_(parse("KrypMarm-H1"), Gene.get("KrypMarm", "H1"))


def test_krma_inherits_fish_UA():
    """Killifish should still inherit UA from Actinopterygii sp."""
    gene = Gene.get("Krma", "UA")
    assert gene is not None


# ---------------------------------------------------------------------------
# Ctenomys: new species
# ---------------------------------------------------------------------------


def test_ctenomys_haigi_DRB():
    eq_(parse("CtenHaig-DRB"), Gene.get("CtenHaig", "DRB"))


def test_ctenomys_opimus_DQB():
    eq_(parse("CtenOpim-DQB"), Gene.get("CtenOpim", "DQB"))


# ---------------------------------------------------------------------------
# Rodents: gene inheritance
# ---------------------------------------------------------------------------


def test_dipodomys_inherits_DRB1():
    eq_(parse("DipoOrdi-DRB1"), Gene.get("DipoOrdi", "DRB1"))


def test_heterocephalus_inherits_DQB1():
    eq_(parse("HeteGlab-DQB1"), Gene.get("HeteGlab", "DQB1"))


def test_peromyscus_inherits_DRB1():
    eq_(parse("PeroMani-DRB1"), Gene.get("PeroMani", "DRB1"))


def test_mus_minutoides_inherits_K():
    """Mus species should inherit H2 genes from Mus sp."""
    eq_(parse("MusMinu-K"), Gene.get("MusMinu", "K"))


def test_mus_pahari_inherits_D():
    eq_(parse("MusPaha-D"), Gene.get("MusPaha", "D"))


def test_mus_spicilegus_inherits_EB():
    eq_(parse("MusSpic-EB"), Gene.get("MusSpic", "EB"))


def test_rattus_fuscipes_inherits_A():
    eq_(parse("RattFusc-A"), Gene.get("RattFusc", "A"))


# ---------------------------------------------------------------------------
# Fish: gene inheritance
# ---------------------------------------------------------------------------


def test_merluccius_polli_mepo_prefix():
    eq_(parse("Mepo-UA"), Gene.get("Mepo", "UA"))


def test_oncorhynchus_nerka_inherits_salmonid_UAA():
    eq_(parse("OncoNerk-UAA"), Gene.get("OncoNerk", "UAA"))


def test_polyodon_inherits_DAB():
    eq_(parse("PolySpat-DAB"), Gene.get("PolySpat", "DAB"))


# ---------------------------------------------------------------------------
# Bird / Reptile / Amphibian: gene inheritance
# ---------------------------------------------------------------------------


def test_haliaeetus_inherits_DAB1():
    eq_(parse("HaliAlbi-DAB1"), Gene.get("HaliAlbi", "DAB1"))


def test_tiliqua_inherits_UAA():
    eq_(parse("TiliRugo-UAA"), Gene.get("TiliRugo", "UAA"))


def test_conolophus_inherits_UA():
    eq_(parse("ConoSubc-UA"), Gene.get("ConoSubc", "UA"))


def test_espadarana_inherits_UA():
    eq_(parse("EspaPros-UA"), Gene.get("EspaPros", "UA"))
