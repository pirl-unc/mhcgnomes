"""
Tests for parsing fixes in v3.30.0.

Covers:
- H2-AA / H2-Aa parsing as Gene (not Pair)
- H2-AB1 / H2-Ab1 parsing as Gene (not parse error)
- RT1-B parsing as Class2Locus (not Haplotype)
- RT1-B gene alias (B → Bb) via preferred_result_types
- Nibea species recognition
- Regression: IAk-style haplotype+locus parsing still works
"""

from mhcgnomes import Class2Locus, Gene, Pair, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# H2-AA / H2-Aa: should parse as Gene, not Pair
# ---------------------------------------------------------------------------


def test_h2_aa_parses_as_gene():
    result = parse("H2-AA")
    eq_(type(result), Gene)
    eq_(result.name, "AA")


def test_h2_aa_lowercase_parses_as_gene():
    result = parse("H2-Aa")
    eq_(type(result), Gene)
    eq_(result.name, "AA")


def test_h2_aa_species_is_mouse():
    result = parse("H2-AA")
    eq_(result.species, Species.get("H2"))


# ---------------------------------------------------------------------------
# H2-AB1 / H2-Ab1: should parse as Gene (was hard parse error)
# ---------------------------------------------------------------------------


def test_h2_ab1_parses_as_gene():
    result = parse("H2-AB1")
    eq_(type(result), Gene)
    eq_(result.name, "AB1")


def test_h2_ab1_lowercase_parses_as_gene():
    result = parse("H2-Ab1")
    eq_(type(result), Gene)
    eq_(result.name, "AB1")


# ---------------------------------------------------------------------------
# RT1-B: should parse as Class2Locus (not Haplotype)
# ---------------------------------------------------------------------------


def test_rt1_b_parses_as_class2_locus():
    result = parse("RT1-B")
    eq_(type(result), Class2Locus)
    eq_(result.name, "B")


def test_rt1_b_species_is_rat():
    result = parse("RT1-B")
    eq_(result.species, Species.get("RT1"))


def test_rt1_b_preferred_gene_returns_bb():
    """With preferred_result_types=[Gene], RT1-B should resolve to Gene Bb
    via the gene alias (NCBI GeneID 24738 legacy entry)."""
    result = parse("RT1-B", preferred_result_types=[Gene])
    eq_(type(result), Gene)
    eq_(result.name, "Bb")


# ---------------------------------------------------------------------------
# Nibea species recognition
# ---------------------------------------------------------------------------


def test_nibea_mitsukurii_species():
    species = Species.get("NibeMits")
    assert species is not None
    eq_(species.latin_name, "Nibea mitsukurii")


def test_nibea_albiflora_species():
    species = Species.get("NibeAlbi")
    assert species is not None
    eq_(species.latin_name, "Nibea albiflora")


def test_nibea_mitsukurii_full_name():
    species = Species.get("Nibea mitsukurii")
    assert species is not None
    eq_(species.prefix, "NibeMits")


# ---------------------------------------------------------------------------
# Regression: IAk-style haplotype+locus splitting still works
# ---------------------------------------------------------------------------


def test_h2_iak_still_parses_as_pair():
    """Ensure the guard in parse_haplotype_with_class2_locus_from_any_string_split
    doesn't break legitimate locus+haplotype splits like IAk.
    IAk = haplotype 'k' restricted to locus A, which collapses to a Pair."""
    result = parse("H2-IAk")
    eq_(type(result), Pair)
    eq_(result.alpha.gene.name, "AA")
    eq_(result.beta.gene.name, "AB")
