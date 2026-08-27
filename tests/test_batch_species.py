"""
Tests for batch-added species from the mhcseqs P2/P5 requests.
Covers raptors, cranes, passerines, additional fish, amphibians,
sharks, tuatara, and taxonomy reclassifications.
"""

import pytest

from mhcgnomes import Gene, Species, parse

from .common import eq_

BATCH_SPECIES = [
    # Raptors
    ("Fape", "Falco peregrinus"),
    ("Fati", "Falco tinnunculus"),
    ("Aqch", "Aquila chrysaetos"),
    ("ButeoBute", "Buteo buteo"),
    ("Ciae", "Circus aeruginosus"),
    ("Gyfu", "Gyps fulvus"),
    # Cranes
    ("Grja", "Grus japonensis"),
    ("Anan", "Antigone antigone"),
    ("Bare", "Balearica regulorum"),
    # Passerines
    ("Pado", "Passer domesticus"),
    ("Coco", "Corvus cornix"),
    ("Tume", "Turdus merula"),
    ("Laco", "Lanius collurio"),
    ("Emci", "Emberiza citrinella"),
    # Shorebirds
    ("Anni", "Anarhynchus nivosus"),
    # Fish
    ("Gaac", "Gasterosteus aculeatus"),
    ("Icpu", "Ictalurus punctatus"),
    ("Hiab", "Hippocampus abdominalis"),
    ("Caau", "Carassius auratus"),
    ("Clma", "Clarias magur"),
    # Amphibians
    ("Lica", "Lithobates catesbeianus"),
    ("Licl", "Lithobates clamitans"),
    ("Amme", "Ambystoma mexicanum"),
    ("Amti", "Ambystoma tigrinum"),
    # Tuatara
    ("Sppu", "Sphenodon punctatus"),
    # Marsupial
    ("Noeu", "Notamacropus eugenii"),
    # Sharks
    ("Gici", "Ginglymostoma cirratum"),
    ("Hefr", "Heterodontus francisci"),
    ("Sqac", "Squalus acanthias"),
    ("Trsc", "Triakis scyllium"),
]


@pytest.mark.parametrize("prefix,latin", BATCH_SPECIES)
def test_batch_species_parseable(prefix, latin):
    species = Species.get(prefix)
    assert species is not None, f"Species.get({prefix!r}) returned None"
    eq_(species.name, latin)
    eq_(parse(prefix, raise_on_error=True), species)
    # Latin name should also work
    eq_(Species.get(latin), species)


# Taxonomy reclassification aliases
RECLASSIFICATION_ALIASES = [
    ("Gran", "Antigone antigone"),  # Grus → Antigone
    ("Chni", "Anarhynchus nivosus"),  # Charadrius → Anarhynchus
    ("Raca", "Lithobates catesbeianus"),  # Rana → Lithobates
    ("Racl", "Lithobates clamitans"),  # Rana → Lithobates
    ("Maeu", "Notamacropus eugenii"),  # Macropus → Notamacropus
]


@pytest.mark.parametrize("old_prefix,latin", RECLASSIFICATION_ALIASES)
def test_old_genus_prefix_resolves_to_current_species(old_prefix, latin):
    species = Species.get(old_prefix)
    assert species is not None, f"Old prefix {old_prefix!r} did not resolve"
    eq_(species.name, latin)


GAP_REPORT_SPECIES = [
    ("Anda", "Andrias davidianus", "UAA"),
    ("Geja", "Gekko japonicus", "DAA"),
    ("Spau", "Sparus aurata", "UAA"),
    ("Laca", "Lates calcarifer", "UAA"),
    ("Safa", "Salarias fasciatus", "UAA"),
    ("Acda", "Acipenser dabryanus", "UAA"),
    ("Pybi", "Python bivittatus", "DRA"),
    ("Poli", "Podarcis lilfordi", "DAA"),
    ("Miun", "Microcaecilia unicolor", "DAA"),
    ("Scsc", "Scomber scombrus", "UAA"),
    ("Stoc", "Strix occidentalis caurina", "DAB1"),
]


@pytest.mark.parametrize("prefix,latin,gene_name", GAP_REPORT_SPECIES)
def test_gap_report_species_parseable_with_example_gene(prefix, latin, gene_name):
    species = Species.get(prefix)
    assert species is not None, f"Species.get({prefix!r}) returned None"
    eq_(species.name, latin)
    eq_(Species.get(latin), species)

    gene = Gene.get(prefix, gene_name)
    assert gene is not None, f"Gene.get({prefix!r}, {gene_name!r}) returned None"
    eq_(parse(f"{prefix}-{gene_name}", raise_on_error=True), gene)


PROMOTED_PUBLISHED_PREFIX_ALIASES = [
    ("AndrDavi", "Anda", "UAA"),
    ("SparAura", "Spau", "UAA"),
    ("AcipDabr", "Acda", "UAA"),
]


@pytest.mark.parametrize(
    "legacy_prefix,canonical_prefix,gene_name", PROMOTED_PUBLISHED_PREFIX_ALIASES
)
def test_promoted_published_prefixes_keep_legacy_aliases(
    legacy_prefix, canonical_prefix, gene_name
):
    legacy_species = Species.get(legacy_prefix)
    canonical_species = Species.get(canonical_prefix)

    assert legacy_species is not None
    assert canonical_species is not None
    eq_(legacy_species, canonical_species)

    gene = Gene.get(canonical_prefix, gene_name)
    assert gene is not None
    eq_(parse(f"{legacy_prefix}-{gene_name}", raise_on_error=True), gene)


@pytest.mark.parametrize(
    "species_prefix,gene_name",
    [
        ("Fape", "DAA"),
        ("Fape", "DRA"),
        ("Aqch", "DRB"),
        ("Grja", "DAB"),
        ("Egga", "DAB1"),
        ("Egga", "DAB2"),
    ],
)
def test_cleaned_bird_clades_still_inherit_runtime_genes(species_prefix, gene_name):
    gene = Gene.get(species_prefix, gene_name)
    assert gene is not None, f"Gene.get({species_prefix!r}, {gene_name!r}) returned None"
    eq_(parse(f"{species_prefix}-{gene_name}", raise_on_error=True), gene)
