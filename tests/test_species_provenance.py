"""
Tests for how a caller can tell a explicit species from an inferred one, and for
comparing two species names that differ in specificity.

https://github.com/pirl-unc/mhcgnomes/issues/116
https://github.com/pirl-unc/mhcgnomes/issues/118
"""

import pytest

from mhcgnomes import Allele, Gene, Pair, ParseError, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# 1. species_source
# ---------------------------------------------------------------------------

EXPLICIT = [
    "HLA-A*02:01",  # attached prefix
    "Gaga-BLB2*02",
    "Coja-DBB1",
    "BoLA-N*01301",
    "Bota-DRB3*011:01",
    "H2-Kb",
    "BoLA class I",
    "mouse H2-Kb",  # leading common name
    "Homo sapiens class I",  # leading latin name
    "HLA",  # species alone
]

INFERRED = [
    "BLB2*02",  # species comes from the gene name
    "BF2*02:01",
    "B12 class I",
]

DEFAULTED = [
    "A*02:01",  # no species anywhere, falls back to default_species
    "MHC class II",
    "class II",
    "TAP1",
]


@pytest.mark.parametrize("name", EXPLICIT)
def test_explicit_species_is_reported_as_explicit(name):
    eq_(parse(name).species_source, "explicit")


@pytest.mark.parametrize("name", INFERRED)
def test_species_from_a_gene_name_is_reported_as_inferred(name):
    eq_(parse(name).species_source, "inferred")


@pytest.mark.parametrize("name", DEFAULTED)
def test_species_from_default_species_is_reported_as_default(name):
    eq_(parse(name).species_source, "default")


@pytest.mark.parametrize("name", EXPLICIT)
def test_explicit_species_is_from_input(name):
    assert parse(name).species_from_input


@pytest.mark.parametrize("name", INFERRED + DEFAULTED)
def test_non_explicit_species_is_not_from_input(name):
    assert not parse(name).species_from_input


@pytest.mark.parametrize("name", EXPLICIT + INFERRED + DEFAULTED)
def test_species_from_input_agrees_with_species_source(name):
    result = parse(name)
    eq_(result.species_from_input, result.species_source == "explicit")


def test_default_is_distinguishable_from_inferred():
    """
    The two are different problems: 'default' means no species was involved at
    all, 'inferred' means one was derived from a gene name. A caller putting
    human MHC on a fish study needs to tell them apart.
    """
    eq_(parse("MHC class II").species_source, "default")
    eq_(parse("BLB2*02").species_source, "inferred")


def test_default_species_argument_is_respected():
    result = parse("A*02:01", default_species="Mamu")
    eq_(result.species_source, "default")
    eq_(result.species.name, "Macaca mulatta")


# ---------------------------------------------------------------------------
# 2. Provenance must not leak into identity
# ---------------------------------------------------------------------------


def test_provenance_does_not_affect_equality_or_hashing():
    explicit = parse("HLA-A*02:01")
    defaulted = parse("A*02:01")
    eq_(explicit.species_source, "explicit")
    eq_(defaulted.species_source, "default")
    eq_(explicit, defaulted)
    eq_(hash(explicit), hash(defaulted))


def test_provenance_does_not_appear_in_repr_or_dict():
    result = parse("HLA-A*02:01")
    assert "species_source" not in repr(result)
    assert "species_source" not in result.to_dict()


def test_directly_constructed_results_have_no_provenance():
    assert Allele.get("HLA", "A", "02", "01").species_source is None
    assert Gene.get("HLA", "A").species_source is None


# ---------------------------------------------------------------------------
# 3. require_explicit_species
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", EXPLICIT)
def test_require_explicit_species_keeps_explicit_results(name):
    eq_(parse(name, require_explicit_species=True), parse(name))


@pytest.mark.parametrize("name", INFERRED + DEFAULTED)
def test_require_explicit_species_rejects_non_explicit_results(name):
    assert parse(name, require_explicit_species=True, raise_on_error=False) is None


@pytest.mark.parametrize("name", INFERRED + DEFAULTED)
def test_require_explicit_species_raises_when_asked(name):
    with pytest.raises(ParseError):
        parse(name, require_explicit_species=True)


def test_species_source_is_none_for_unparsed_input():
    """
    Every parseable result currently carries a species, so the None case only
    arises for input that does not parse at all.
    """
    assert parse("n/a", raise_on_error=False) is None
    assert parse("n/a", require_explicit_species=True, raise_on_error=False) is None


def test_require_explicit_species_composes_with_required_result_types():
    eq_(
        parse(
            "Gaga-BLB2*02",
            required_result_types=(Allele, Gene, Pair),
            require_explicit_species=True,
        ).to_string(),
        "Gaga-BLB2*02",
    )
    assert (
        parse(
            "BLB2*02",
            required_result_types=(Allele, Gene, Pair),
            require_explicit_species=True,
            raise_on_error=False,
        )
        is None
    )


# ---------------------------------------------------------------------------
# 4. Species.compatible_with
# ---------------------------------------------------------------------------

COMPATIBLE = [
    ("Bos taurus", "Bos sp."),
    ("Sus scrofa", "Sus sp."),
    ("Coturnix japonica", "Galliformes sp."),
    ("Homo sapiens", "Homo sapiens"),
    ("Saimiri sciureus", "Primata sp."),
    ("Homo sapiens", "Gnathostomata sp."),
    # Humans are primates, and Primata sp. is the primate order (#122).
    ("Homo sapiens", "Primata sp."),
]

INCOMPATIBLE = [
    ("Macaca mulatta", "Macaca fascicularis"),
    ("Carassius gibelio", "Homo sapiens"),
    ("Bos taurus", "Ovis aries"),
    # An NHP-* allele can never have come from a human sample. This is plain
    # ancestry, not a special case: NHP is a sibling of Homo sapiens under
    # Primata sp., not one of its ancestors. See issues #122 and #126.
    ("Homo sapiens", "NHP"),
]


@pytest.mark.parametrize("a,b", COMPATIBLE)
def test_compatible_species(a, b):
    assert Species.get_by_latin_name(a).compatible_with(b)


@pytest.mark.parametrize("a,b", COMPATIBLE)
def test_compatibility_is_symmetric(a, b):
    assert Species.get_by_latin_name(b).compatible_with(a)


@pytest.mark.parametrize("a,b", INCOMPATIBLE)
def test_incompatible_species(a, b):
    assert not Species.get_by_latin_name(a).compatible_with(b)
    assert not Species.get_by_latin_name(b).compatible_with(a)


def test_compatible_with_accepts_prefixes_and_common_names():
    cattle = Species.get("BoLA")
    assert cattle.compatible_with("Bota")
    assert cattle.compatible_with("Bos taurus")
    assert cattle.compatible_with("cow")


def test_compatible_with_returns_false_for_unknown_species():
    assert not Species.get_by_latin_name("Homo sapiens").compatible_with("not a species")


def test_sharing_a_common_ancestor_is_not_the_same_predicate():
    """
    Every species descends from Gnathostomata sp., so a common-ancestor test
    would accept anything. compatible_with requires a direct relation.
    """
    human = Species.get_by_latin_name("Homo sapiens")
    carp = Species.get_by_latin_name("Carassius gibelio")
    root = Species.get_by_latin_name("Gnathostomata sp.")
    assert root.is_ancestor_of(human) and root.is_ancestor_of(carp)
    assert not human.compatible_with(carp)
