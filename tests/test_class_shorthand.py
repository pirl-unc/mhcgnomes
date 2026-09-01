"""
The hyphenated class shorthand: "SLA-I", "BoLA-II", "HLA-I".

Common in the literature, and it returned None for almost every species before
3.47.0 -- so a caller extracting MHC tokens from curated text got nothing and
the sample silently ended up with no genotype.

https://github.com/pirl-unc/mhcgnomes/issues/104
"""

import pytest

from mhcgnomes import Gene, Haplotype, MhcClass, parse

from .common import eq_, ok_

# Prefixes the issue reported as returning None. Every one of these has a
# working "<prefix> class I" form, which is what made the asymmetry a bug
# rather than a gap.
PREFIXES = ["HLA", "SLA", "BoLA", "DLA", "Patr", "Gaga", "ELA", "RT1", "Bota", "Ovar"]


@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("mhc_class", ["I", "II"])
def test_hyphenated_class_shorthand_parses(prefix, mhc_class):
    result = parse(f"{prefix}-{mhc_class}", raise_on_error=True)
    eq_(type(result), MhcClass)
    eq_(result.mhc_class, mhc_class)


@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("mhc_class", ["I", "II"])
def test_it_agrees_with_the_spelled_out_form(prefix, mhc_class):
    """The two spellings were meant to mean the same thing all along."""
    eq_(
        parse(f"{prefix}-{mhc_class}", raise_on_error=True),
        parse(f"{prefix} class {mhc_class}", raise_on_error=True),
    )


@pytest.mark.parametrize("prefix,expected", [("SLA", "1"), ("BoLA", "1"), ("ELA", "1")])
def test_the_digit_spelling_is_left_alone(prefix, expected):
    """
    Deliberately not extended to "<prefix>-1". SLA-1, BoLA-1 and ELA-1 are real
    class I gene names, so mapping the digits would shadow genuine loci for
    some species and not others -- exactly the inconsistency #104 reports.
    """
    result = parse(f"{prefix}-1", raise_on_error=True)
    eq_(type(result), Gene)
    eq_(result.name, expected)


# ---------------------------------------------------------------------------
# The two species with a better answer than the shorthand
# ---------------------------------------------------------------------------


def test_mamu_i_stays_a_gene():
    """
    Not a misparse of the class shorthand, which is how #104 read it. Mamu-I is
    a published macaque MHC class I locus -- J Immunol 2000;164:1386, "Mamu-I:
    A Novel Primate MHC Class I B-Related Locus with Unusually Low Variability"
    -- and the ontology declares it. The shorthand must not take it away.
    """
    result = parse("Mamu-I", raise_on_error=True)
    eq_(type(result), Gene)
    eq_(result.name, "I")
    eq_(result.species.name, "Macaca mulatta")


def test_h2_i_stays_a_haplotype():
    """
    "i" is a curated mouse haplotype. Note that mouse literature also writes
    H2-I for the class II region (I-A / I-E), so this string is genuinely
    ambiguous in the source material; the haplotype reading is what the
    ontology has evidence for.
    """
    result = parse("H2-I", raise_on_error=True)
    eq_(type(result), Haplotype)
    eq_(result.name, "i")


@pytest.mark.parametrize("prefix", ["Mamu", "H2"])
def test_the_class_two_form_still_works_for_those_species(prefix):
    """Only the class I spelling collides; nothing is named "II"."""
    result = parse(f"{prefix}-II", raise_on_error=True)
    eq_(type(result), MhcClass)
    eq_(result.mhc_class, "II")


def test_only_the_documented_species_shadow_the_class_i_shorthand():
    """
    A sweep, so a future gene or haplotype named "I" cannot quietly take the
    shorthand away from another species. Gene "II" resolves nowhere today, and
    "i" is a haplotype only for the mouse.
    """
    from mhcgnomes.species import latin_name_to_species_object

    shadowing = sorted(
        species.prefix
        for species in latin_name_to_species_object.values()
        if species.find_matching_gene_name("I") is not None
    )
    ok_(shadowing, "expected at least the macaque group to declare a gene named I")
    for prefix in PREFIXES:
        ok_(prefix not in shadowing, f"{prefix} now declares a gene named I")
