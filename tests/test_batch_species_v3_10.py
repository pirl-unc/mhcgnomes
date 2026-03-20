"""
Tests for the 48 batch-added species from mhcseqs unknown species report.
Covers prefix parsing, latin name lookup, gene inheritance, cross-taxon
isolation, and edge cases for non-standard prefixes.
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_

# All 48 new species with their attested prefixes
BATCH_SPECIES = [
    # Fish
    ("Cosp", "Coregonus sp."),
    ("Trsp", "Tropheus sp."),
    ("KareBico", "Kareius bicoloratus"),
    ("LabeInte", "Labeobarbus intermedius"),
    ("ScopMaxi", "Scophthalmus maximus"),
    ("MonoAlbu", "Monopterus albus"),
    ("AstyMexi", "Astyanax mexicanus"),
    ("SinoGrah", "Sinocyclocheilus grahami"),
    ("SiluAsot", "Silurus asotus"),
    ("OryzDanc", "Oryzias dancena"),
    ("OryzLuzo", "Oryzias luzonensis"),
    ("ScatArgu", "Scatophagus argus"),
    ("RutiRuti", "Rutilus rutilus"),
    ("ParaToxo", "Parachondrostoma toxostoma"),
    ("ClarBatr", "Clarias batrachus"),
    # Snakes
    ("NajaNaja", "Naja naja"),
    ("OphiHann", "Ophiophagus hannah"),
    ("CrotAdam", "Crotalus adamanteus"),
    ("NoteScut", "Notechis scutatus"),
    ("PantGutt", "Pantherophis guttatus"),
    ("PseuText", "Pseudonaja textilis"),
    ("LatiLati", "Laticauda laticaudata"),
    # Lizards
    ("AmblCris", "Amblyrhynchus cristatus"),
    ("EublMacu", "Eublepharis macularius"),
    ("SalvMeri", "Salvator merianae"),
    ("PogoVitt", "Pogona vitticeps"),
    ("PodaMura", "Podarcis muralis"),
    ("LaceAgil", "Lacerta agilis"),
    # Birds
    ("PhasColc", "Phasianus colchicus"),
    ("Iibi", "Tympanuchus cupido"),
    ("CicoBoyc", "Ciconia boyciana"),
    ("AgelPhoe", "Agelaius phoeniceus"),
    ("OceaLeuc", "Oceanodroma leucorhoa"),
    ("EudyMino", "Eudyptula minor"),
    ("ColuLivi", "Columba livia"),
    ("EgreGarz", "Egretta garzetta"),
    ("ChroScop", "Chroicocephalus scopulinus"),
    ("PiprFili", "Pipra filicauda"),
    ("SpheMend", "Spheniscus mendiculus"),
    # Amphibians
    ("RhinMari", "Rhinella marina"),
    ("GeotSera", "Geotrypetes seraphini"),
    ("PeloCult", "Pelobates cultripes"),
    # Turtles
    ("GophEvgo", "Gopherus evgoodei"),
    # Mammals
    ("RhinFerr", "Rhinolophus ferrumequinum"),
    ("MyotLuci", "Myotis lucifugus"),
    ("VombUrsi", "Vombatus ursinus"),
    ("HippArmi", "Hipposideros armiger"),
    ("MyotBran", "Myotis brandtii"),
]


@pytest.mark.parametrize("prefix,latin", BATCH_SPECIES)
def test_batch_species_parse_by_prefix(prefix, latin):
    sp = Species.get(prefix)
    assert sp is not None, f"Species.get({prefix!r}) returned None"
    eq_(sp.name, latin)


@pytest.mark.parametrize("prefix,latin", BATCH_SPECIES)
def test_batch_species_parse_by_latin_name(prefix, latin):
    sp = Species.get(latin)
    assert sp is not None, f"Species.get({latin!r}) returned None"
    eq_(sp.prefix, prefix)


@pytest.mark.parametrize("prefix,latin", BATCH_SPECIES)
def test_batch_species_inherit_root_genes(prefix, latin):
    """Every new species should inherit DMA and TAP1 from Gnathostomata."""
    sp = Species.get(prefix)
    assert sp is not None
    assert sp.find_matching_gene_name("DMA") is not None, f"{latin} missing DMA"
    assert sp.find_matching_gene_name("TAP1") is not None, f"{latin} missing TAP1"


# --- Galliform inheritance ---


def test_pheasant_inherits_bf_from_galliformes():
    result = parse("PhasColc-BF", raise_on_error=True)
    eq_(result.species.name, "Phasianus colchicus")


def test_prairie_chicken_inherits_blb_from_galliformes():
    result = parse("Iibi-BLB", raise_on_error=True)
    eq_(result.species.name, "Tympanuchus cupido")


def test_pheasant_full_latin_name_works():
    result = parse("PhasianusColchicus-BF", raise_on_error=True)
    eq_(result.species.name, "Phasianus colchicus")


# --- Testudines inheritance ---


def test_gopherus_evgoodei_inherits_turtle_genes():
    sp = Species.get("Goev")
    assert sp.find_matching_gene_name("UA") is not None
    assert sp.find_matching_gene_name("DAB") is not None


# --- Cross-taxon leak prevention ---


def test_dove_does_not_get_galliform_bf():
    sp = Species.get("Columba livia")
    assert sp.find_matching_gene_name("BF") is None


def test_cobra_does_not_get_galliform_blb():
    sp = Species.get("Naja naja")
    assert sp.find_matching_gene_name("BLB") is None


def test_bat_does_not_get_fish_uaa():
    sp = Species.get("Myotis lucifugus")
    assert sp.find_matching_gene_name("UAA") is None


def test_toad_inherits_drb1_from_amphibia():
    """DRB1 is now on Amphibia — attested in amphibian MHC literature."""
    sp = Species.get("Rhinella marina")
    assert sp.find_matching_gene_name("DRB1") is not None


# --- species= strict parameter ---


def test_species_strict_dma_with_cobra():
    result = parse("DMA", species="Naja naja", raise_on_error=True)
    eq_(result.species.name, "Naja naja")


def test_species_strict_b2m_with_gecko():
    result = parse("B2M", species="Eublepharis macularius", raise_on_error=True)
    eq_(result.species.name, "Eublepharis macularius")


# --- Non-standard prefix edge cases ---


def test_arbr_prefix_for_roach():
    """Arbr is non-standard (old genus?) but attested in UniProt."""
    eq_(Species.get("Arbr").name, "Rutilus rutilus")


def test_pctn_prefix_for_softnose():
    eq_(Species.get("Pctn").name, "Parachondrostoma toxostoma")


def test_iibi_prefix_for_prairie_chicken():
    eq_(Species.get("Iibi").name, "Tympanuchus cupido")


def test_lasc_prefix_for_gull():
    """Lasc from old genus Larus, now Chroicocephalus."""
    eq_(Species.get("Lasc").name, "Chroicocephalus scopulinus")
