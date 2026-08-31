"""
Invariants about the shape of the species tree: what a parent link means, and
where the tree deliberately departs from taxonomy.

A parent link is containment, taxonomic wherever it can be, and it is what
genes are inherited along. Whether an ancestor's prefix may *name* a descendant
is a separate question, answered by Species.can_name and constrained by the
"prefix excludes" declaration -- which is why Homo sapiens can be a primate
without ever answering to NHP.

https://github.com/pirl-unc/mhcgnomes/issues/122
"""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.species import (
    latin_name_to_species_object,
    raw_allele_aliases_dict,
    raw_gene_aliases_dict,
    raw_haplotypes_dict,
    raw_heterodimers_dict,
    raw_known_alleles_dict,
    raw_serotypes_dict,
    raw_species_dict,
    raw_supertypes_dict,
)

from .common import eq_, ok_

ALL_SPECIES = sorted(latin_name_to_species_object.values(), key=lambda s: s.name)

# Nodes standing for a group rather than one species, indexed by the taxon they
# are named for: {"Bos": Species("Bos sp."), "Aves": Species("Aves sp."), ...}
GROUP_NODES = {s.name[: -len(" sp.")]: s for s in ALL_SPECIES if s.name.endswith(" sp.")}

# The genera that actually appear in a binomial, so that "Bos sp." is
# recognised as a genus node while "Aves sp." and "Primata sp." are not.
BINOMIAL_GENERA = {s.name.split()[0] for s in ALL_SPECIES if not s.name.endswith(" sp.")}

GENUS_NODES = {genus: node for genus, node in GROUP_NODES.items() if genus in BINOMIAL_GENERA}


# ---------------------------------------------------------------------------
# 1. Homo sapiens is a primate
# ---------------------------------------------------------------------------


def test_human_is_a_descendant_of_the_primate_node():
    human = Species.get_by_latin_name("Homo sapiens")
    primates = Species.get_by_latin_name("Primata sp.")
    ok_(human.is_descendant_of(primates))
    ok_(primates.is_ancestor_of(human))


def test_human_still_descends_from_the_root():
    human = Species.get_by_latin_name("Homo sapiens")
    ok_(human.is_descendant_of(Species.get_by_latin_name("Gnathostomata sp.")))


# ---------------------------------------------------------------------------
# 2. ...but is not in the NHP naming group
# ---------------------------------------------------------------------------
# "NHP" is the IPD-MHC group code for Non-Human Primates
# (https://www.ebi.ac.uk/ipd/mhc/group/NHP/), so it must never reach a human by
# any route: not as an inherited prefix, not through compatible_with, and not
# through the ancestor-to-descendant conversion that species= performs.


def test_human_does_not_inherit_the_nhp_prefix():
    human = Species.get_by_latin_name("Homo sapiens")
    eq_(human.historic_mhc_prefix, "HLA")
    ok_("NHP" not in human.all_mhc_prefixes)
    ok_("NHP" not in set(human.all_identifiers))


def test_the_primate_node_cannot_name_a_human():
    human = Species.get_by_latin_name("Homo sapiens")
    primates = Species.get_by_latin_name("Primata sp.")
    ok_(not primates.can_name(human))
    ok_(not human.compatible_with(primates))
    ok_(not primates.compatible_with(human))
    ok_(not human.compatible_with("NHP"))


def test_the_primate_node_can_still_name_every_other_primate():
    primates = Species.get_by_latin_name("Primata sp.")
    unnameable = [
        s.name
        for s in ALL_SPECIES
        if primates.is_ancestor_of(s) and s.name != "Homo sapiens" and not primates.can_name(s)
    ]
    eq_(unnameable, [], f"NHP stopped covering: {unnameable}")


def test_exclusion_does_not_leak_to_nodes_above_it():
    # Gnathostomata sp. does not exclude anything, so human stays reachable
    # from the root even though the path passes through the excluded edge.
    human = Species.get_by_latin_name("Homo sapiens")
    root = Species.get_by_latin_name("Gnathostomata sp.")
    ok_(root.can_name(human))
    ok_(human.compatible_with(root))


# Every gene `Primata sp.` owns, so that these exercise the conversion path
# rather than merely failing to find a gene. `species=` on the second column is
# the ancestor-to-descendant conversion that must be refused for NHP.
NHP_GENES = ["E", "DMB", "MICA", "CD1a"]


@pytest.mark.parametrize("gene", NHP_GENES)
def test_nhp_gene_names_parse_as_the_primate_node(gene):
    result = parse(f"NHP-{gene}")
    eq_(result.species.name, "Primata sp.")


@pytest.mark.parametrize("gene", NHP_GENES)
@pytest.mark.parametrize("human_name", ["Homo sapiens", "HLA", "human"])
def test_nhp_gene_names_are_never_converted_to_human(gene, human_name):
    eq_(
        parse(f"NHP-{gene}", species=human_name, raise_on_error=False),
        None,
        f"'NHP-{gene}' was relabelled as {human_name}",
    )


def test_ancestor_to_descendant_conversion_still_works_where_it_should():
    # The guard above must not have disabled the feature it constrains.
    result = parse("BoLA-N*01301", species="Bos taurus")
    eq_(result.species.name, "Bos taurus")


def test_nhp_prefix_still_belongs_to_the_primate_node():
    eq_(Species.get("NHP"), Species.get_by_latin_name("Primata sp."))


def test_every_other_primate_still_inherits_nhp():
    primates = Species.get_by_latin_name("Primata sp.")
    # Genus nodes inherit NHP too, despite carrying prefixes of their own:
    # Macaca sp. is RhLA *and* old prefix NHP. The only children that do not
    # are the two with a documented historic prefix, and human.
    declares_own_old_prefix = {"Callithrix pygmaea", "Semnopithecus entellus", "Homo sapiens"}
    lost = [
        s.name
        for s in ALL_SPECIES
        if s.parent is primates
        and s.name not in declares_own_old_prefix
        and s.historic_mhc_prefix != "NHP"
    ]
    eq_(lost, [], f"children of Primata sp. that lost the NHP umbrella: {lost}")


# ---------------------------------------------------------------------------
# 3. Reparenting must stay inert
# ---------------------------------------------------------------------------
# Gene *names* are only one of the things inherited along a parent link. Gene
# properties, gene families, class II locus groupings and seven side tables
# keyed by ancestor latin name all flow down too, so checking names alone would
# let a pseudogene flag on Primata sp. silently become one on HLA.

SIDE_TABLES = {
    "gene_aliases.yaml": raw_gene_aliases_dict,
    "allele_aliases.yaml": raw_allele_aliases_dict,
    "known_alleles.yaml": raw_known_alleles_dict,
    "haplotypes.yaml": raw_haplotypes_dict,
    "serotypes.yaml": raw_serotypes_dict,
    "heterodimers.yaml": raw_heterodimers_dict,
    "supertypes.yaml": raw_supertypes_dict,
}


def _declared_gene_names(entry):
    names = set()
    for members in entry.get("genes", {}).values():
        groups = members.values() if isinstance(members, dict) else [members]
        for group in groups:
            names.update(str(gene).upper() for gene in group)
    return names


def test_the_primate_node_declares_no_gene_hla_does_not():
    primates = raw_species_dict["Primata sp."]
    human = raw_species_dict["Homo sapiens"]
    missing = sorted(_declared_gene_names(primates) - _declared_gene_names(human))
    eq_(missing, [], f"HLA would inherit these genes without declaring them: {missing}")


@pytest.mark.parametrize("key", ["gene properties", "gene families"])
def test_the_primate_node_declares_no_metadata_hla_does_not(key):
    primates = raw_species_dict["Primata sp."].get(key) or {}
    human = {
        str(k).upper(): v for k, v in (raw_species_dict["Homo sapiens"].get(key) or {}).items()
    }
    mismatched = sorted(k for k, v in primates.items() if human.get(str(k).upper()) != v)
    eq_(mismatched, [], f"HLA would inherit '{key}' for {mismatched} without declaring it")


@pytest.mark.parametrize("filename,table", sorted(SIDE_TABLES.items()))
def test_the_primate_node_has_no_side_table_entries(filename, table):
    # These merge into every descendant by ancestor latin name, so a Primata
    # sp. entry lands in HLA wholesale. Adding one may well be right -- but it
    # has to be checked against IMGT/HLA for humans too, not just for monkeys.
    ok_(
        "Primata sp." not in table,
        f"{filename} now has a 'Primata sp.' entry, which HLA inherits; "
        f"confirm it is correct for humans before allowlisting it here",
    )


# ---------------------------------------------------------------------------
# 4. Where the tree departs from taxonomy
# ---------------------------------------------------------------------------

# The one parent link in the ontology that points at another genus's node.
# Water buffalo is Bubalus, not Bos, but IPD-MHC files it in the BoLA group and
# the literature assigns its class II sequences to cattle loci by trans-species
# polymorphism, so the edge is what makes Bubu-DRA and Bubu-DRB3 parse (#115).
GENUS_CROSSING_EDGES = {("Bubalus bubalis", "Bos sp.")}


def test_only_documented_edges_point_at_another_genus_node():
    # Ranks above genus (Aves sp., Primata sp.) legitimately hold many genera
    # and are not considered here; only nodes named for an actual genus are.
    crossing = {
        (species.name, species.parent.name)
        for species in ALL_SPECIES
        if species.parent is not None
        and species.parent is GENUS_NODES.get(species.parent.name[: -len(" sp.")])
        and not species.name.startswith(species.parent.name[: -len(" sp.")] + " ")
    }
    eq_(sorted(crossing), sorted(GENUS_CROSSING_EDGES))


# Species that sit at a higher node even though their own genus has one. These
# are curation gaps rather than decisions: reparenting them would hand them the
# genus gene list, which needs its own check against the literature.
# https://github.com/pirl-unc/mhcgnomes/issues/123
UNPLACED_WITHIN_GENUS = {
    "Callithrix pygmaea",
    "Macaca arctoides",
    "Macaca assamensis",
    "Macaca fuscata",
    "Macaca leonina",
}


def test_species_sit_under_their_genus_node_when_one_exists():
    unplaced = {
        species.name
        for species in ALL_SPECIES
        if not species.name.endswith(" sp.")
        and species.name.split()[0] in GENUS_NODES
        and not GENUS_NODES[species.name.split()[0]].is_ancestor_of(species)
    }
    eq_(sorted(unplaced), sorted(UNPLACED_WITHIN_GENUS))
