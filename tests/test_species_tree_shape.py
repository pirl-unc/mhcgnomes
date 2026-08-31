"""
Invariants about the shape of the species tree: what a parent link means, and
where the tree deliberately departs from taxonomy.

A parent link is containment, taxonomic wherever it can be, and it is what
genes are inherited along. Every MHC prefix owns a node, so "is a human a
primate?" and "can NHP-* name a human?" are both plain ancestry questions:
Primata sp. is the primate order and an ancestor of Homo sapiens, while NHP is
a sibling of Homo sapiens beneath it.

https://github.com/pirl-unc/mhcgnomes/issues/122
https://github.com/pirl-unc/mhcgnomes/issues/126
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


def test_nhp_is_a_sibling_of_human_not_an_ancestor():
    human = Species.get_by_latin_name("Homo sapiens")
    nhp = Species.get("NHP")
    ok_(not nhp.is_ancestor_of(human))
    ok_(not human.is_descendant_of(nhp))
    ok_(not human.compatible_with(nhp))
    ok_(not nhp.compatible_with(human))
    eq_(nhp.parent.name, "Primata sp.")


def test_nhp_covers_every_primate_except_human():
    primates = Species.get_by_latin_name("Primata sp.")
    nhp = Species.get("NHP")
    outside = sorted(
        s.name
        for s in ALL_SPECIES
        if primates.is_ancestor_of(s) and s is not nhp and not nhp.is_ancestor_of(s)
    )
    eq_(outside, ["Homo sapiens"], f"outside the NHP group: {outside}")


# Every gene the primate node owns, so that these exercise the species=
# conversion path rather than merely failing to find a gene.
NHP_GENES = ["E", "DMB", "MICA", "CD1a"]


@pytest.mark.parametrize("gene", NHP_GENES)
def test_nhp_gene_names_parse_as_the_nhp_node(gene):
    eq_(parse(f"NHP-{gene}").species.name, "NHP")


@pytest.mark.parametrize("gene", NHP_GENES)
@pytest.mark.parametrize("human_name", ["Homo sapiens", "HLA", "human"])
def test_nhp_gene_names_are_never_converted_to_human(gene, human_name):
    eq_(
        parse(f"NHP-{gene}", species=human_name, raise_on_error=False),
        None,
        f"'NHP-{gene}' was relabelled as {human_name}",
    )


def test_ancestor_to_descendant_conversion_still_works_where_it_should():
    # The structure must not have disabled the feature it constrains.
    eq_(parse("BoLA-N*01301", species="Bos taurus").species.name, "Bos taurus")


def test_nhp_prefix_belongs_to_the_nhp_node():
    eq_(Species.get("NHP"), Species.get_by_latin_name("NHP"))
    eq_(Species.get("primate"), Species.get_by_latin_name("Primata sp."))


def test_primata_prefix_is_its_own_taxon_name_and_is_not_inherited():
    # "Primata" is the node's taxon name, so the loader treats it the way it
    # treats "Aves" and "Rodentia": it is not handed down as an MHC prefix.
    primates = Species.get_by_latin_name("Primata sp.")
    eq_(primates.prefix, "Primata")
    inheritors = [
        s.name for s in ALL_SPECIES if s.historic_mhc_prefix == "Primata" and s is not primates
    ]
    eq_(inheritors, [], f"species that picked up 'Primata' as an MHC prefix: {inheritors}")


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
