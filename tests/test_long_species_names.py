"""
Species named by a common name of more than three words.

The species matcher tried the first three tokens, then two, then one. Forty-one
common names in the ontology are longer than that once hyphens are counted --
"north atlantic right whale", "thirteen-lined ground squirrel", "kemp's ridley
sea turtle" -- so none of them could be read back, and any input naming those
species by common name simply failed.

Found while measuring #176, which required every printed form to parse back:
`Gene.to_string` prints CD1 genes with the common species name, so the package
was emitting strings it then refused.

https://github.com/pirl-unc/mhcgnomes/issues/177
"""

import pytest

from mhcgnomes import parse
from mhcgnomes.species import (
    MAX_SPECIES_NAME_TOKENS,
    latin_name_to_species_object,
)

from .common import eq_, ok_


def _token_count(name):
    return len(str(name).replace("-", " ").split())


LONG_COMMON_NAMES = sorted(
    {
        (str(common_name), species.name)
        for species in latin_name_to_species_object.values()
        for common_name in species.all_common_names
        if _token_count(common_name) > 3
    }
)


def test_there_are_long_common_names_to_test():
    ok_(
        len(LONG_COMMON_NAMES) >= 40,
        f"only {len(LONG_COMMON_NAMES)} found; did the ontology shrink?",
    )


@pytest.mark.parametrize("common_name,latin_name", LONG_COMMON_NAMES)
def test_a_long_common_name_can_lead_a_string(common_name, latin_name):
    result = parse(f"{common_name} class I", raise_on_error=False)
    ok_(result is not None, f"{common_name!r} does not parse as a leading species name")
    eq_(result.species.name, latin_name)


def test_the_window_covers_the_longest_name_curated():
    """
    The constant is a bound on the ontology, so it has to move if a longer name
    is ever added -- otherwise that name silently stops being parseable, which
    is the state all 41 of these were in.
    """
    longest = max(
        (
            (_token_count(common_name), str(common_name), species.name)
            for species in latin_name_to_species_object.values()
            for common_name in species.all_common_names
        ),
        default=(0, "", ""),
    )
    ok_(
        longest[0] <= MAX_SPECIES_NAME_TOKENS,
        f"{longest[1]!r} ({longest[2]}) is {longest[0]} tokens, over the "
        f"MAX_SPECIES_NAME_TOKENS of {MAX_SPECIES_NAME_TOKENS}",
    )


@pytest.mark.parametrize(
    "text,expected_species",
    [
        ("north atlantic right whale class I", "Eubalaena glacialis"),
        ("north island brown kiwi-B2M", "Apteryx mantelli"),
        ("nancy ma's night monkey-B2M", "Aotus nancymaae"),
        ("hong kong whipping frog-DAB", "Polypedates megacephalus"),
    ],
)
def test_names_that_used_to_return_none(text, expected_species):
    result = parse(text)
    eq_(result.species.name, expected_species)


def test_short_names_are_unaffected():
    # The loop tries longest first and always did, so a wider window cannot
    # change what a shorter name matches.
    eq_(parse("homo sapiens class I").species.name, "Homo sapiens")
    eq_(parse("human-CD1a").species.name, "Homo sapiens")
    eq_(parse("rhesus monkey-CD1a").species.name, "Macaca mulatta")
    eq_(parse("HLA-A*02:01").to_string(), "HLA-A*02:01")
