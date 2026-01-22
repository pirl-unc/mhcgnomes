"""
Tests for handling nonsense and malformed inputs.

These tests verify that mhcgnomes gracefully handles invalid inputs
without crashing, and documents the parser's behavior with edge cases.

The parser is intentionally lenient to handle the many variations
found in real-world data (different separators, case variations, etc.).
"""

import pytest

from mhcgnomes import parse
from mhcgnomes.allele import Allele
from mhcgnomes.errors import ParseError
from mhcgnomes.gene import Gene
from mhcgnomes.species import Species


class TestCompleteNonsense:
    """Tests for completely invalid inputs that should be rejected."""

    @pytest.mark.parametrize(
        "inp",
        [
            # Random strings
            "asdfghjkl",
            "hello world",
            "12345",
            "!!!@@@###",
            # Empty/whitespace
            "",
            "   ",
            # Other genes
            "BRCA1",
            "TP53",
            "KIR2DL1",
            "CD4",
            "CD8",
            # Injection attempts (should fail, not crash)
            "'; DROP TABLE alleles;--",
            "<script>alert('xss')</script>",
            # Unicode
            "🧬",
            "HLA-Ä1",
        ],
    )
    def test_nonsense_raises_parse_error(self, inp):
        """Complete nonsense should raise ParseError, not crash."""
        with pytest.raises(ParseError):
            parse(inp)

    @pytest.mark.parametrize(
        "inp",
        [
            "null",
            "None",
            "undefined",
            "NaN",
        ],
    )
    def test_null_like_strings_rejected(self, inp):
        """Strings that look like null values should be rejected."""
        with pytest.raises(ParseError):
            parse(inp)


class TestPartialInputs:
    """Tests for partial/incomplete inputs."""

    def test_hla_prefix_alone_returns_species(self):
        """Just 'HLA' should return the Species object."""
        result = parse("HLA")
        assert isinstance(result, Species)
        assert result.prefix == "HLA"

    def test_hla_with_dash_returns_species(self):
        """'HLA-' (with trailing dash) returns Species."""
        result = parse("HLA-")
        assert isinstance(result, Species)

    def test_gene_without_allele_returns_gene(self):
        """'HLA-A*' (gene without allele fields) returns Gene."""
        result = parse("HLA-A*")
        assert isinstance(result, Gene)
        assert result.name == "A"

    @pytest.mark.parametrize(
        "inp",
        [
            "HLA-X",  # X is not a valid gene
            "HLA-Z99",
            "Z*01:01",  # Z is not a valid gene letter
        ],
    )
    def test_invalid_genes_rejected(self, inp):
        """Invalid gene names should be rejected."""
        with pytest.raises(ParseError):
            parse(inp)


class TestMalformedAlleles:
    """Tests for malformed allele strings."""

    @pytest.mark.parametrize(
        "inp",
        [
            "A*:01",  # Empty first field
            "A*01:",  # Empty second field
            "A*AB:CD",  # Letters instead of numbers
            "A*01.5:01",  # Decimal number
            "A*01:01:01:01:01:01",  # Too many fields (6)
        ],
    )
    def test_clearly_malformed_rejected(self, inp):
        """Clearly malformed allele strings should be rejected."""
        with pytest.raises(ParseError):
            parse(inp)


class TestLenientParsing:
    """
    Tests documenting the parser's lenient behavior.

    The parser is intentionally flexible to handle real-world data variations.
    These tests document what IS accepted (not necessarily what SHOULD be).
    """

    def test_fake_allele_numbers_accepted(self):
        """
        Fake allele numbers are accepted - no database validation.

        This is by design: the parser doesn't validate against the IMGT/HLA
        database. It accepts any syntactically valid allele string.
        """
        result = parse("A*99:99")
        assert isinstance(result, Allele)
        assert result.allele_fields == ("99", "99")

    def test_zero_allele_fields_accepted(self):
        """
        A*00:00 is accepted even though it's not a real allele.

        This might be undesirable but is current behavior.
        """
        result = parse("A*00:00")
        assert isinstance(result, Allele)
        assert result.allele_fields == ("00", "00")

    def test_various_field_lengths_accepted(self):
        """Different allele field lengths are accepted."""
        # Single digit
        r1 = parse("A*1:1")
        assert r1.allele_fields == ("1", "1")

        # Two digit (standard)
        r2 = parse("A*01:01")
        assert r2.allele_fields == ("01", "01")

        # Three digit
        r3 = parse("A*001:001")
        assert r3.allele_fields == ("001", "001")

    def test_underscore_separator_normalized(self):
        """Underscore separators are accepted and normalized to colons."""
        result = parse("A*01_01")
        assert isinstance(result, Allele)
        assert result.to_string() == "HLA-A*01:01"

    def test_flexible_species_separator(self):
        """Parser accepts various separators after species prefix."""
        # Standard
        r1 = parse("HLA-A*01:01")
        # Asterisk instead of dash
        r2 = parse("HLA*A*01:01")
        # Colon instead of dash
        r3 = parse("HLA:A:01:01")

        # All should produce equivalent results
        assert r1.to_string() == r2.to_string() == r3.to_string() == "HLA-A*01:01"

    def test_unknown_annotation_accepted(self):
        """
        Unknown annotation suffixes are accepted.

        Valid annotations: N (null), L (low), S (secreted), Q (questionable), A (aberrant)
        But parser accepts any single letter.
        """
        result = parse("A*01:01X")
        assert isinstance(result, Allele)


class TestCaseInsensitivity:
    """Tests for case-insensitive parsing."""

    @pytest.mark.parametrize(
        "inp",
        [
            "HLA",
            "hla",
            "Hla",
            "hLa",
        ],
    )
    def test_species_case_insensitive(self, inp):
        """Species prefix should be case-insensitive."""
        result = parse(inp)
        assert isinstance(result, Species)

    @pytest.mark.parametrize(
        "inp",
        [
            "HLA-A2",
            "hla-a2",
            "HLA-a2",
            "Hla-A2",
        ],
    )
    def test_serotype_case_insensitive(self, inp):
        """Serotype parsing should be case-insensitive."""
        result = parse(inp)
        assert result.name == "A2"


class TestSpreadsheetNomenclature:
    """Tests for nomenclature variations commonly seen in spreadsheets."""

    @pytest.mark.parametrize(
        "inp,expected_type",
        [
            # Mouse H2 haplotypes - various formats
            ("H2k", "Gene"),
            ("H-2k", "Gene"),
            ("H2-k", "Gene"),
            ("H-2-k", "Gene"),
            ("haplotype H2k", "Haplotype"),
            ("H2k haplotype", "Haplotype"),
            # Human with "serotype" keyword
            ("HLA-A2 serotype", "Serotype"),
            ("serotype A2", "Serotype"),
            # MHC class descriptors
            ("HLA class I", "MhcClass"),
            ("HLA class II", "MhcClass"),
            ("MHC class I", "MhcClass"),
            ("class I HLA", "MhcClass"),
            # Rat RT1
            ("RT1", "Species"),
            ("RT1-A", "Gene"),
            # Multi-field alleles
            ("HLA-A*02:01:01:01", "Allele"),
            ("A*02:01:01:01", "Allele"),
            ("HLA-DRB1*04:01", "Allele"),
            ("DRB1*0401", "Allele"),
            # Alleles with annotations
            ("HLA-A*01:01N", "Allele"),
            ("A*24:02:01:02L", "Allele"),
        ],
    )
    def test_spreadsheet_nomenclature_accepted(self, inp, expected_type):
        """Common spreadsheet nomenclature should parse correctly."""
        result = parse(inp)
        assert type(result).__name__ == expected_type, f"{inp} should parse as {expected_type}"

    @pytest.mark.parametrize(
        "inp",
        [
            "A2 antigen",  # "antigen" suffix not supported
            "HLA-B27 antigen",
        ],
    )
    def test_unsupported_nomenclature_rejected(self, inp):
        """Some nomenclature variations are not supported."""
        with pytest.raises(ParseError):
            parse(inp)

    @pytest.mark.parametrize(
        "inp,expected_name",
        [
            ("B17.1", "B17.1"),
            ("B17.2", "B17.2"),
            ("B17.3", "B17.3"),
            ("HLA-B17.1", "B17.1"),
        ],
    )
    def test_b17_subsplits_with_dots(self, inp, expected_name):
        """B17 subsplits use dot notation and should parse."""
        from mhcgnomes.serotype import Serotype

        result = parse(inp)
        assert isinstance(result, Serotype)
        assert result.name == expected_name


class TestDQDRHeterodimers:
    """
    Tests for HLA-DQ heterodimer dot nomenclature.

    For comprehensive heterodimer tests, see tests/test_heterodimers.py.

    This class only contains basic sanity checks to document that:
    1. DQ2 (without dot) parses as Serotype
    2. DQ2.5 (with dot) should parse as Pair (heterodimer) - currently xfail
    """

    def test_dq2_without_dot_is_serotype(self):
        """DQ2 without dot notation parses as Serotype."""
        from mhcgnomes.serotype import Serotype

        result = parse("DQ2")
        assert isinstance(result, Serotype)
        assert result.name == "DQ2"

    def test_dq2_5_with_dot_is_pair(self):
        """DQ2.5 with dot notation should parse as Pair (heterodimer)."""
        from mhcgnomes.pair import Pair

        result = parse("DQ2.5")
        assert isinstance(result, Pair)


class TestNonHLAGenes:
    """Tests confirming that non-HLA/MHC genes are rejected."""

    @pytest.mark.parametrize(
        "inp",
        [
            "BRCA1",
            "BRCA2",
            "TP53",
            "EGFR",
            "KRAS",
            "insulin",
            "hemoglobin",
            "COVID-19",
            "SARS-CoV-2",
        ],
    )
    def test_non_mhc_genes_rejected(self, inp):
        """Non-MHC gene names should be rejected."""
        with pytest.raises(ParseError):
            parse(inp)
