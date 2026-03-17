"""
Tests for batch-added species from the mhcseqs P2/P5 requests.
Covers raptors, cranes, passerines, additional fish, amphibians,
sharks, tuatara, and taxonomy reclassifications.
"""

import pytest

from mhcgnomes import Species, parse

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
