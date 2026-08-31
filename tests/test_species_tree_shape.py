"""
Invariants about the shape of the species tree: what a parent link means, and
where the tree deliberately departs from taxonomy.

A parent link is containment, and it is taxonomic wherever it can be. The
umbrella MHC prefix is a *separate*, opt-out-able property of a node, which is
why Homo sapiens can be a primate without answering to NHP.

https://github.com/pirl-unc/mhcgnomes/issues/122
"""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.species import latin_name_to_species_object

from .common import eq_, ok_

ALL_SPECIES = sorted(latin_name_to_species_object.values(), key=lambda s: s.name)

GENUS_NODES = {s.name[: -len(" sp.")]: s for s in ALL_SPECIES if s.name.endswith(" sp.")}


# ---------------------------------------------------------------------------
# 1. Homo sapiens is a primate
# ---------------------------------------------------------------------------


def test_human_is_a_descendant_of_the_primate_node():
    human = Species.get_by_latin_name("Homo sapiens")
    primates = Species.get_by_latin_name("Primata sp.")
    ok_(human.is_descendant_of(primates))
    ok_(primates.is_ancestor_of(human))
    ok_(human.compatible_with(primates))
    ok_(primates.compatible_with(human))


def test_human_still_descends_from_the_root():
    human = Species.get_by_latin_name("Homo sapiens")
    ok_(human.is_descendant_of(Species.get_by_latin_name("Gnathostomata sp.")))


# ---------------------------------------------------------------------------
# 2. ...but is not in the NHP naming group
# ---------------------------------------------------------------------------
# "NHP" is the IPD-MHC group code for Non-Human Primates
# (https://www.ebi.ac.uk/ipd/mhc/group/NHP/), so it must never reach a human.


def test_human_does_not_inherit_the_nhp_prefix():
    human = Species.get_by_latin_name("Homo sapiens")
    eq_(human.historic_mhc_prefix, "HLA")
    ok_("NHP" not in human.all_mhc_prefixes)
    ok_("NHP" not in set(human.all_identifiers))


# What each NHP string resolves to today. None means "does not parse"; the point
# of listing the resolutions rather than only asserting "not human" is that a
# string which silently stopped parsing would otherwise pass this test.
NHP_STRINGS = [
    ("NHP", "Primata sp."),
    ("NHP class I", "Primata sp."),
    ("NHP class II", "Primata sp."),
    ("NHP-A*01:01", None),
    ("NHP-DRB1*03:01", None),
]


@pytest.mark.parametrize("name,expected", NHP_STRINGS)
def test_nhp_strings_never_resolve_to_human(name, expected):
    result = parse(name, raise_on_error=False)
    if expected is None:
        eq_(result, None, f"'{name}' now parses as {result}")
        return
    species = result if isinstance(result, Species) else result.species
    eq_(species.name, expected)
    ok_(
        not species.is_human,
        f"'{name}' resolved to {species.name} through the non-human-primate prefix",
    )


def test_nhp_prefix_still_belongs_to_the_primate_node():
    eq_(Species.get("NHP"), Species.get_by_latin_name("Primata sp."))


def test_every_other_primate_still_inherits_nhp():
    primates = Species.get_by_latin_name("Primata sp.")
    # Children with an umbrella prefix of their own (a genus node, or a
    # documented historic prefix) legitimately do not inherit NHP.
    declares_own_old_prefix = {"Callithrix pygmaea", "Semnopithecus entellus", "Homo sapiens"}
    inherited = [
        s.name
        for s in ALL_SPECIES
        if s.parent is primates
        and s.name not in declares_own_old_prefix
        and s.historic_mhc_prefix != "NHP"
    ]
    eq_(inherited, [], f"children of Primata sp. that lost the NHP umbrella: {inherited}")


# ---------------------------------------------------------------------------
# 3. Reparenting must stay inert for gene inheritance
# ---------------------------------------------------------------------------


def test_human_declares_every_gene_it_inherits_from_the_primate_node():
    """
    Homo sapiens gains nothing by being parented under Primata sp.: it already
    declares all sixteen genes that node owns. If a primate-wide gene is ever
    added that humans do not declare, this fails and the addition has to be
    thought about rather than silently landing in HLA.
    """
    human = Species.get_by_latin_name("Homo sapiens")
    primates = Species.get_by_latin_name("Primata sp.")
    own = {g.upper() for g in human.own_gene_names}
    missing = sorted(g for g in primates.own_gene_names if g.upper() not in own)
    eq_(missing, [], f"HLA would inherit these from Primata sp. without declaring them: {missing}")


# ---------------------------------------------------------------------------
# 4. Where the tree departs from taxonomy
# ---------------------------------------------------------------------------

# The one parent link in the ontology that crosses a genus boundary. Water
# buffalo is Bubalus, not Bos, but IPD-MHC files it in the BoLA group and the
# literature assigns its class II sequences to cattle loci by trans-species
# polymorphism, so the edge is what makes Bubu-DRA and Bubu-DRB3 parse (#115).
GENUS_CROSSING_EDGES = {("Bubalus bubalis", "Bos sp.")}


def test_only_documented_edges_cross_a_genus_boundary():
    crossing = set()
    for species in ALL_SPECIES:
        parent = species.parent
        if parent is None or not parent.name.endswith(" sp."):
            continue
        genus = parent.name[: -len(" sp.")]
        if " " in genus or not genus[0].isupper():
            continue
        # Only genus-level nodes constrain their children's genus; ranks above
        # genus (Aves sp., Primata sp.) legitimately hold many genera.
        if genus not in {s.name.split()[0] for s in ALL_SPECIES if not s.name.endswith(" sp.")}:
            continue
        if not species.name.startswith(genus + " "):
            crossing.add((species.name, parent.name))
    eq_(sorted(crossing), sorted(GENUS_CROSSING_EDGES))


# Species that sit at the primate node even though their own genus has a node.
# These are curation gaps rather than decisions: reparenting them would hand
# them the genus gene list, which needs its own check against the literature.
# https://github.com/pirl-unc/mhcgnomes/issues/123
UNPLACED_WITHIN_GENUS = {
    "Callithrix pygmaea",
    "Macaca arctoides",
    "Macaca assamensis",
    "Macaca fuscata",
    "Macaca leonina",
}


def test_species_sit_under_their_genus_node_when_one_exists():
    unplaced = set()
    for species in ALL_SPECIES:
        if species.name.endswith(" sp."):
            continue
        node = GENUS_NODES.get(species.name.split()[0])
        if node is None or node.is_ancestor_of(species):
            continue
        unplaced.add(species.name)
    eq_(sorted(unplaced), sorted(UNPLACED_WITHIN_GENUS))
