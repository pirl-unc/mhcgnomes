"""
Tests for 'alpha'/'beta' chain suffix resolution in gene names,
TL gene inheritance across Mus species, and literature-attested
Mus short prefixes.
"""

import pytest

from mhcgnomes import Gene, Species, parse

from .common import eq_

# ---------------------------------------------------------------------------
# alpha/beta suffix → single-letter chain indicator
# ---------------------------------------------------------------------------


def test_rt1_DOalpha_parses_as_gene():
    """'DOalpha' should resolve to gene DOa, not Allele(DOa, lpha)."""
    result = parse("RT1-DOalpha")
    assert type(result).__name__ == "Gene"
    eq_(result, Gene.get("RT1", "DOa"))


def test_rt1_DObeta_parses_as_gene():
    """'DObeta' should resolve to gene DOb."""
    result = parse("RT1-DObeta")
    assert type(result).__name__ == "Gene"
    eq_(result, Gene.get("RT1", "DOb"))


def test_mhc_rt1_dot_DOalpha():
    """Full benchmark string 'MHC RT1.DOalpha' should parse as Gene(DOa)."""
    result = parse("MHC RT1.DOalpha")
    assert type(result).__name__ == "Gene"
    eq_(result, Gene.get("RT1", "DOa"))


def test_h2_Ebeta_parses_as_gene():
    eq_(parse("H2-Ebeta"), Gene.get("H2", "EB"))


def test_h2_Aalpha_parses_as_gene():
    eq_(parse("H2-Aalpha"), Gene.get("H2", "AA"))


def test_exact_gene_match_not_broken_by_suffix_stripping():
    """Exact gene names ending in 'a' or 'b' should still match directly."""
    eq_(parse("RT1-DOa"), Gene.get("RT1", "DOa"))
    eq_(parse("HLA-DRA"), Gene.get("HLA", "DRA"))
    eq_(parse("HLA-DRB1"), Gene.get("HLA", "DRB1"))


def test_suffix_stripping_does_not_fire_when_candidate_not_a_gene():
    """When stripping 'alpha'/'beta' doesn't yield a known gene,
    the parser should fall through to other strategies, not crash."""
    # 'Ka' is not a Mus gene, so H2-Kalpha should not parse as Gene(Ka)
    result = parse("H2-Kalpha", raise_on_error=False)
    if result is not None:
        assert result.name != "Ka"


# ---------------------------------------------------------------------------
# TL gene on Mus sp.
# ---------------------------------------------------------------------------


def test_tl_gene_defined_on_mus_sp():
    gene = Gene.get("MusSp", "TL")
    assert gene is not None


def test_muco_tl_parses():
    """MucoTL = Mus cookii prefix + TL gene."""
    eq_(parse("MucoTL"), Gene.get("Muco", "TL"))


def test_mupl_tl_parses():
    """MuplTL = Mus platythrix prefix + TL gene."""
    eq_(parse("MuplTL"), Gene.get("Mupl", "TL"))


def test_muca_tl_parses():
    eq_(parse("MucaTL"), Gene.get("Muca", "TL"))


def test_muab_tl_parses():
    eq_(parse("MuabTL"), Gene.get("Muab", "TL"))


def test_mumi_tl_parses():
    eq_(parse("MumiTL"), Gene.get("Mumi", "TL"))


def test_mupa_tl_parses():
    eq_(parse("MupaTL"), Gene.get("Mupa", "TL"))


def test_tl_inherited_by_mus_musculus():
    """H2 (Mus musculus) should also inherit TL from Mus sp."""
    gene = Gene.get("H2", "TL")
    assert gene is not None


# ---------------------------------------------------------------------------
# Literature-attested Mus short prefixes
# ---------------------------------------------------------------------------

ATTESTED_MUS_PREFIXES = [
    ("Muco", "Mus cookii"),
    ("Mupl", "Mus platythrix"),
    ("Muce", "Mus cervicolor"),
    ("Muca", "Mus caroli"),
    ("Mupa", "Mus pahari"),
    ("Muab", "Mus abbotti"),
    ("Mumi", "Mus minutoides"),
]


@pytest.mark.parametrize("prefix, latin", ATTESTED_MUS_PREFIXES)
def test_mus_short_prefix_resolves(prefix, latin):
    species = Species.get(prefix)
    assert species is not None, f"Prefix {prefix} not found"
    assert species.latin_name == latin


def test_musa_not_registered():
    """Musa (M. saxicola) is NOT attested in the literature and should
    not resolve — it collides with the banana genus Musa."""
    species = Species.get("Musa")
    if species is not None:
        assert species.latin_name != "Mus saxicola"
