"""
Tests for HLA Class II heterodimer dot notation parsing.

HLA-DQ molecules are heterodimers consisting of an alpha chain (DQA1) and
a beta chain (DQB1). The shorthand "DQx.y" notation encodes both:
- x = the DQ serotype number (determined by beta chain)
- y = the alpha chain variant number

For example, DQ2.5 means "DQ2 serotype with alpha-5 chain" = DQA1*05:01/DQB1*02:01.

Note: HLA-DR does NOT use this notation because DRA is essentially monomorphic
(non-variable), so DR serotypes are determined solely by DRB alleles.

References:
-----------
DQ2.5 (DQA1*05:01/DQB1*02:01):
    - Lundin KE, et al. "Gliadin-specific, HLA-DQ restricted T cells from coeliac
      disease patients." PMC3872820 (2014)
      https://pmc.ncbi.nlm.nih.gov/articles/PMC3872820/
    - Megiorni F, Pizzuti A. "HLA-DQA1 and HLA-DQB1 in Celiac disease
      predisposition." J Biomed Sci. PMC3482388 (2012)
      https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3482388/

DQ2.2 (DQA1*02:01/DQB1*02:02):
    - Dahal-Koirala S, et al. "A molecular basis for the T cell response in
      HLA-DQ2.2 mediated celiac disease." PNAS 117(6):3063-3070 (2020)
      https://www.pnas.org/doi/10.1073/pnas.1914308117

DQ2.3 (DQA1*03:01/DQB1*02:01):
    - Broughton SE, et al. "Structural and Functional Studies of trans-Encoded
      HLA-DQ2.3 (DQA1*03:01/DQB1*02:01) Protein Molecule." PMC3340161 (2012)
      https://pmc.ncbi.nlm.nih.gov/articles/PMC3340161/

DQ7.5 (DQA1*05:05/DQB1*03:01):
    - Mayo Clinic Laboratories. "Celiac Associated HLA-DQ Alpha 1 and DQ Beta 1
      DNA Typing." Test ID: CELI.
      https://gi.testcatalog.org/show/CELI

DQ3.1 (DQA1*03:01/DQB1*03:01):
    - Sidney J, et al. "Definition of a DQ3.1-specific binding motif."
      J Immunol. 1994 Oct 1;153(7):3194-203. PMID: 7512598
      https://pubmed.ncbi.nlm.nih.gov/7512598/
    - IEDB assay data referencing HLA-DQA1*03:01/DQB1*03:01

DQ8.5 (DQA1*05:01/DQB1*03:02):
    - Petersen J, et al. "Diverse T Cell Receptor Gene Usage in HLA-DQ8-Associated
      Celiac Disease Converges into a Consensus Binding Solution."
      Structure. 2016 Oct 4;24(10):1643-1657. PMID: 27568928
      https://pubmed.ncbi.nlm.nih.gov/27568928/
    - Crystal structures: PDB 5KSA, 5KSB

IEDB occurrence counts (mhc_ligand_full.csv):
    DQ2.2:  45,950 occurrences
    DQ7.5:  45,944 occurrences
    DQ2.5:  43,167 occurrences
    DR11.1:     84 occurrences (T cell clone name, NOT a heterodimer)
    DQ3.1:      47 occurrences
    DQ2.3:      14 occurrences
    DQ8.5:       2 occurrences
"""

import pytest

from mhcgnomes import parse
from mhcgnomes.errors import ParseError
from mhcgnomes.pair import Pair


class TestHeterodimersBasicParsing:
    """Test that heterodimer shorthand notation parses to Pair objects."""

    @pytest.mark.parametrize(
        "shorthand,expected_alpha,expected_beta",
        [
            # DQ2.5 - most common celiac disease haplotype (43,167 in IEDB)
            # Source: PMC3872820, PMC3482388
            ("DQ2.5", "DQA1*05:01", "DQB1*02:01"),
            ("HLA-DQ2.5", "DQA1*05:01", "DQB1*02:01"),
            # DQ2.2 - second DQ2 variant (45,950 in IEDB)
            # Source: PNAS 1914308117
            ("DQ2.2", "DQA1*02:01", "DQB1*02:02"),
            ("HLA-DQ2.2", "DQA1*02:01", "DQB1*02:02"),
            # DQ2.3 - trans-encoded variant associated with T1D
            # Source: PMC3340161
            ("DQ2.3", "DQA1*03:01", "DQB1*02:01"),
            ("HLA-DQ2.3", "DQA1*03:01", "DQB1*02:01"),
            # DQ7.5 - shares alpha chain with DQ2.5 (45,944 in IEDB)
            # Source: Mayo Clinic Labs CELI test
            ("DQ7.5", "DQA1*05:05", "DQB1*03:01"),
            ("HLA-DQ7.5", "DQA1*05:05", "DQB1*03:01"),
            # DQ3.1 - well-characterized binding motif (47 in IEDB)
            # Source: J Immunol 1994 PMID:7512598
            ("DQ3.1", "DQA1*03:01", "DQB1*03:01"),
            ("HLA-DQ3.1", "DQA1*03:01", "DQB1*03:01"),
            # DQ8.5 - trans-encoded DQ8 variant (2 in IEDB)
            # Source: Structure 2016 PMID:27568928, PDB 5KSA/5KSB
            ("DQ8.5", "DQA1*05:01", "DQB1*03:02"),
            ("HLA-DQ8.5", "DQA1*05:01", "DQB1*03:02"),
        ],
    )
    def test_heterodimer_parses_to_pair(self, shorthand, expected_alpha, expected_beta):
        """Heterodimer shorthand should parse to a Pair with correct alpha/beta alleles."""
        result = parse(shorthand)
        assert isinstance(result, Pair), f"{shorthand} should parse as Pair, got {type(result)}"

        # Verify alpha chain
        alpha_str = result.alpha.to_string()
        assert expected_alpha in alpha_str, (
            f"{shorthand} alpha chain should be {expected_alpha}, got {alpha_str}"
        )

        # Verify beta chain
        beta_str = result.beta.to_string()
        assert expected_beta in beta_str, (
            f"{shorthand} beta chain should be {expected_beta}, got {beta_str}"
        )


class TestHeterodimersStringOutput:
    """Test that heterodimer Pair objects produce correct string representations."""

    @pytest.mark.parametrize(
        "shorthand,expected_compact",
        [
            ("DQ2.5", "HLA-DQA1*05:01/DQB1*02:01"),
            ("DQ2.2", "HLA-DQA1*02:01/DQB1*02:02"),
            ("DQ2.3", "HLA-DQA1*03:01/DQB1*02:01"),
            ("DQ7.5", "HLA-DQA1*05:05/DQB1*03:01"),
            ("DQ3.1", "HLA-DQA1*03:01/DQB1*03:01"),
            ("DQ8.5", "HLA-DQA1*05:01/DQB1*03:02"),
        ],
    )
    def test_heterodimer_to_string(self, shorthand, expected_compact):
        """Heterodimer should produce standard pair notation when converted to string."""
        result = parse(shorthand)
        assert result.to_string() == expected_compact


class TestHeterodimersPreserveRawString:
    """Test that parsing preserves the original input string."""

    @pytest.mark.parametrize(
        "shorthand",
        [
            "DQ2.5",
            "HLA-DQ2.5",
            "DQ2.2",
            "DQ7.5",
        ],
    )
    def test_raw_string_preserved(self, shorthand):
        """The original input string should be preserved in raw_string."""
        result = parse(shorthand)
        assert result.raw_string == shorthand


class TestHeterodimersVsSerotypes:
    """Test that heterodimer notation is distinct from serotype notation."""

    def test_dq2_is_serotype(self):
        """DQ2 (without dot) should parse as Serotype, not Pair."""
        from mhcgnomes.serotype import Serotype

        result = parse("DQ2")
        assert isinstance(result, Serotype)
        assert result.name == "DQ2"

    def test_dq8_is_serotype(self):
        """DQ8 (without dot) should parse as Serotype."""
        from mhcgnomes.serotype import Serotype

        result = parse("DQ8")
        assert isinstance(result, Serotype)
        assert result.name == "DQ8"

    def test_dq2_5_is_pair(self):
        """DQ2.5 (with dot) should parse as Pair, not Serotype."""
        result = parse("DQ2.5")
        assert isinstance(result, Pair)
        # Should NOT be a Serotype
        from mhcgnomes.serotype import Serotype

        assert not isinstance(result, Serotype)


class TestHeterodimersEquivalence:
    """Test that heterodimer shorthand produces same result as explicit pair notation."""

    @pytest.mark.parametrize(
        "shorthand,explicit",
        [
            ("DQ2.5", "DQA1*05:01/DQB1*02:01"),
            ("DQ2.2", "DQA1*02:01/DQB1*02:02"),
            ("DQ2.3", "DQA1*03:01/DQB1*02:01"),
            ("DQ7.5", "DQA1*05:05/DQB1*03:01"),
            ("DQ3.1", "DQA1*03:01/DQB1*03:01"),
            ("DQ8.5", "DQA1*05:01/DQB1*03:02"),
        ],
    )
    def test_shorthand_equals_explicit_notation(self, shorthand, explicit):
        """Parsing shorthand should produce equivalent result to parsing explicit notation."""
        shorthand_result = parse(shorthand)
        explicit_result = parse(explicit)

        # Both should be Pair objects
        assert isinstance(shorthand_result, Pair)
        assert isinstance(explicit_result, Pair)

        # Alpha chains should match
        assert shorthand_result.alpha == explicit_result.alpha

        # Beta chains should match
        assert shorthand_result.beta == explicit_result.beta


class TestHeterodimersNamingLogic:
    """
    Test the naming logic: DQx.y means DQx serotype with alpha-y chain.

    The notation encodes:
    - First number (x) = DQ serotype (determined by DQB1 allele)
    - Second number (y) = alpha chain variant (DQA1 allele group)

    This is based on the classical serological naming where:
    - DQ2 serotype = DQB1*02:xx alleles
    - DQ3 serotype = DQB1*03:xx alleles
    - DQ7 serotype = DQB1*03:01 specifically (split of DQ3)
    - DQ8 serotype = DQB1*03:02 specifically (split of DQ3)
    """

    def test_dq2_variants_share_beta_chain_family(self):
        """All DQ2.x variants should have DQB1*02:xx beta chains."""
        for shorthand in ["DQ2.2", "DQ2.3", "DQ2.5"]:
            result = parse(shorthand)
            assert isinstance(result, Pair)
            beta_gene = result.beta.gene.name
            assert beta_gene == "DQB1", f"{shorthand} beta should be DQB1, got {beta_gene}"
            beta_group = result.beta.allele_fields[0]
            assert beta_group == "02", f"{shorthand} beta should be *02:xx, got *{beta_group}:xx"

    def test_alpha_5_variants(self):
        """DQx.5 variants should have DQA1*05:xx alpha chains."""
        for shorthand in ["DQ2.5", "DQ7.5", "DQ8.5"]:
            result = parse(shorthand)
            assert isinstance(result, Pair)
            alpha_gene = result.alpha.gene.name
            assert alpha_gene == "DQA1", f"{shorthand} alpha should be DQA1"
            alpha_group = result.alpha.allele_fields[0]
            assert alpha_group == "05", f"{shorthand} alpha should be *05:xx, got *{alpha_group}:xx"


class TestHeterodimersEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_case_insensitive(self):
        """Heterodimer parsing should be case-insensitive."""
        variants = ["DQ2.5", "dq2.5", "Dq2.5", "dQ2.5"]
        results = [parse(v) for v in variants]

        # All should produce equivalent Pair objects
        for i, result in enumerate(results):
            assert isinstance(result, Pair), f"{variants[i]} should parse as Pair"

        # All should have same alpha/beta
        for i in range(1, len(results)):
            assert results[i].alpha == results[0].alpha
            assert results[i].beta == results[0].beta

    def test_invalid_heterodimer_patterns_fail(self):
        """Invalid heterodimer patterns should raise ParseError or not parse as Pair."""
        import contextlib

        invalid_patterns = [
            "DQ2.",  # Missing second number
            "DQ.5",  # Missing first number
            "DQ25",  # No dot (this is ambiguous - could be serotype)
            "DR2.5",  # DR doesn't use this notation (DRA is monomorphic)
        ]
        for pattern in invalid_patterns:
            # These should either fail or parse as something other than heterodimer Pair
            with contextlib.suppress(ParseError):
                result = parse(pattern)
                # If it parses, it shouldn't be a Pair from heterodimer notation
                # (e.g., DQ25 might parse as something else)
                assert not isinstance(result, Pair), f"{pattern} should not parse as Pair"


class TestDRDoesNotUseHeterodimerNotation:
    """
    Test that DR molecules don't use the DQx.y heterodimer notation.

    HLA-DR is different from HLA-DQ:
    - DRA (alpha chain) is essentially monomorphic (no functional variation)
    - All DR serotype specificity comes from DRB (beta chain)
    - Therefore "DRx.y" notation doesn't make sense for DR

    The "DR11.1" found in IEDB (84 occurrences) refers to a T cell clone name,
    not a heterodimer designation.

    Reference:
    - HLA-DRA Wikipedia: "Unlike the alpha chains of other Human MHC class II
      molecules, the alpha subunit is practically invariable."
      https://en.wikipedia.org/wiki/HLA-DRA
    """

    def test_dr11_is_serotype(self):
        """DR11 should parse as serotype (beta chain determines DR specificity)."""
        from mhcgnomes.serotype import Serotype

        result = parse("DR11")
        assert isinstance(result, Serotype)
        assert result.name == "DR11"

    def test_dr11_1_is_not_valid_heterodimer(self):
        """DR11.1 should not parse as a heterodimer (DRA is monomorphic)."""
        # DR11.1 in IEDB refers to a T cell clone, not a molecule
        # This should either fail or not parse as a Pair
        try:
            result = parse("DR11.1")
            assert not isinstance(result, Pair), "DR11.1 should not parse as Pair"
        except ParseError:
            pass  # This is acceptable - DR11.1 is not valid heterodimer notation


class TestCeliacDiseaseAssociatedHeterodimers:
    """
    Test heterodimers commonly referenced in celiac disease literature.

    ~90% of celiac patients carry DQ2.5 or DQ2.2, often in combination.
    ~5-10% carry DQ8 (not dot notation since it's determined by DQB1*03:02 alone).

    The trans-encoded DQ2.5 can form from DQ2.2/DQ7.5 heterozygotes:
    - DQ2.2 provides DQB1*02:02 (similar to DQB1*02:01)
    - DQ7.5 provides DQA1*05:05 (similar to DQA1*05:01)
    - Together they can form DQ2.5-like molecule in trans

    References:
    - Megiorni F, Pizzuti A. J Biomed Sci. 2012. PMC3482388
    - Lundin KE, et al. PMC3872820
    """

    def test_celiac_primary_risk_heterodimer(self):
        """DQ2.5 is the primary celiac disease risk heterodimer."""
        result = parse("DQ2.5")
        assert isinstance(result, Pair)
        # Verify it's the correct molecule
        assert "DQA1" in result.alpha.gene.name
        assert "DQB1" in result.beta.gene.name

    def test_celiac_secondary_risk_heterodimer(self):
        """DQ2.2 confers lower celiac risk than DQ2.5."""
        result = parse("DQ2.2")
        assert isinstance(result, Pair)

    def test_trans_contributing_heterodimer(self):
        """DQ7.5 can contribute to trans-encoded DQ2.5 formation."""
        result = parse("DQ7.5")
        assert isinstance(result, Pair)
        # DQ7.5 shares the alpha chain with DQ2.5
        assert result.alpha.allele_fields[0] == "05"


class TestIEDBOccurrencePatterns:
    """
    Test all heterodimer patterns found in IEDB mhc_ligand_full.csv.

    Occurrence counts:
        DQ2.2:  45,950
        DQ7.5:  45,944
        DQ2.5:  43,167
        DQ3.1:      47
        DQ2.3:      14
        DQ8.5:       2
        DQ2.25:      1 (likely typo)
        DQ2.22:      1 (likely typo)
    """

    @pytest.mark.parametrize(
        "shorthand,count",
        [
            ("DQ2.2", 45950),
            ("DQ7.5", 45944),
            ("DQ2.5", 43167),
            ("DQ3.1", 47),
            ("DQ2.3", 14),
            ("DQ8.5", 2),
        ],
    )
    def test_iedb_heterodimer_patterns(self, shorthand, count):
        """All heterodimer patterns from IEDB should parse as Pair."""
        result = parse(shorthand)
        assert isinstance(result, Pair), (
            f"{shorthand} ({count} occurrences in IEDB) should parse as Pair"
        )

    def test_rare_iedb_variants_are_typos(self):
        """DQ2.22 and DQ2.25 (1 occurrence each) are likely typos."""
        # These appear only once in IEDB and don't follow standard naming
        # DQ2.22 - might be typo for DQ2.2
        # DQ2.25 - might be typo for DQ2.5 or DQ2.2/DQ2.5
        # We don't need to support these
        pass
