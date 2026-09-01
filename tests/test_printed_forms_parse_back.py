"""
Every string this package prints, it must also accept.

That invariant was never tested, and 148 corpus names violated it. All were
CD1: `Gene.to_string` renders class `Id` genes with the common species name,
and the parser could not read those names back.

Two separate causes, both now fixed:

  1. The species matcher tried at most three leading tokens, so the 41 common
     names longer than that were unreachable (#178).
  2. `normalize_string` *deletes* hyphens, so "long-haired rat" is stored as
     LONGHAIRED RAT while the parser, joining tokens with a space, asks for
     LONG HAIRED RAT. Hyphenated multi-word names were unreachable however wide
     the window.

The round-trip test is the durable part -- whichever way the CD1 branch is
settled later, printing something unparseable should fail here first.

https://github.com/pirl-unc/mhcgnomes/issues/177
"""

import pytest

from mhcgnomes import parse
from mhcgnomes.species import latin_name_to_species_object

from .common import eq_, ok_

# CD1 is the family that exposed this, because it is the one printed with the
# common species name rather than a prefix.
CD1_GENES = ["CD1a", "CD1b", "CD1c", "CD1d", "CD1e"]

CD1_CASES = sorted(
    {
        (species.prefix, gene_name)
        for species in latin_name_to_species_object.values()
        for gene_name in CD1_GENES
        if gene_name.upper() in {name.upper() for name in species.gene_names}
    }
)


def test_there_are_cd1_cases_to_check():
    ok_(len(CD1_CASES) > 100, f"only {len(CD1_CASES)} CD1 forms found; did the ontology change?")


@pytest.mark.parametrize("prefix,gene_name", CD1_CASES)
def test_a_printed_cd1_form_parses_back(prefix, gene_name):
    printed = parse(f"{prefix}-{gene_name}").to_string()
    reparsed = parse(printed, raise_on_error=False)
    ok_(reparsed is not None, f"{prefix}-{gene_name} prints {printed!r}, which does not parse")
    eq_(reparsed.to_string(), printed)


@pytest.mark.parametrize(
    "text,expected",
    [
        # a hyphen inside the first word, which no window width could reach
        ("long-haired rat-CD1a", "long-haired rat-CD1a"),
        ("RattVill-CD1a", "long-haired rat-CD1a"),
        # and the same name written without the hyphen
        ("long haired rat class I", "long-haired rat class I"),
        # four words with a hyphen and an apostrophe
        ("kemp's ridley sea turtle-B2M", "LepiKemp-B2M"),
    ],
)
def test_hyphenated_common_names_are_reachable(text, expected):
    eq_(parse(text).to_string(), expected)


def test_a_hyphenated_gene_name_is_not_split_into_two_words():
    """
    The alias is added only for identifiers that already contain a space, so
    "DMB-1" cannot become the two-token gene name "DMB 1".
    """
    from mhcgnomes.species import _hyphens_as_spaces

    eq_(_hyphens_as_spaces("DMB-1"), None)
    eq_(_hyphens_as_spaces("long-haired rat"), "long haired rat")
    eq_(_hyphens_as_spaces("rhesus monkey"), None)
    eq_(parse("DMB-1").to_string(), "SpheMend-DMB-1")


def test_the_species_that_already_worked_are_untouched():
    eq_(parse("human-CD1a").to_string(), "human-CD1a")
    eq_(parse("rhesus monkey-CD1a").to_string(), "rhesus monkey-CD1a")
    eq_(parse("HLA-A*02:01").to_string(), "HLA-A*02:01")
