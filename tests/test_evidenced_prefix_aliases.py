"""
Prefix spellings attested in an external database or the literature.

Imported from the sibling mhcseqs registry, with the evidence URL kept per
(species, alias) rather than per species -- one species can have current,
historical and database spellings from different sources.

Whether an alias is globally parseable or context-only is computed at load
time from how many species claim it, so it cannot go stale as species are
added.

https://github.com/pirl-unc/mhcgnomes/issues/136
"""

from pathlib import Path

import pytest
import yaml

from mhcgnomes import Species, parse
from mhcgnomes.species import (
    EVIDENCED_CONTEXT_ONLY_ALIASES,
    EVIDENCED_GLOBAL_ALIASES,
    _blocked_registry_prefixes,
    find_matching_context_only_species_objects,
)

from .common import eq_, ok_

ALIASES_PATH = Path(__file__).parent.parent / "mhcgnomes" / "data" / "evidenced_prefix_aliases.yaml"
REGISTRY = yaml.safe_load(ALIASES_PATH.read_text())


def test_every_row_carries_an_evidence_url():
    """
    Requirement 1 of the model in #136: import only what is cited. This is the
    one property that cannot be recovered later if it is skipped.
    """
    uncited = [
        (species, entry["alias"])
        for species, entries in REGISTRY.items()
        for entry in entries
        if not str(entry.get("evidence", "")).startswith("http")
    ]
    eq_(uncited, [], f"evidenced aliases with no source: {uncited}")


def test_every_row_names_a_species_we_have():
    missing = sorted({s for s in REGISTRY if Species.get_by_latin_name(s) is None})
    eq_(missing, [], f"aliases for species absent from the ontology: {missing}")


# The examples #136 lists as absent source spellings.
NEWLY_RESOLVABLE = [
    ("Acsi", "Acipenser sinensis"),
    ("GPLA", "Cavia porcellus"),
    ("XLA", "Xenopus laevis"),
]


@pytest.mark.parametrize("alias,latin_name", NEWLY_RESOLVABLE)
def test_an_uncontested_attested_spelling_resolves(alias, latin_name):
    species = Species.get(alias)
    assert species is not None, f"{alias!r} still resolves to nothing"
    eq_(species.name, latin_name)


# The collisions #136 lists: (alias, the species that keeps it as its prefix,
# a newly evidenced claimant that gets it context-only instead).
CONTESTED = [
    ("Bubu", "Bubalus bubalis", "Bubo bubo"),
    ("Cyca", "Cyprinus carpio", "Cyanistes caeruleus"),
    ("Cyca", "Cyprinus carpio", "Clarias magur"),
]


@pytest.mark.parametrize("alias,keeps_it,context_only_claimant", CONTESTED)
def test_a_contested_spelling_is_context_only(alias, keeps_it, context_only_claimant):
    """
    The owner is unaffected -- an attested spelling elsewhere does not take a
    prefix away from the species that already uses it.
    """
    eq_(Species.get(alias).name, keeps_it)
    claimants = {s.name for s in find_matching_context_only_species_objects(alias)}
    ok_(
        context_only_claimant in claimants,
        f"{context_only_claimant} does not carry {alias!r} as context-only",
    )
    ok_(keeps_it not in claimants, f"{keeps_it} should own {alias!r}, not hold it context-only")


def test_context_only_is_recoverable_with_an_explicit_species():
    """The point of the bucket: the published record is still reachable."""
    result = parse("UAA", species="Bubo bubo", raise_on_error=True)
    eq_(result.species.name, "Bubo bubo")


def test_multi_claimant_aliases_are_never_global():
    """
    An alias two species can cite must not silently pick one. Computed from
    claimant count rather than curated, so adding a species cannot leave a
    stale decision behind.
    """
    claim_count = {}
    for entries in REGISTRY.values():
        for entry in entries:
            claim_count[entry["alias"].lower()] = claim_count.get(entry["alias"].lower(), 0) + 1
    for aliases in EVIDENCED_GLOBAL_ALIASES.values():
        for alias in aliases:
            eq_(claim_count[alias.lower()], 1, f"{alias!r} is global despite multiple claimants")


def test_the_curation_holdback_is_respected():
    """
    `underrepresented_taxa_source_registry.yaml` keeps prefixes out of runtime
    deliberately. An attested source spelling does not override that -- Otel,
    Phco and Phtr are blocked there, and tests/test_birds.py asserts they do
    not parse.
    """
    blocked = _blocked_registry_prefixes()
    ok_(blocked, "expected some blocked prefixes in the registry")
    imported = {a.lower() for v in EVIDENCED_GLOBAL_ALIASES.values() for a in v}
    imported |= {a.lower() for v in EVIDENCED_CONTEXT_ONLY_ALIASES.values() for a in v}
    leaked = sorted(imported & blocked)
    eq_(leaked, [], f"blocked prefixes imported anyway: {leaked}")


@pytest.mark.parametrize("name", ["Otel-DAB", "Phtr-UA", "Phco-UA"])
def test_blocked_bird_prefixes_still_do_not_parse(name):
    eq_(parse(name, raise_on_error=False), None)


def test_very_short_aliases_are_not_imported_globally():
    """
    "B" is real chicken nomenclature (B-F, B-L), but as a bare species prefix
    it shadows the mouse haplotype b and `b/d` stops parsing. Same reason the
    single-letter HLA fragments stay out of unprefixed resolution (#113).
    """
    too_short = [a for v in EVIDENCED_GLOBAL_ALIASES.values() for a in v if len(a) < 3]
    eq_(too_short, [], f"aliases too short to be a species prefix: {too_short}")
    eq_(parse("b/d", raise_on_error=True).species.name, "Mus musculus")
