from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import pytest
import yaml

from mhcgnomes import Species, parse
from mhcgnomes.mhc_class_helpers import class1_restrictions, class2_restrictions

from .common import eq_

ROOT = Path(__file__).resolve().parents[1]
RAW_SPECIES = yaml.safe_load((ROOT / "mhcgnomes" / "data" / "species.yaml").read_text())

CLEANED_CETACEAN_SPECIES = [
    "Balaenoptera musculus",
    "Balaenoptera acutorostrata",
    "Balaenoptera edeni",
    "Cephalorhynchus hectori",
    "Delphinus delphis",
    "Eubalaena australis",
    "Globicephala melas",
    "Grampus griseus",
    "Kogia breviceps",
    "Lagenorhynchus obscurus",
    "Mesoplodon densirostris",
    "Mesoplodon europaeus",
    "Mesoplodon grayi",
    "Megaptera novaeangliae",
    "Steno bredanensis",
    "Stenella coeruleoalba",
    "Tursiops truncatus",
    "Ziphius cavirostris",
]

CLEANED_OWL_SPECIES = [
    "Aegolius funereus",
    "Asio flammeus",
    "Asio otus",
    "Athene noctua",
    "Bubo africanus",
    "Bubo bubo",
    "Bubo scandiacus",
    "Glaucidium passerinum",
    "Otus scops",
    "Strix aluco",
    "Strix nebulosa",
    "Strix uralensis",
    "Surnia ulula",
    "Tyto alba",
]


def _flatten_gene_names(genes):
    result = set()
    for members in (genes or {}).values():
        if isinstance(members, list):
            result.update(str(gene) for gene in members)
        elif isinstance(members, dict):
            for genes_for_locus in members.values():
                result.update(str(gene) for gene in genes_for_locus)
    return result


@lru_cache(None)
def _explicit_gene_names(latin_name):
    return _flatten_gene_names(RAW_SPECIES[latin_name].get("genes"))


@lru_cache(None)
def _all_gene_names(latin_name):
    return _inherited_gene_names(latin_name) | _explicit_gene_names(latin_name)


@lru_cache(None)
def _inherited_gene_names(latin_name):
    parent = RAW_SPECIES[latin_name].get("parent")
    if not parent and latin_name != "Gnathostomata sp.":
        parent = "Gnathostomata sp."
    if not parent:
        return set()
    return _all_gene_names(parent)


def test_manual_species_prefixes_are_unique():
    prefix_to_species = defaultdict(set)
    for latin_name, info in RAW_SPECIES.items():
        prefix_to_species[info["prefix"].lower()].add(latin_name)
        other_prefixes = info.get("other prefixes") or []
        if isinstance(other_prefixes, str):
            other_prefixes = [other_prefixes]
        for prefix in other_prefixes:
            prefix_to_species[str(prefix).lower()].add(latin_name)

    collisions = {
        prefix: sorted(species_names)
        for prefix, species_names in prefix_to_species.items()
        if len(species_names) > 1
    }
    assert not collisions, collisions


def test_class2_blocks_do_not_use_reserved_class_names_as_loci():
    reserved_locus_names = set(class1_restrictions) | set(class2_restrictions) | {"other"}
    bad_entries = []

    for latin_name, info in RAW_SPECIES.items():
        for mhc_class, members in info.get("genes", {}).items():
            if mhc_class not in class2_restrictions:
                continue
            assert isinstance(members, dict), (latin_name, mhc_class, type(members))
            for locus_name, genes_for_locus in members.items():
                if locus_name in reserved_locus_names:
                    bad_entries.append((latin_name, mhc_class, locus_name))
                assert genes_for_locus == {} or isinstance(genes_for_locus, list), (
                    latin_name,
                    mhc_class,
                    locus_name,
                    type(genes_for_locus),
                )

    assert not bad_entries, bad_entries


@pytest.mark.parametrize(
    "latin_name",
    [
        "Placentalia sp.",
        "Cetacea sp.",
        "Felis sp.",
        "Ovis sp.",
        "Capra sp.",
        "Mus sp.",
        "Rattus sp.",
        "Oryctolagus sp.",
    ],
)
def test_selected_shared_nodes_do_not_repeat_inherited_genes(latin_name):
    duplicate_genes = _explicit_gene_names(latin_name) & _inherited_gene_names(latin_name)
    assert not duplicate_genes, (latin_name, sorted(duplicate_genes))


def test_cleaned_cetacean_and_owl_species_do_not_redeclare_only_inherited_genes():
    redundant_children = []
    for latin_name in CLEANED_CETACEAN_SPECIES + CLEANED_OWL_SPECIES:
        explicit = _explicit_gene_names(latin_name)
        if explicit and explicit <= _inherited_gene_names(latin_name):
            redundant_children.append(latin_name)

    assert not redundant_children, redundant_children


def test_goat_tap_helper_genes_stay_in_other_class():
    goat = Species.get("CLA")
    assert goat is not None
    for gene in ["TAP1", "TAP2", "TAPBP", "B2M"]:
        eq_(goat.gene_name_to_mhc_class[gene], "other")


def test_lanius_species_have_distinct_prefixes():
    eq_(Species.get("LaniColl").name, "Lanius collurio")
    eq_(Species.get("LaniCola").name, "Lanius collaris")

    collurio = parse("LaniColl-DAB1", raise_on_error=True)
    collaris = parse("LaniCola-DAB1", raise_on_error=True)
    eq_(collurio.species.name, "Lanius collurio")
    eq_(collaris.species.name, "Lanius collaris")


@pytest.mark.parametrize(
    "raw,expected_species,expected_gene",
    [
        ("Aefu-DAB1", "Aegolius funereus", "DAB1"),
        ("Tyal-DAB2", "Tyto alba", "DAB2"),
        ("BuboBubo-DAB1", "Bubo bubo", "DAB1"),
    ],
)
def test_owl_species_inherit_shared_dab_genes(raw, expected_species, expected_gene):
    result = parse(raw, raise_on_error=True)
    eq_(result.species.name, expected_species)
    eq_(result.name, expected_gene)


@pytest.mark.parametrize(
    "raw,expected_species,expected_gene",
    [
        ("Bamu-DQA", "Balaenoptera musculus", "DQA"),
        ("Baac-S", "Balaenoptera acutorostrata", "S"),
        ("Tutr-N", "Tursiops truncatus", "N"),
        ("Zica-DRB1", "Ziphius cavirostris", "DRB1"),
    ],
)
def test_cetacean_species_inherit_shared_core(raw, expected_species, expected_gene):
    result = parse(raw, raise_on_error=True)
    eq_(result.species.name, expected_species)
    eq_(result.name, expected_gene)
