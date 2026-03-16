"""
Tests for the mhc1/mhc2 gene prefix stripping in Species.find_matching_gene_name().

ZFIN and some other fish databases use lowercase concatenated gene names like
"mhc1uba" (class I gene UBA) and "mhc2daa" (class II gene DAA). The parser
strips mhc1/mhc2 prefixes generically rather than requiring per-gene aliases.
"""

from mhcgnomes import Gene, parse

from .common import eq_

# ---------------------------------------------------------------------------
# Positive tests: mhc1/mhc2 prefix stripping resolves known genes
# ---------------------------------------------------------------------------


class TestMhc1Mhc2PrefixStrippingPositive:
    """Gene tokens starting with mhc1/mhc2 resolve to the stripped gene name."""

    def test_dare_mhc1uba(self):
        eq_(parse("Dare-mhc1uba", raise_on_error=True), Gene.get("Dare", "UBA"))

    def test_dare_mhc1uma(self):
        eq_(parse("Dare-mhc1uma", raise_on_error=True), Gene.get("Dare", "UMA"))

    def test_dare_mhc2daa(self):
        eq_(parse("Dare-mhc2daa", raise_on_error=True), Gene.get("Dare", "DAA"))

    def test_dare_mhc2dab(self):
        eq_(parse("Dare-mhc2dab", raise_on_error=True), Gene.get("Dare", "DAB"))

    def test_case_insensitive_MHC1UBA(self):
        """Uppercase MHC1UBA should also strip."""
        eq_(parse("Dare-MHC1UBA", raise_on_error=True), Gene.get("Dare", "UBA"))

    def test_case_insensitive_MHC2DAB(self):
        eq_(parse("Dare-MHC2DAB", raise_on_error=True), Gene.get("Dare", "DAB"))

    def test_works_for_other_fish_with_uba(self):
        """mhc1 stripping should work for any fish species, not just zebrafish."""
        eq_(parse("Saal-mhc1uba", raise_on_error=True), Gene.get("Saal", "UBA"))

    def test_works_for_salmon_mhc2dab(self):
        eq_(parse("Sasa-mhc2dab", raise_on_error=True), Gene.get("Sasa", "DAB"))

    def test_works_for_trout_mhc1uba(self):
        eq_(parse("Onmy-mhc1uba", raise_on_error=True), Gene.get("Onmy", "UBA"))

    def test_allele_with_mhc1_prefix(self):
        """mhc1/mhc2 stripping should work in allele context too."""
        result = parse("Dare-mhc1uba*01", raise_on_error=True)
        eq_(result.gene.name, "UBA")

    def test_allele_with_mhc2_prefix(self):
        result = parse("Dare-mhc2daa*01:01", raise_on_error=True)
        eq_(result.gene.name, "DAA")


# ---------------------------------------------------------------------------
# Negative tests: mhc1/mhc2 stripping does not create false positives
# ---------------------------------------------------------------------------


class TestMhc1Mhc2PrefixStrippingNegative:
    """Stripping must not match genes that don't exist in the species."""

    def test_mhc1_with_nonexistent_gene_returns_none(self):
        """mhc1zzz should not parse — ZZZ is not a zebrafish gene."""
        assert parse("Dare-mhc1zzz", raise_on_error=False) is None

    def test_mhc2_with_nonexistent_gene_returns_none(self):
        assert parse("Dare-mhc2zzz", raise_on_error=False) is None

    def test_mhc1_alone_is_not_a_gene(self):
        """Bare 'mhc1' without a gene suffix should not parse as a gene."""
        assert parse("Dare-mhc1", raise_on_error=False) is None

    def test_mhc2_alone_is_not_a_gene(self):
        assert parse("Dare-mhc2", raise_on_error=False) is None

    def test_mhc3_prefix_not_stripped(self):
        """Only mhc1 and mhc2 should be stripped, not mhc3 or other numbers."""
        assert parse("Dare-mhc3uba", raise_on_error=False) is None

    def test_mhc_without_number_not_stripped_at_gene_level(self):
        """Plain 'mhc' prefix on a gene token should not be stripped.
        (This is handled at the species level, not gene level.)"""
        # mhcuba is not a valid gene — "mhc" without 1/2 is not a gene prefix
        assert parse("Dare-mhcuba", raise_on_error=False) is None

    def test_does_not_strip_for_species_without_gene(self):
        """mhc1dqa on a species that doesn't have DQA should fail."""
        # Zebrafish has UBA, UMA, DAA, DAB — but not DQA
        assert parse("Dare-mhc1dqa", raise_on_error=False) is None

    def test_does_not_strip_when_gene_exists_directly(self):
        """If a gene alias 'mhc1uba' were also defined directly, the
        direct match should win. Here we just verify direct genes still
        work when they don't start with mhc1/mhc2."""
        # UBA matches directly, no stripping needed
        eq_(parse("Dare-UBA", raise_on_error=True), Gene.get("Dare", "UBA"))
