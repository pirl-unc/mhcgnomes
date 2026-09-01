"""
An identifier shared by a node and its own descendants names the node.

`Species.get` walks a ladder when an alias has several claimants: exact latin
name, exact primary prefix, then -- per its own comment -- "the species that
isn't a subspecies (no parent with same identifier)". The code tested
`sp.parent_species is None`, which means "has no parent at all", so it only
ever fired for root entries.

Umbrella *prefixes* were unaffected because they are settled a step earlier:
"MusSp" is Mus sp.'s own prefix. A shared *common name* has no such step, so
"tropheus cichlid" -- Tropheus sp. and Tropheus moorii beneath it -- returned
None, while `parse("tropheus cichlid class I")` happily answered Tropheus sp.
The public lookup disagreed with the parser about the same string.

https://github.com/pirl-unc/mhcgnomes/issues/129
"""

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.species import latin_name_to_species_object

from .common import eq_, ok_

# (alias, the ancestor that should win)
SHARED_WITH_DESCENDANTS = [
    ("tropheus cichlid", "Tropheus sp."),
    ("swordtail", "Xiphophorus sp."),
    ("MusSp", "Mus sp."),
]


@pytest.mark.parametrize("alias,expected", SHARED_WITH_DESCENDANTS)
def test_the_containing_node_wins(alias, expected):
    got = Species.get(alias)
    ok_(got is not None, f"{alias!r} still resolves to nothing")
    eq_(got.name, expected)


@pytest.mark.parametrize("alias,expected", SHARED_WITH_DESCENDANTS)
def test_the_lookup_agrees_with_the_parser(alias, expected):
    """The disagreement is the bug; the value they agree on is secondary."""
    parsed = parse(f"{alias} class I")
    eq_(parsed.species.name, expected)
    eq_(Species.get(alias).name, parsed.species.name)


@pytest.mark.parametrize("alias,expected", SHARED_WITH_DESCENDANTS)
def test_the_winner_really_does_contain_the_others(alias, expected):
    claimants = Species.get_multiple(alias)
    ok_(len(claimants) > 1, f"{alias!r} is no longer shared; pick another example")
    winner = Species.get_by_latin_name(expected)
    for other in claimants:
        ok_(
            other is winner or winner.is_ancestor_of(other),
            f"{winner.name} is not an ancestor of {other.name}",
        )


def test_no_alias_in_the_ontology_has_unrelated_claimants():
    """
    Why the step is safe today: every multi-claimant alias is a node plus its
    own descendants. #112 and #134 moved the genuinely contested strings --
    Caau, Hyam, Moal, Orla and the rest -- to `context only prefixes`, so they
    have one ordinary claimant each and are reachable only with species=.

    If this ever fails, an alias has been given to two unrelated species and
    the ladder below will resolve it to nothing, silently.
    """
    from mhcgnomes.species import alias_to_species_objects

    unrelated = []
    for alias, holders in alias_to_species_objects.items():
        claimants = list(holders)
        if len(claimants) < 2:
            continue
        if any(all(o is s or s.is_ancestor_of(o) for o in claimants) for s in claimants):
            continue
        unrelated.append((str(alias), sorted(s.name for s in claimants)))
    eq_(unrelated, [], f"aliases claimed by unrelated species: {unrelated[:5]}")


def test_unrelated_claimants_would_still_be_refused():
    """
    The branch the test above leaves unexercised. Built rather than borrowed,
    because relying on data that no longer collides is how a guard rots.
    """
    from mhcgnomes.species import _containing_species

    human = Species.get_by_latin_name("Homo sapiens")
    chicken = Species.get_by_latin_name("Gallus gallus")
    primates = Species.get_by_latin_name("Primata sp.")

    ok_(not human.is_ancestor_of(chicken) and not chicken.is_ancestor_of(human))
    eq_(_containing_species([human, chicken]), None)

    # and the shape that does resolve
    eq_(_containing_species([primates, human]), primates)
    eq_(_containing_species([human]), human)


def test_every_identifier_resolves_to_its_owner_or_a_containing_ancestor():
    """
    The sweep that found this. An identifier must never resolve to a species
    unrelated to the one advertising it.
    """
    wrong = []
    for latin_name, species in latin_name_to_species_object.items():
        for identifier in set(species.all_identifiers):
            got = Species.get(identifier)
            if got is None or got.name == latin_name:
                continue
            if not got.is_ancestor_of(species):
                wrong.append((latin_name, str(identifier), got.name))
    eq_(wrong, [], f"identifiers resolving to an unrelated species: {wrong[:5]}")
