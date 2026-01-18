# Comprehensive tests using real-world HLA allele formats encountered in the wild
#
# These tests cover various API methods on alleles commonly seen in:
# - IEDB database
# - NetMHCpan input/output
# - Clinical HLA typing reports
# - Research publications
# - UniProt descriptions

import pytest

from mhcgnomes import (
    Allele,
    Gene,
    MhcClass,
    Pair,
    ParseError,
    Serotype,
    Species,
    parse,
)

from .common import eq_

# ============================================================================
# Standard HLA Class I alleles - the most common formats
# ============================================================================


class TestStandardClassIAlleles:
    """Tests for standard HLA Class I allele formats."""

    # Common alleles seen in immunology research
    STANDARD_CLASS1_ALLELES = [
        # (input, expected_gene, expected_fields, expected_annotations)
        ("HLA-A*02:01", "A", ("02", "01"), ()),
        ("HLA-A*01:01", "A", ("01", "01"), ()),
        ("HLA-A*03:01", "A", ("03", "01"), ()),
        ("HLA-A*11:01", "A", ("11", "01"), ()),
        ("HLA-A*24:02", "A", ("24", "02"), ()),
        ("HLA-B*07:02", "B", ("07", "02"), ()),
        ("HLA-B*08:01", "B", ("08", "01"), ()),
        ("HLA-B*15:01", "B", ("15", "01"), ()),
        ("HLA-B*27:05", "B", ("27", "05"), ()),
        ("HLA-B*35:01", "B", ("35", "01"), ()),
        ("HLA-B*44:02", "B", ("44", "02"), ()),
        ("HLA-B*44:03", "B", ("44", "03"), ()),
        ("HLA-B*51:01", "B", ("51", "01"), ()),
        ("HLA-B*57:01", "B", ("57", "01"), ()),  # Associated with HIV control
        ("HLA-C*01:02", "C", ("01", "02"), ()),
        ("HLA-C*03:04", "C", ("03", "04"), ()),
        ("HLA-C*04:01", "C", ("04", "01"), ()),
        ("HLA-C*05:01", "C", ("05", "01"), ()),
        ("HLA-C*06:02", "C", ("06", "02"), ()),  # Psoriasis association
        ("HLA-C*07:01", "C", ("07", "01"), ()),
        ("HLA-C*07:02", "C", ("07", "02"), ()),
    ]

    @pytest.mark.parametrize("allele_str,gene,fields,annotations", STANDARD_CLASS1_ALLELES)
    def test_parse_standard_class1(self, allele_str, gene, fields, annotations):
        """Parse standard Class I alleles and verify all properties."""
        result = parse(allele_str)
        assert result is not None, f"Failed to parse {allele_str}"
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)
        eq_(result.annotations, annotations)
        assert result.is_class1
        assert not result.is_class2
        assert result.species.is_human

    @pytest.mark.parametrize("allele_str,gene,fields,annotations", STANDARD_CLASS1_ALLELES)
    def test_to_string_roundtrip(self, allele_str, gene, fields, annotations):
        """Parse and convert back to string - should be normalizable."""
        result = parse(allele_str)
        output = result.to_string()
        # Re-parse the output
        reparsed = parse(output)
        eq_(result, reparsed)

    @pytest.mark.parametrize("allele_str,gene,fields,annotations", STANDARD_CLASS1_ALLELES)
    def test_compact_string(self, allele_str, gene, fields, annotations):
        """Test compact string output without separators."""
        result = parse(allele_str)
        compact = result.compact_string(include_species=True)
        # Compact string should not have * or : in allele portion
        assert ":" not in compact.split("*")[-1] if "*" in compact else True

    @pytest.mark.parametrize("allele_str,gene,fields,annotations", STANDARD_CLASS1_ALLELES)
    def test_to_record(self, allele_str, gene, fields, annotations):
        """Test dictionary record output."""
        result = parse(allele_str)
        record = result.to_record()
        assert "gene" in record
        assert "allele" in record
        assert "species_prefix" in record
        # gene field includes species prefix (e.g., "HLA-A" not just "A")
        assert gene in record["gene"]


# ============================================================================
# Four-field (8-digit) alleles - full resolution typing
# ============================================================================


class TestFourFieldAlleles:
    """Tests for full 4-field allele designations."""

    FOUR_FIELD_ALLELES = [
        "HLA-A*02:01:01:01",
        "HLA-A*01:01:01:01",
        "HLA-B*07:02:01:01",
        "HLA-B*08:01:01:01",
        "HLA-B*15:01:01:01",
        "HLA-C*07:02:01:01",
        "HLA-DRB1*01:01:01:01",
        "HLA-DRB1*03:01:01:01",
        "HLA-DRB1*04:01:01:01",
        "HLA-DQB1*02:01:01:01",
    ]

    @pytest.mark.parametrize("allele_str", FOUR_FIELD_ALLELES)
    def test_parse_four_field(self, allele_str):
        """Parse 4-field alleles."""
        result = parse(allele_str)
        assert result is not None
        assert type(result) is Allele
        eq_(len(result.allele_fields), 4)

    @pytest.mark.parametrize("allele_str", FOUR_FIELD_ALLELES)
    def test_restrict_allele_fields(self, allele_str):
        """Test restricting allele fields to lower resolution."""
        result = parse(allele_str)

        # Restrict to 2 fields
        two_field = result.restrict_allele_fields(2)
        eq_(len(two_field.allele_fields), 2)
        eq_(two_field.allele_fields, result.allele_fields[:2])

        # Restrict to 1 field (allele group only)
        one_field = result.restrict_allele_fields(1)
        eq_(len(one_field.allele_fields), 1)


# ============================================================================
# Alleles with expression annotations (N, L, S, C, A, Q)
# ============================================================================


class TestAnnotatedAlleles:
    """Tests for alleles with functional annotations."""

    ANNOTATED_ALLELES = [
        # Null alleles (not expressed)
        ("HLA-A*02:15N", "A", ("02", "15"), ("N",), "annotation_null"),
        ("HLA-B*15:01N", "B", ("15", "01"), ("N",), "annotation_null"),
        ("HLA-B*44:02:01:02N", "B", ("44", "02", "01", "02"), ("N",), "annotation_null"),
        # Low expression
        ("HLA-A*24:02L", "A", ("24", "02"), ("L",), "annotation_low_expression"),
        ("HLA-B*44:02L", "B", ("44", "02"), ("L",), "annotation_low_expression"),
        # Secreted (soluble)
        ("HLA-A*24:02S", "A", ("24", "02"), ("S",), "annotation_secreted"),
        # Cytoplasmic (not on cell surface)
        ("HLA-B*44:02C", "B", ("44", "02"), ("C",), "annotation_cystosolic"),
        # Questionable
        ("HLA-A*02:01Q", "A", ("02", "01"), ("Q",), "annotation_questionable"),
        # Aberrant expression
        ("HLA-A*02:01A", "A", ("02", "01"), ("A",), "annotation_aberrant_expression"),
    ]

    @pytest.mark.parametrize("allele_str,gene,fields,annotations,attr", ANNOTATED_ALLELES)
    def test_parse_annotated_allele(self, allele_str, gene, fields, annotations, attr):
        """Parse alleles with expression annotations."""
        result = parse(allele_str)
        assert result is not None, f"Failed to parse {allele_str}"
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)
        eq_(result.annotations, annotations)
        # Check the annotation property
        assert getattr(result, attr) is True


# ============================================================================
# HLA Class II alleles - alpha/beta chains
# ============================================================================


class TestClassIIAlleles:
    """Tests for HLA Class II allele formats."""

    CLASS2_BETA_ALLELES = [
        # DR locus
        ("HLA-DRB1*01:01", "DRB1", ("01", "01")),
        ("HLA-DRB1*03:01", "DRB1", ("03", "01")),
        ("HLA-DRB1*04:01", "DRB1", ("04", "01")),
        ("HLA-DRB1*04:04", "DRB1", ("04", "04")),
        ("HLA-DRB1*07:01", "DRB1", ("07", "01")),
        ("HLA-DRB1*11:01", "DRB1", ("11", "01")),
        ("HLA-DRB1*13:01", "DRB1", ("13", "01")),
        ("HLA-DRB1*15:01", "DRB1", ("15", "01")),  # MS association
        ("HLA-DRB3*01:01", "DRB3", ("01", "01")),
        ("HLA-DRB4*01:01", "DRB4", ("01", "01")),
        ("HLA-DRB5*01:01", "DRB5", ("01", "01")),
        # DQ locus
        ("HLA-DQB1*02:01", "DQB1", ("02", "01")),
        ("HLA-DQB1*03:01", "DQB1", ("03", "01")),
        ("HLA-DQB1*03:02", "DQB1", ("03", "02")),  # T1D association
        ("HLA-DQB1*05:01", "DQB1", ("05", "01")),
        ("HLA-DQB1*06:02", "DQB1", ("06", "02")),
        # DP locus
        ("HLA-DPB1*01:01", "DPB1", ("01", "01")),
        ("HLA-DPB1*02:01", "DPB1", ("02", "01")),
        ("HLA-DPB1*04:01", "DPB1", ("04", "01")),
        ("HLA-DPB1*04:02", "DPB1", ("04", "02")),
    ]

    CLASS2_ALPHA_ALLELES = [
        ("HLA-DRA*01:01", "DRA", ("01", "01")),
        ("HLA-DRA*01:02", "DRA", ("01", "02")),
        ("HLA-DQA1*01:01", "DQA1", ("01", "01")),
        ("HLA-DQA1*01:02", "DQA1", ("01", "02")),
        ("HLA-DQA1*03:01", "DQA1", ("03", "01")),
        ("HLA-DQA1*05:01", "DQA1", ("05", "01")),
        ("HLA-DPA1*01:03", "DPA1", ("01", "03")),
        ("HLA-DPA1*02:01", "DPA1", ("02", "01")),
    ]

    @pytest.mark.parametrize("allele_str,gene,fields", CLASS2_BETA_ALLELES)
    def test_parse_class2_beta(self, allele_str, gene, fields):
        """Parse Class II beta chain alleles."""
        result = parse(allele_str)
        assert result is not None
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)
        assert result.is_class2
        assert result.is_class2_beta

    @pytest.mark.parametrize("allele_str,gene,fields", CLASS2_ALPHA_ALLELES)
    def test_parse_class2_alpha(self, allele_str, gene, fields):
        """Parse Class II alpha chain alleles."""
        result = parse(allele_str)
        assert result is not None
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)
        assert result.is_class2
        assert result.is_class2_alpha


# ============================================================================
# Class II alpha/beta pairs
# ============================================================================


class TestClassIIPairs:
    """Tests for Class II alpha/beta pair formats."""

    CLASS2_PAIRS = [
        # DR pairs
        ("HLA-DRA*01:01/DRB1*01:01", "DRA", "01:01", "DRB1", "01:01"),
        ("HLA-DRA*01:01/DRB1*03:01", "DRA", "01:01", "DRB1", "03:01"),
        ("HLA-DRA*01:01/DRB1*04:01", "DRA", "01:01", "DRB1", "04:01"),
        ("HLA-DRA*01:01/DRB1*15:01", "DRA", "01:01", "DRB1", "15:01"),
        # DQ pairs
        ("HLA-DQA1*01:02/DQB1*06:02", "DQA1", "01:02", "DQB1", "06:02"),
        ("HLA-DQA1*05:01/DQB1*02:01", "DQA1", "05:01", "DQB1", "02:01"),
        ("HLA-DQA1*03:01/DQB1*03:02", "DQA1", "03:01", "DQB1", "03:02"),
        # DP pairs
        ("HLA-DPA1*01:03/DPB1*04:01", "DPA1", "01:03", "DPB1", "04:01"),
        ("HLA-DPA1*02:01/DPB1*01:01", "DPA1", "02:01", "DPB1", "01:01"),
    ]

    @pytest.mark.parametrize("pair_str,alpha_gene,alpha_fields,beta_gene,beta_fields", CLASS2_PAIRS)
    def test_parse_class2_pair(self, pair_str, alpha_gene, alpha_fields, beta_gene, beta_fields):
        """Parse Class II alpha/beta pairs."""
        result = parse(pair_str)
        assert result is not None, f"Failed to parse {pair_str}"
        assert type(result) is Pair

        # Check alpha chain
        assert result.alpha is not None
        eq_(result.alpha.gene_name, alpha_gene)

        # Check beta chain
        assert result.beta is not None
        eq_(result.beta.gene_name, beta_gene)

    def test_pair_to_string_roundtrip(self):
        """Test that pair can be converted to string and reparsed."""
        pair_str = "HLA-DRA*01:01/DRB1*01:01"
        result = parse(pair_str)
        output = result.to_string()
        reparsed = parse(output)
        eq_(type(reparsed), Pair)


# ============================================================================
# Alternate input formats commonly seen in the wild
# ============================================================================


class TestAlternateFormats:
    """Tests for non-standard but common allele formats."""

    ALTERNATE_FORMATS = [
        # Without HLA prefix
        ("A*02:01", "A", ("02", "01")),
        ("B*07:02", "B", ("07", "02")),
        ("DRB1*01:01", "DRB1", ("01", "01")),
        # Lowercase
        ("hla-a*02:01", "A", ("02", "01")),
        ("hla-b*07:02", "B", ("07", "02")),
        # Without colons (compact format)
        ("HLA-A*0201", "A", ("02", "01")),
        ("HLA-B*0702", "B", ("07", "02")),
        ("A*0201", "A", ("02", "01")),
        # With underscore separator
        ("HLA-A_0201", "A", ("02", "01")),
        ("A_02_01", "A", ("02", "01")),
        # Ultra-compact (no separators)
        ("A0201", "A", ("02", "01")),
        ("B0702", "B", ("07", "02")),
        # Three-digit allele groups (high-resolution typing)
        ("HLA-B*15:120", "B", ("15", "120")),
        ("HLA-A*02:101", "A", ("02", "101")),
    ]

    @pytest.mark.parametrize("allele_str,gene,fields", ALTERNATE_FORMATS)
    def test_parse_alternate_format(self, allele_str, gene, fields):
        """Parse alternate allele formats."""
        result = parse(allele_str)
        assert result is not None, f"Failed to parse {allele_str}"
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)


# ============================================================================
# Serotypes (serological typing)
# ============================================================================


class TestSerotypes:
    """Tests for serological type designations."""

    SEROTYPES = [
        ("HLA-A2", "A2"),
        ("HLA-A1", "A1"),
        ("HLA-A3", "A3"),
        ("HLA-B7", "B7"),
        ("HLA-B8", "B8"),
        ("HLA-B27", "B27"),
        ("HLA-B35", "B35"),
        ("HLA-DR1", "DR1"),
        ("HLA-DR3", "DR3"),
        ("HLA-DR4", "DR4"),
        ("HLA-DR7", "DR7"),
        ("HLA-DQ2", "DQ2"),
    ]

    @pytest.mark.parametrize("sero_str,name", SEROTYPES)
    def test_parse_serotype(self, sero_str, name):
        """Parse serological types."""
        result = parse(sero_str)
        assert result is not None, f"Failed to parse {sero_str}"
        assert type(result) is Serotype
        eq_(result.name, name)
        assert result.species.is_human


# ============================================================================
# Mutations
# ============================================================================


class TestMutantAlleles:
    """Tests for alleles with point mutations."""

    def test_single_mutation(self):
        """Parse allele with single mutation."""
        result = parse("HLA-A*02:01 T80M mutant")
        assert result is not None
        assert result.is_mutant
        eq_(len(result.mutations), 1)
        eq_(result.mutations[0].aa_original, "T")
        eq_(result.mutations[0].pos, 80)
        eq_(result.mutations[0].aa_mutant, "M")

    def test_multiple_mutations(self):
        """Parse allele with multiple mutations."""
        result = parse("HLA-A*02:01 E152A, R155Y, L156Y mutant")
        assert result is not None
        assert result.is_mutant
        eq_(len(result.mutations), 3)

    def test_class2_pair_with_mutation(self):
        """Parse Class II pair with mutation on beta chain."""
        result = parse("HLA-DRA*01:01/DRB1*01:01 G86Y mutant")
        assert result is not None
        assert type(result) is Pair
        # Mutation should be on beta chain
        assert result.beta.is_mutant
        eq_(len(result.beta.mutations), 1)


# ============================================================================
# Non-classical HLA genes
# ============================================================================


class TestNonClassicalHLA:
    """Tests for non-classical HLA molecules."""

    NON_CLASSICAL_ALLELES = [
        # HLA-E
        ("HLA-E*01:01", "E", ("01", "01")),
        ("HLA-E*01:03", "E", ("01", "03")),
        # HLA-F
        ("HLA-F*01:01", "F", ("01", "01")),
        # HLA-G
        ("HLA-G*01:01", "G", ("01", "01")),
        ("HLA-G*01:04", "G", ("01", "04")),
        # MICA/MICB
        ("HLA-MICA*001", "MICA", ("001",)),
        ("HLA-MICA*002", "MICA", ("002",)),
        ("HLA-MICA*008", "MICA", ("008",)),
        ("HLA-MICB*002", "MICB", ("002",)),
    ]

    @pytest.mark.parametrize("allele_str,gene,fields", NON_CLASSICAL_ALLELES)
    def test_parse_non_classical(self, allele_str, gene, fields):
        """Parse non-classical HLA alleles."""
        result = parse(allele_str)
        assert result is not None, f"Failed to parse {allele_str}"
        assert type(result) is Allele
        eq_(result.gene_name, gene)
        eq_(result.allele_fields, fields)


# ============================================================================
# Gene-level parsing (without allele designation)
# ============================================================================


class TestGeneParsing:
    """Tests for gene-level parsing."""

    GENES = [
        ("HLA-A", "A"),
        ("HLA-B", "B"),
        ("HLA-C", "C"),
        ("HLA-DRA", "DRA"),
        ("HLA-DRB1", "DRB1"),
        ("HLA-DQA1", "DQA1"),
        ("HLA-DQB1", "DQB1"),
        ("HLA-DPA1", "DPA1"),
        ("HLA-DPB1", "DPB1"),
    ]

    @pytest.mark.parametrize("gene_str,name", GENES)
    def test_parse_gene(self, gene_str, name):
        """Parse gene names."""
        result = parse(gene_str)
        assert result is not None, f"Failed to parse {gene_str}"
        assert type(result) is Gene
        eq_(result.name, name)


# ============================================================================
# MHC Class parsing
# ============================================================================


class TestMhcClassParsing:
    """Tests for MHC class-level parsing."""

    def test_parse_hla_class_i(self):
        """Parse HLA Class I."""
        result = parse("HLA class I")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class1

    def test_parse_hla_class_ii(self):
        """Parse HLA Class II."""
        result = parse("HLA class II")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class2


# ============================================================================
# Species parsing
# ============================================================================


class TestSpeciesParsing:
    """Tests for species-level parsing."""

    def test_parse_hla_species(self):
        """Parse HLA as species."""
        result = parse("HLA")
        assert result is not None
        assert type(result) is Species
        assert result.is_human

    def test_species_from_allele(self):
        """Verify species is correctly identified from allele."""
        result = parse("HLA-A*02:01")
        assert result.species.is_human
        eq_(result.species.prefix, "HLA")


# ============================================================================
# Error handling
# ============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    INVALID_INPUTS = [
        "",  # Empty string
        "   ",  # Whitespace only
        "INVALID*99:99",  # Invalid gene
        "HLA-Z*01:01",  # Non-existent gene
    ]

    @pytest.mark.parametrize("invalid_str", INVALID_INPUTS)
    def test_parse_invalid_raises(self, invalid_str):
        """Invalid inputs should raise ParseError."""
        with pytest.raises(ParseError):
            parse(invalid_str)

    @pytest.mark.parametrize("invalid_str", INVALID_INPUTS)
    def test_parse_invalid_returns_none(self, invalid_str):
        """Invalid inputs should return None with raise_on_error=False."""
        result = parse(invalid_str, raise_on_error=False)
        assert result is None


# ============================================================================
# Edge cases and boundary conditions
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_allele_with_leading_zeros(self):
        """Alleles with leading zeros should be preserved."""
        result = parse("HLA-A*01:01")
        eq_(result.allele_fields, ("01", "01"))
        # Verify leading zeros preserved in output
        assert "01:01" in result.to_string()

    def test_very_long_allele_name(self):
        """Parse 4-field allele with all fields."""
        result = parse("HLA-A*02:01:01:01")
        eq_(len(result.allele_fields), 4)

    def test_allele_equality(self):
        """Two alleles parsed from same string should be equal."""
        a1 = parse("HLA-A*02:01")
        a2 = parse("HLA-A*02:01")
        eq_(a1, a2)
        assert hash(a1) == hash(a2)

    def test_allele_inequality_different_fields(self):
        """Alleles with different fields should not be equal."""
        a1 = parse("HLA-A*02:01")
        a2 = parse("HLA-A*02:02")
        assert a1 != a2

    def test_allele_inequality_different_genes(self):
        """Alleles from different genes should not be equal."""
        a1 = parse("HLA-A*02:01")
        a2 = parse("HLA-B*02:01")
        assert a1 != a2

    def test_case_insensitivity(self):
        """Parsing should be case insensitive."""
        upper = parse("HLA-A*02:01")
        lower = parse("hla-a*02:01")
        mixed = parse("Hla-A*02:01")
        eq_(upper, lower)
        eq_(upper, mixed)


# ============================================================================
# Real-world clinical/research scenarios
# ============================================================================


class TestRealWorldScenarios:
    """Tests simulating real-world usage scenarios."""

    def test_clinical_typing_report(self):
        """Simulate parsing a clinical HLA typing report."""
        typing_results = [
            "HLA-A*02:01",
            "HLA-A*03:01",
            "HLA-B*07:02",
            "HLA-B*44:02",
            "HLA-C*05:01",
            "HLA-C*07:02",
            "HLA-DRB1*03:01",
            "HLA-DRB1*07:01",
            "HLA-DQB1*02:01",
            "HLA-DQB1*03:03",
        ]

        for allele_str in typing_results:
            result = parse(allele_str)
            assert result is not None
            assert type(result) is Allele
            assert result.species.is_human

    def test_netmhcpan_output_format(self):
        """Parse alleles in NetMHCpan output format."""
        netmhcpan_alleles = [
            "HLA-A02:01",  # NetMHCpan sometimes omits the *
            "HLA-B07:02",
            "HLA-B57:01",
        ]

        for allele_str in netmhcpan_alleles:
            result = parse(allele_str)
            assert result is not None

    def test_iedb_format(self):
        """Parse alleles in IEDB format."""
        iedb_alleles = [
            "HLA-A*02:01",
            "HLA-A*0201",  # IEDB sometimes uses compact format
            "H-2-Kb",  # Mouse
            "H-2-Db",
        ]

        for allele_str in iedb_alleles:
            result = parse(allele_str)
            assert result is not None

    def test_disease_association_alleles(self):
        """Parse alleles commonly associated with diseases."""
        disease_alleles = {
            "HLA-B*27:05": "Ankylosing spondylitis",
            "HLA-DRB1*15:01": "Multiple sclerosis",
            "HLA-DQB1*03:02": "Type 1 diabetes",
            "HLA-C*06:02": "Psoriasis",
            "HLA-B*57:01": "HIV control / Abacavir hypersensitivity",
            "HLA-B*58:01": "Allopurinol hypersensitivity",
            "HLA-DRB1*04:01": "Rheumatoid arthritis",
        }

        for allele_str, disease in disease_alleles.items():
            result = parse(allele_str)
            assert result is not None, f"Failed to parse {allele_str} ({disease})"
            assert type(result) is Allele
