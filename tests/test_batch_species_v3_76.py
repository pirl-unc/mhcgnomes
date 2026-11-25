"""Tests for the 66 vertebrate species added for mhcseqs coverage (#277)."""

import pytest

from mhcgnomes import Species, parse

from .common import eq_, ok_

ADDED_SPECIES = [
    ("Spermophilus dauricus", "SperDaur", 99837, "other_mammal"),
    ("Apodemus speciosus", "ApodSpec", 105296, "murine"),
    ("Apodemus agrarius", "ApodAgra", 39030, "murine"),
    ("Neotoma lepida", "NeotLepi", 56216, "other_mammal"),
    ("Sciurus carolinensis", "SciuCaro", 30640, "other_mammal"),
    ("Sciurus aberti", "SciuAber", 10007, "other_mammal"),
    ("Peromyscus eremicus", "PeroErem", 42410, "other_mammal"),
    ("Peromyscus pectoralis", "PeroPect", 97213, "other_mammal"),
    ("Peromyscus attwateri", "PeroAttw", 97206, "other_mammal"),
    ("Tokudaia muenninki", "TokuMuen", 742503, "murine"),
    ("Tokudaia osimensis", "TokuOsim", 73109, "murine"),
    ("Diplothrix legata", "DiplLega", 106283, "murine"),
    ("Hybomys univittatus", "HyboUniv", 71162, "murine"),
    ("Nannospalax ehrenbergi", "NannEhre", 30637, "other_mammal"),
    ("Octodon sp.", "Octodon", 169034, "other_mammal"),
    ("Isoodon macrourus", "IsooMacr", 37698, "marsupial"),
    ("Carpodacus erythrinus", "CarpEryt", 175930, "bird"),
    ("Parus monticolus", "ParuMont", 156542, "bird"),
    ("Aphelocoma coerulescens", "ApheCoer", 39617, "bird"),
    ("Alcedo atthis", "AlceAtth", 36245, "bird"),
    ("Calidris pugnax", "CaliPugn", 198806, "bird"),
    ("Hydrobates castro", "HydrCast", 126871, "bird"),
    ("Oceanodroma monteiroi", "OceaMont", 1200804, "bird"),
    ("Pagophila eburnea", "PagoEbur", 126721, "bird"),
    ("Ciconia ciconia", "CicoCico", 8928, "bird"),
    ("Procellaria aequinoctialis", "ProcAequ", 53665, "bird"),
    ("Tauraco hartlaubi", "TaurHart", 56304, "bird"),
    ("Bulweria bulwerii", "BulwBulw", 52120, "bird"),
    ("Calonectris diomedea", "CaloDiom", 52122, "bird"),
    ("Pachyptila desolata", "PachDeso", 79635, "bird"),
    ("Pagodroma nivea", "PagoNive", 52126, "bird"),
    ("Acrocephalus sechellensis", "AcroSech", 68481, "bird"),
    ("Tachymarptis melba", "TachMelb", 670359, "bird"),
    ("Dendrocopos major", "DendMajo", 183177, "bird"),
    ("Diomedea exulans", "DiomExul", 46550, "bird"),
    ("Haemorhous mexicanus", "HaemMexi", 30427, "bird"),
    ("Anser anser", "AnseAnse", 8843, "bird"),
    ("Rallus aquaticus", "RallAqua", 54496, "bird"),
    ("Jynx torquilla", "JynxTorq", 189526, "bird"),
    ("Philetairus socius", "PhilSoci", 247666, "bird"),
    ("Crithagra citrinelloides", "CrithagraCitrinelloides", 2546078, "bird"),
    ("Crithagra citrinipectus", "CrithagraCitrinipectus", 3149685, "bird"),
    ("Crithagra dorsostriata", "CritDors", 163845, "bird"),
    ("Crithagra flaviventris", "CritFlav", 163847, "bird"),
    ("Crithagra mozambica", "CritMoza", 1892170, "bird"),
    ("Serinus citrinella", "SeriCitr", 632108, "bird"),
    ("Serinus atrogularis", "SeriAtro", 3149682, "bird"),
    ("Serinus thibetanus", "SeriThib", 163846, "bird"),
    ("Serinus striolatus", "SeriStri", 3149701, "bird"),
    ("Serinus gularis", "SeriGula", 3149689, "bird"),
    ("Spinus psaltria", "SpinPsal", 54559, "bird"),
    ("Spinus dominicensis", "SpinDomi", 175929, "bird"),
    ("Spinus atriceps", "SpinAtri", 175928, "bird"),
    ("Spinus lawrencei", "SpinLawr", 285242, "bird"),
    ("Nerodia sipedon", "NeroSipe", 8592, "reptile"),
    ("Crocodylus novaeguineae", "CrocNova", 8503, "reptile"),
    ("Perca fluviatilis", "PercFluv", 8168, "bony_fish"),
    ("Sander vitreus", "SandVitr", 283036, "bony_fish"),
    ("Knipowitschia caucasica", "KnipCauc", 637954, "bony_fish"),
    ("Acipenser baerii", "AcipBaer", 27689, "bony_fish"),
    ("Plecoglossus altivelis", "PlecAlti", 61084, "bony_fish"),
    ("Osmerus mordax", "OsmeMord", 8014, "bony_fish"),
    ("Lutjanus peru", "LutjPeru", 290247, "bony_fish"),
    ("Bagarius yarrelli", "BagaYarr", 175774, "bony_fish"),
    ("Anoplopoma fimbria", "AnopFimb", 229290, "bony_fish"),
    ("Takifugu rubripes", "TakiRubr", 31033, "bony_fish"),
]


@pytest.mark.parametrize("latin_name,prefix,taxid,clade", ADDED_SPECIES)
def test_added_species_resolve_with_verified_taxonomy(latin_name, prefix, taxid, clade):
    from mhcgnomes.prefix_display_policy import CURATED, prefix_display_policy

    sp = Species.get(latin_name)
    assert sp is not None, f"Species.get({latin_name!r}) returned None"
    eq_(sp.name, latin_name)
    eq_(sp.canonical_mhc_prefix, prefix)
    with prefix_display_policy(CURATED):
        eq_(sp.prefix, prefix)
    eq_(sp.ncbi_taxid, taxid)
    eq_(sp.clade, clade)
    eq_(Species.get_by_ncbi_taxid(taxid), sp)
    eq_(Species.get(prefix), sp)


def test_added_synonyms_and_uniprot_variants():
    eq_(Species.get("Oceanodroma castro"), Species.get("Hydrobates castro"))
    eq_(
        Species.get("Oceanodroma castro (Band-rumped storm-petrel) (Hydrobates castro)"),
        Species.get("Hydrobates castro"),
    )
    eq_(Species.get("OceanodromaCastro"), Species.get("Hydrobates castro"))

    eq_(Species.get("Spalax ehrenbergi"), Species.get("Nannospalax ehrenbergi"))
    eq_(Species.get("SpalaxEhrenbergi"), Species.get("Nannospalax ehrenbergi"))

    eq_(Species.get("Fugu rubripes"), Species.get("Takifugu rubripes"))
    eq_(Species.get("FuguRubripes"), Species.get("Takifugu rubripes"))

    eq_(Species.get("Octodon sp"), Species.get("Octodon sp."))
    eq_(Species.get("OctodonSp"), Species.get("Octodon sp."))
    ok_(Species.get("Octodon degus").is_child_of("Octodon sp."))


def test_colliding_crithagra_4_4_is_withheld():
    assert Species.get("CritCitr") is None
    eq_(
        parse("CrithagraCitrinelloides-DAB1").species.name,
        "Crithagra citrinelloides",
    )
    eq_(
        parse("CrithagraCitrinipectus-DAB1").species.name,
        "Crithagra citrinipectus",
    )
