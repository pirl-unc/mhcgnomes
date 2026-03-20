"""
Tests for the Mhc-prefix stripping logic in infer_species_from_prefix.

The parser strips a leading "Mhc" (case-insensitive) from allele strings
when normal prefix matching fails, so that literature-style names like
"MhcTyal-DAB1*01:01" resolve to the correct species and gene. This
stripping is a last-resort fallback — a direct prefix match always wins.
"""

from mhcgnomes import Allele, Gene, parse
from mhcgnomes.species import infer_species_from_prefix

from .common import eq_

# ---------------------------------------------------------------------------
# 1. Basic Mhc stripping for barn owl (the motivating case)
# ---------------------------------------------------------------------------


def test_mhc_strip_tyal_species_inferred():
    result = infer_species_from_prefix("MhcTyal-DAB1*01:01")
    assert result is not None
    species, prefix = result
    eq_(species.prefix, "TytoAlba")
    eq_(prefix, "MhcTyal")


def test_mhc_strip_tyal_gene():
    eq_(parse("MhcTyal-UA", raise_on_error=True), Gene.get("TytoAlba", "UA"))


def test_mhc_strip_tyal_gene_dab1():
    eq_(parse("MhcTyal-DAB1", raise_on_error=True), Gene.get("TytoAlba", "DAB1"))


def test_mhc_strip_tyal_gene_dab2():
    eq_(parse("MhcTyal-DAB2", raise_on_error=True), Gene.get("TytoAlba", "DAB2"))


def test_mhc_strip_tyal_allele_ua():
    expected = Allele.get("TytoAlba", "UA", "01", "01")
    assert expected is not None
    eq_(parse("MhcTyal-UA*01:01", raise_on_error=True), expected)


def test_mhc_strip_tyal_allele_dab1():
    expected = Allele.get("TytoAlba", "DAB1", "01", "01")
    assert expected is not None
    eq_(parse("MhcTyal-DAB1*01:01", raise_on_error=True), expected)


# ---------------------------------------------------------------------------
# 2. Works for other bird species (not just barn owl)
# ---------------------------------------------------------------------------


def test_mhc_strip_acar_gene():
    """Great reed warbler — MhcAcar-UA should parse."""
    eq_(parse("MhcAcar-UA", raise_on_error=True), Gene.get("AcroArun", "UA"))


def test_mhc_strip_acar_allele():
    expected = Allele.get("AcroArun", "UA", "01", "01")
    assert expected is not None
    eq_(parse("MhcAcar-UA*01:01", raise_on_error=True), expected)


def test_mhc_strip_fuat_gene():
    """Eurasian coot — MhcFuat-DAB should parse."""
    eq_(parse("MhcFuat-DAB", raise_on_error=True), Gene.get("Fuat", "DAB"))


def test_mhc_strip_spma_gene():
    """Magellanic penguin — MhcSpma-DRB1 should parse."""
    eq_(parse("MhcSpma-DRB1", raise_on_error=True), Gene.get("Spma", "DRB1"))


def test_mhc_strip_coja_gene():
    """Japanese quail — MhcCoja-DAB1 should parse."""
    eq_(parse("MhcCoja-DAB1", raise_on_error=True), Gene.get("Coja", "DAB1"))


def test_mhc_strip_sthi_gene():
    """Common tern — MhcSthi-DAB should parse."""
    eq_(parse("MhcSthi-DAB", raise_on_error=True), Gene.get("Sthi", "DAB"))


# ---------------------------------------------------------------------------
# 3. Works for non-bird species too
# ---------------------------------------------------------------------------


def test_mhc_strip_paol_gene():
    """Olive flounder — MhcPaol-DAB should parse."""
    eq_(parse("MhcPaol-DAB", raise_on_error=True), Gene.get("Paol", "DAB"))


def test_mhc_strip_dare_gene():
    """Zebrafish — MhcDare-UBA should parse."""
    eq_(parse("MhcDare-UBA", raise_on_error=True), Gene.get("Dare", "UBA"))


def test_mhc_strip_xela_gene():
    """African clawed frog — MhcXela-UAA should parse."""
    eq_(parse("MhcXela-UAA", raise_on_error=True), Gene.get("Xela", "UAA"))


def test_mhc_strip_sasa_allele():
    """Atlantic salmon — MhcSasa-DAB*05:01 should parse."""
    expected = Allele.get("Sasa", "DAB", "05", "01")
    assert expected is not None
    eq_(parse("MhcSasa-DAB*05:01", raise_on_error=True), expected)


# ---------------------------------------------------------------------------
# 4. Case insensitivity of the Mhc prefix
# ---------------------------------------------------------------------------


def test_mhc_strip_lowercase():
    eq_(parse("mhcTyal-UA", raise_on_error=True), Gene.get("TytoAlba", "UA"))


def test_mhc_strip_uppercase():
    eq_(parse("MHCTyal-UA", raise_on_error=True), Gene.get("TytoAlba", "UA"))


def test_mhc_strip_mixed_case():
    eq_(parse("mHcTyal-UA", raise_on_error=True), Gene.get("TytoAlba", "UA"))


# ---------------------------------------------------------------------------
# 5. Direct prefix match always wins over Mhc stripping
# ---------------------------------------------------------------------------


def test_hla_not_stripped():
    """HLA starts with H, not Mhc — should parse normally."""
    result = infer_species_from_prefix("HLA-A*02:01")
    assert result is not None
    species, _prefix = result
    eq_(species.prefix, "HLA")


def test_direct_prefix_preferred_over_strip():
    """
    Known prefixes that happen to start with M are not mangled.
    """
    # Maar = Macaca arctoides (stump-tailed macaque)
    result = infer_species_from_prefix("Maar-A1")
    assert result is not None
    species, _prefix = result
    eq_(species.prefix, "Maar")


def test_mhcmafa_direct_prefix_wins():
    """
    MhcMafa is a registered alternative prefix for Macaca fascicularis.
    The direct prefix match must win — stripping 'Mhc' and matching 'Mafa'
    would also work, but the direct match is preferred and returns the
    correct full prefix length.
    """
    result = infer_species_from_prefix("MhcMafa-I*01:01")
    assert result is not None
    species, prefix = result
    eq_(species.prefix, "Mafa")
    # The full "MhcMafa" should be consumed as the prefix, not just "Mafa"
    eq_(prefix, "MhcMafa")


def test_gaga_direct_match_not_stripped():
    """Gaga (chicken) should match directly, not via Mhc stripping."""
    result = infer_species_from_prefix("Gaga-BF1")
    assert result is not None
    species, prefix = result
    eq_(species.prefix, "Gaga")
    eq_(prefix, "Gaga")


# ---------------------------------------------------------------------------
# 6. Stripping does NOT happen when it would produce garbage
# ---------------------------------------------------------------------------


def test_mhc_alone_returns_none():
    """Bare 'Mhc' with nothing after it should not match."""
    result = infer_species_from_prefix("Mhc")
    assert result is None


def test_mhc_with_unknown_suffix_returns_none():
    """Mhc followed by nonsense should not match any species."""
    result = infer_species_from_prefix("MhcZZZZ-FOO")
    assert result is None


def test_mhc_strip_does_not_double_strip():
    """
    If stripping 'Mhc' once leaves another 'Mhc' prefix, it should NOT
    strip again. E.g., 'MhcMhcTyal' should not resolve to Tyal.
    """
    result = infer_species_from_prefix("MhcMhcTyal-UA")
    assert result is None


# ---------------------------------------------------------------------------
# 7. The returned prefix length is correct for remaining-string computation
# ---------------------------------------------------------------------------


def test_mhc_strip_remaining_string_gene():
    """After stripping MhcTyal, remaining string should be '-UA'."""
    result = infer_species_from_prefix("MhcTyal-UA")
    assert result is not None
    _species, prefix = result
    remaining = "MhcTyal-UA"[len(prefix) :]
    eq_(remaining, "-UA")


def test_mhc_strip_remaining_string_allele():
    """After stripping MhcAcar, remaining string should be '-UA*01:01'."""
    result = infer_species_from_prefix("MhcAcar-UA*01:01")
    assert result is not None
    _species, prefix = result
    remaining = "MhcAcar-UA*01:01"[len(prefix) :]
    eq_(remaining, "-UA*01:01")


def test_mhc_strip_prefix_length_equals_mhc_plus_species():
    """The returned prefix should be exactly 'Mhc' + species prefix."""
    result = infer_species_from_prefix("MhcFuat-DAB*199")
    assert result is not None
    _species, prefix = result
    eq_(prefix, "MhcFuat")
    eq_(len(prefix), 3 + len("Fuat"))


# ---------------------------------------------------------------------------
# 8. Integration: full parse round-trips with Mhc prefix
# ---------------------------------------------------------------------------


def test_mhc_strip_round_trip_gene_to_string():
    """Parsed MhcTyal-UA should normalize to 'Tyal-UA' in to_string()."""
    result = parse("MhcTyal-UA", raise_on_error=True)
    assert isinstance(result, Gene)
    eq_(result.species.prefix, "TytoAlba")
    eq_(result.name, "UA")


def test_mhc_strip_round_trip_allele_to_string():
    """Parsed MhcAcar-UA*01:01 should produce a valid Allele with Acar species."""
    result = parse("MhcAcar-UA*01:01", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "AcroArun")
    eq_(result.gene.name, "UA")


def test_mhc_strip_round_trip_allele_fields():
    """Allele fields should be correctly parsed after Mhc stripping."""
    result = parse("MhcTyal-DAB1*03:02", raise_on_error=True)
    assert isinstance(result, Allele)
    eq_(result.species.prefix, "TytoAlba")
    eq_(result.gene.name, "DAB1")
    eq_(result.allele_fields, ("03", "02"))
