# Tests for uncovered edge cases in parser.py
#
# These tests target specific uncovered lines and edge cases identified
# by coverage analysis.

from mhcgnomes import (
    Allele,
    Class2Locus,
    Gene,
    Haplotype,
    MhcClass,
    Mutation,
    Pair,
    Parser,
    Serotype,
    Species,
    parse,
)
from mhcgnomes.token import Token
from mhcgnomes.tokenize import tokenize

from .common import eq_

# ============================================================================
# get_serotype edge cases
# ============================================================================


class TestGetSerotype:
    """Tests for Parser.get_serotype edge cases."""

    def test_get_serotype_invalid_species(self):
        """get_serotype should return None for invalid species."""
        parser = Parser()
        result = parser.get_serotype("INVALID_SPECIES", "A2")
        assert result is None

    def test_get_serotype_invalid_serotype_name(self):
        """get_serotype should return None for invalid serotype name."""
        parser = Parser()
        result = parser.get_serotype("HLA", "INVALID999")
        assert result is None


# ============================================================================
# create_crossed_haplotype edge cases
# ============================================================================


class TestCreateCrossedHaplotype:
    """Tests for Parser.create_crossed_haplotype edge cases."""

    def test_create_crossed_haplotype_none_first(self):
        """create_crossed_haplotype with None first haplotype returns None."""
        parser = Parser()
        result = parser.create_crossed_haplotype(None, "k")
        assert result is None

    def test_create_crossed_haplotype_empty_second(self):
        """create_crossed_haplotype with empty second name returns None."""
        parser = Parser()
        first = parser.get_haplotype("H2", "b")
        assert first is not None
        result = parser.create_crossed_haplotype(first, "")
        assert result is None

    def test_create_crossed_haplotype_non_alnum_second(self):
        """create_crossed_haplotype with non-alphanumeric second name returns None."""
        parser = Parser()
        first = parser.get_haplotype("H2", "b")
        assert first is not None
        result = parser.create_crossed_haplotype(first, "k@#$")
        assert result is None

    def test_create_crossed_haplotype_invalid_second(self):
        """create_crossed_haplotype with invalid second haplotype returns None."""
        parser = Parser()
        first = parser.get_haplotype("H2", "b")
        assert first is not None
        result = parser.create_crossed_haplotype(first, "invalidhaplotype")
        assert result is None

    def test_create_crossed_haplotype_success(self):
        """create_crossed_haplotype successfully creates crossed haplotype."""
        parser = Parser()
        first = parser.get_haplotype("H2", "b")
        assert first is not None
        result = parser.create_crossed_haplotype(first, "d")
        assert result is not None
        assert type(result) is Haplotype
        assert "b" in result.name and "d" in result.name


# ============================================================================
# parse_allele_from_allele_fields edge cases
# ============================================================================


class TestParseAlleleFromAlleleFields:
    """Tests for Parser.parse_allele_from_allele_fields edge cases."""

    def test_allele_fields_none(self):
        """parse_allele_from_allele_fields with None fields returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_from_allele_fields(gene, None)
        assert result is None

    def test_allele_fields_empty(self):
        """parse_allele_from_allele_fields with empty fields returns gene."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_from_allele_fields(gene, [])
        eq_(result, gene)

    def test_allele_fields_too_many(self):
        """parse_allele_from_allele_fields with >4 fields returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        # Pass functional_annotations to skip the annotation parsing step
        result = parser.parse_allele_from_allele_fields(
            gene, ["01", "01", "01", "01", "01"], functional_annotations=[]
        )
        assert result is None

    def test_allele_field_with_asterisk(self):
        """parse_allele_from_allele_fields with '*' in field returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_from_allele_fields(
            gene, ["02", "01"], functional_annotations=["*"]
        )
        # The asterisk in annotations won't cause None, let's test the field check
        # by using parse_allele_with_gene which calls this
        result = parser.parse_allele_with_gene(gene, "02*01")
        assert result is None

    def test_allele_field_with_dash(self):
        """parse_allele_with_gene with '-' in string properly handles it."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_with_gene(gene, "02-01")
        assert isinstance(result, Allele)
        assert result.to_string() == "HLA-A*02:01"
        # May or may not return None depending on parsing

    def test_human_allele_non_digit_field(self):
        """Human allele with non-digit field returns None via parse_allele_with_gene."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        # Use the high-level function that validates fields
        result = parser.parse_allele_from_allele_fields(
            gene, ["02", "AB"], functional_annotations=[]
        )
        assert result is None

    def test_chicken_allele_with_letters(self):
        """Chicken allele with letters in field returns None."""
        parser = Parser()
        gene = Gene.get("chicken", "BF2")
        assert gene is not None
        result = parser.parse_allele_from_allele_fields(gene, ["12AB"], functional_annotations=[])
        assert result is None


# ============================================================================
# get_gene_or_locus edge cases
# ============================================================================


class TestGetGeneOrLocus:
    """Tests for Parser.get_gene_or_locus edge cases."""

    def test_get_gene_or_locus_returns_gene(self):
        """get_gene_or_locus returns Gene when found."""
        parser = Parser()
        result = parser.get_gene_or_locus("HLA", "A")
        assert result is not None
        assert type(result) is Gene

    def test_get_gene_or_locus_returns_locus(self):
        """get_gene_or_locus returns Class2Locus when found."""
        parser = Parser()
        result = parser.get_gene_or_locus("HLA", "DR")
        assert result is not None
        assert type(result) is Class2Locus

    def test_get_gene_or_locus_returns_none(self):
        """get_gene_or_locus returns None when not found."""
        parser = Parser()
        result = parser.get_gene_or_locus("HLA", "INVALIDGENENAME")
        assert result is None


# ============================================================================
# parse_allele_with_gene edge cases
# ============================================================================


class TestParseAlleleWithGene:
    """Tests for Parser.parse_allele_with_gene edge cases."""

    def test_parse_allele_with_gene_none_gene(self):
        """parse_allele_with_gene with None gene returns None."""
        parser = Parser()
        result = parser.parse_allele_with_gene(None, "0201")
        assert result is None

    def test_parse_allele_with_gene_empty_string(self):
        """parse_allele_with_gene with empty string returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_with_gene(gene, "")
        assert result is None

    def test_parse_allele_with_gene_whitespace(self):
        """parse_allele_with_gene with whitespace returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_with_gene(gene, "02 01")
        assert result is None

    def test_parse_allele_with_gene_asterisk(self):
        """parse_allele_with_gene with asterisk in string returns None."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_with_gene(gene, "02*01")
        assert result is None

    def test_parse_pig_allele_with_hash(self):
        """parse_allele_with_gene handles pig alleles with # symbol."""
        parser = Parser()
        gene = Gene.get("SLA", "3")
        assert gene is not None
        result = parser.parse_allele_with_gene(gene, "US#11")
        assert isinstance(result, Allele)
        assert result.gene == gene


# ============================================================================
# parse_class2_pair_from_alpha_and_beta_strings edge cases
# ============================================================================


class TestParseClass2PairFromStrings:
    """Tests for Parser.parse_class2_pair_from_alpha_and_beta_strings edge cases."""

    def test_alpha_parse_fails(self):
        """Returns None when alpha parse fails."""
        parser = Parser()
        result = parser.parse_class2_pair_from_alpha_and_beta_strings("INVALID", "DRB1*01:01")
        assert result is None

    def test_alpha_wrong_type(self):
        """Returns None when alpha is wrong type (not Allele/Gene)."""
        parser = Parser()
        # Parsing just "HLA" gives Species, not Allele/Gene
        result = parser.parse_class2_pair_from_alpha_and_beta_strings("HLA", "DRB1*01:01")
        assert result is None

    def test_require_alleles_alpha_is_gene(self):
        """Returns None when require_alleles=True but alpha is Gene."""
        parser = Parser()
        result = parser.parse_class2_pair_from_alpha_and_beta_strings(
            "HLA-DRA", "DRB1*01:01", require_alleles=True
        )
        assert result is None

    def test_require_alleles_beta_is_gene(self):
        """Returns None when require_alleles=True but beta is Gene."""
        parser = Parser()
        result = parser.parse_class2_pair_from_alpha_and_beta_strings(
            "HLA-DRA*01:01", "DRB1", require_alleles=True
        )
        assert result is None

    def test_species_mismatch(self):
        """Returns None when alpha and beta have different species."""
        parser = Parser()
        # This should fail because we're mixing species
        result = parser.parse_class2_pair_from_alpha_and_beta_strings(
            "HLA-DRA*01:01", "H2-Ab"
        )  # HLA vs H2
        assert result is None


# ============================================================================
# parse_mutations edge cases
# ============================================================================


class TestParseMutations:
    """Tests for Parser.parse_mutations edge cases."""

    def test_empty_mutation_string(self):
        """Empty mutation strings are skipped."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["", "  ", "G86Y"])
        assert result is not None
        mutations, _chain_to_mut, _gene_to_mut = result
        eq_(len(mutations), 1)

    def test_mutation_with_trailing_comma(self):
        """Mutation strings with trailing commas are handled."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["G86Y,"])
        assert result is not None
        mutations, _chain_to_mut, _gene_to_mut = result
        eq_(len(mutations), 1)

    def test_alpha_chain_selector(self):
        """Chain selector 'alpha' works."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["alpha", "G86Y"])
        assert result is not None
        _mutations, chain_to_mut, _gene_to_mut = result
        eq_(len(chain_to_mut["alpha"]), 1)

    def test_beta_chain_selector(self):
        """Chain selector 'beta' works."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["beta", "G86Y"])
        assert result is not None
        _mutations, chain_to_mut, _gene_to_mut = result
        eq_(len(chain_to_mut["beta"]), 1)

    def test_gene_selector_mutation(self):
        """Mutation with gene selector (gene:mutation) works."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["DRB1:G86Y"])
        assert result is not None
        _mutations, _chain_to_mut, gene_to_mut = result
        eq_(len(gene_to_mut), 1)

    def test_invalid_gene_selector(self):
        """Invalid gene selector returns None."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["INVALIDGENE:G86Y"])
        assert result is None

    def test_multiple_colons_in_mutation(self):
        """Multiple colons in mutation string returns None."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["A:B:C86Y"])
        assert result is None

    def test_invalid_mutation_format(self):
        """Invalid mutation format returns None."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_mutations(species, ["NOTAMUTATION"])
        assert result is None


# ============================================================================
# apply_mutations edge cases
# ============================================================================


class TestApplyMutations:
    """Tests for Parser.apply_mutations edge cases."""

    def test_no_mutations(self):
        """Returns None when no mutations to apply."""
        from collections import defaultdict

        parser = Parser()
        allele = parse("HLA-A*02:01")
        result = parser.apply_mutations(allele, [], defaultdict(list), defaultdict(list))
        assert result is None

    def test_gene_mismatch_in_gene_to_mutations(self):
        """Returns None when gene in gene_to_mutations doesn't match."""
        from collections import defaultdict

        parser = Parser()
        allele = parse("HLA-A*02:01")
        wrong_gene = Gene.get("HLA", "B")
        mut = Mutation.get(86, "G", "Y")
        gene_to_mut = defaultdict(list)
        gene_to_mut[wrong_gene] = [mut]
        result = parser.apply_mutations(allele, [], defaultdict(list), gene_to_mut)
        assert result is None

    def test_beta_mutations_on_class2_alpha(self):
        """Returns None when beta mutations applied to class2 alpha chain."""
        from collections import defaultdict

        parser = Parser()
        allele = parse("HLA-DRA*01:01")
        assert allele.is_class2_alpha
        mut = Mutation.get(86, "G", "Y")
        chain_to_mut = defaultdict(list)
        chain_to_mut["beta"] = [mut]
        result = parser.apply_mutations(allele, [], chain_to_mut, defaultdict(list))
        assert result is None

    def test_alpha_beta_mutations_on_class1(self):
        """Returns None when alpha/beta mutations applied to class I."""
        from collections import defaultdict

        parser = Parser()
        allele = parse("HLA-A*02:01")
        assert allele.is_class1
        mut = Mutation.get(86, "G", "Y")
        chain_to_mut = defaultdict(list)
        chain_to_mut["alpha"] = [mut]
        result = parser.apply_mutations(allele, [], chain_to_mut, defaultdict(list))
        assert result is None

    def test_unexpected_gene_in_pair(self):
        """Returns None when unexpected gene in pair mutations."""
        from collections import defaultdict

        parser = Parser()
        pair = parse("HLA-DRA*01:01/DRB1*01:01")
        wrong_gene = Gene.get("HLA", "A")
        mut = Mutation.get(86, "G", "Y")
        gene_to_mut = defaultdict(list)
        gene_to_mut[wrong_gene] = [mut]
        result = parser.apply_mutations(pair, [], defaultdict(list), gene_to_mut)
        assert result is None

    def test_unsupported_result_type(self):
        """Returns None for unsupported result type."""
        from collections import defaultdict

        parser = Parser()
        species = Species.get("HLA")
        mut = Mutation.get(86, "G", "Y")
        result = parser.apply_mutations(species, [mut], defaultdict(list), defaultdict(list))
        assert result is None


# ============================================================================
# parse() filtering options
# ============================================================================


class TestParseFilters:
    """Tests for Parser.parse filtering options."""

    def test_only_class1_filter(self):
        """only_class1 filter returns only class I results."""
        parser = Parser()
        # H2K can be parsed as both gene (class I) and haplotype
        result = parser.parse("H2K", only_class1=True)
        assert result is not None
        assert result.is_class1

    def test_only_class2_filter(self):
        """only_class2 filter returns only class II results."""
        parser = Parser()
        result = parser.parse("HLA-DRB1*01:01", only_class2=True)
        assert result is not None
        assert result.is_class2

    def test_required_result_types_single(self):
        """required_result_types with single type works."""
        parser = Parser()
        result = parser.parse("H2K", required_result_types=Gene)
        assert result is not None
        assert type(result) is Gene

    def test_required_result_types_list(self):
        """required_result_types with list works."""
        parser = Parser()
        result = parser.parse("H2K", required_result_types=[Gene, Haplotype])
        assert result is not None
        assert type(result) in (Gene, Haplotype)

    def test_preferred_result_types_single(self):
        """preferred_result_types with single type works."""
        parser = Parser()
        result = parser.parse("H2K", preferred_result_types=Haplotype)
        assert result is not None
        assert type(result) is Haplotype

    def test_preferred_result_types_list(self):
        """preferred_result_types with list works."""
        parser = Parser()
        result = parser.parse("HLA-A2", preferred_result_types=[Serotype])
        assert result is not None
        assert type(result) is Serotype

    def test_preferred_result_types_falls_back_when_no_match(self):
        """preferred_result_types falls back to non-preferred parse when needed."""
        parser = Parser()
        result = parser.parse("HLA-A*02:01", preferred_result_types=[Serotype])
        assert result is not None
        assert type(result) is Allele

    def test_required_result_types_is_strict(self):
        """required_result_types is strict and returns None when no type matches."""
        parser = Parser()
        result = parser.parse(
            "HLA-A*02:01",
            required_result_types=[Serotype],
            raise_on_error=False,
        )
        assert result is None

    def test_max_allele_fields(self):
        """max_allele_fields restricts allele resolution."""
        parser = Parser()
        result = parser.parse("HLA-A*02:01:01:01", max_allele_fields=2)
        assert result is not None
        assert type(result) is Allele
        eq_(len(result.allele_fields), 2)


# ============================================================================
# Token-based parsing edge cases
# ============================================================================


class TestTokenParsing:
    """Tests for token-based parsing edge cases."""

    def test_alpha_token_with_class1(self):
        """Parsing with 'alpha' token on class I allele."""
        result = parse("HLA-A*02:01 alpha")
        assert result is not None

    def test_beta_token_with_class2_beta(self):
        """Parsing with 'beta' token on class II beta allele."""
        result = parse("HLA-DRB1*01:01 beta")
        assert result is not None

    def test_class_token_at_start(self):
        """Parsing with class token at start."""
        result = parse("class I HLA")
        assert result is not None
        assert result.is_class1

    def test_class_token_at_end(self):
        """Parsing with class token at end."""
        result = parse("HLA class II")
        assert result is not None
        assert result.is_class2

    def test_haplotype_token_at_start(self):
        """Parsing with 'haplotype' token at start."""
        result = parse("haplotype H2-k")
        assert result is not None

    def test_haplotype_token_at_end(self):
        """Parsing with 'haplotype' token at end."""
        result = parse("H2-k haplotype")
        assert result is not None

    def test_gene_token_at_end(self):
        """Parsing with 'gene' token at end."""
        result = parse("HLA-A gene")
        assert result is not None
        assert type(result) is Gene

    def test_gene_token_at_start(self):
        """Parsing with 'gene' token at start."""
        result = parse("gene HLA-A")
        assert result is not None
        assert type(result) is Gene


# ============================================================================
# Slash-separated parsing edge cases
# ============================================================================


class TestSlashParsing:
    """Tests for slash-separated parsing edge cases."""

    def test_slash_nothing_before(self):
        """Parsing with nothing before slash returns None."""
        assert parse("/DRB1*01:01", raise_on_error=False) is None

    def test_slash_nothing_after(self):
        """Parsing with nothing after slash returns None without raising."""
        assert parse("DRA*01:01/", raise_on_error=False) is None

    def test_double_slash_rejected(self):
        """Parsing with consecutive slashes returns None."""
        assert parse("HLA-DRA*01:01//DRB1*01:01", raise_on_error=False) is None

    def test_spaced_slash_pair(self):
        """Spaces around '/' in a Class II pair should still parse as Pair."""
        result = parse("HLA-DRA*01:01 / HLA-DRB1*01:01", raise_on_error=True)
        assert type(result) is Pair
        eq_(result.alpha, Allele.get("HLA", "DRA", "01", "01"))
        eq_(result.beta, Allele.get("HLA", "DRB1", "01", "01"))

    def test_spaced_slash_per_chain_locus_labels(self):
        """Per-chain alpha/beta labels on both sides of '/' still form a Pair."""
        result = parse("HLA-DR alpha / HLA-DR beta", raise_on_error=True)
        assert type(result) is Pair
        eq_(result.alpha, Gene.get("HLA", "DRA"))
        eq_(result.beta, Gene.get("HLA", "DRB1"))

    def test_spaced_slash_per_chain_allele_labels(self):
        """Explicit alpha/beta labels on both alleles around '/' form a Pair."""
        result = parse("HLA-DRA*01:01 alpha / HLA-DRB1*01:01 beta", raise_on_error=True)
        assert type(result) is Pair
        eq_(result.alpha, Allele.get("HLA", "DRA", "01", "01"))
        eq_(result.beta, Allele.get("HLA", "DRB1", "01", "01"))

    def test_spaced_slash_crossed_haplotype(self):
        """Spaces around '/' in a crossed haplotype parse as Haplotype."""
        result = parse("H2-b / d", raise_on_error=True)
        assert type(result) is Haplotype
        eq_(result.name, "b/d")

    def test_crossed_haplotype(self):
        """Parsing crossed haplotype format."""
        result = parse("H2-b/d", raise_on_error=False)
        assert type(result) is Haplotype
        assert result.name == "b/d"

    def test_crossed_haplotype_with_class(self):
        """Parsing crossed haplotype with class restriction."""
        result = parse("H2-b/d class I", raise_on_error=False)
        assert isinstance(result, Haplotype)
        assert result.name == "b/d"
        assert result.class_restriction == "I"


# ============================================================================
# Haplotype parsing edge cases
# ============================================================================


class TestHaplotypeParsing:
    """Tests for haplotype parsing edge cases."""

    def test_haplotype_species_no_other_tokens(self):
        """Parsing 'haplotype H2' returns mouse Species."""
        result = parse("haplotype H2", raise_on_error=True)
        assert type(result) is Species
        eq_(result, Species.get("H2"))

    def test_haplotype_token_not_species(self):
        """Parsing 'haplotype k' resolves to the mouse H2-k haplotype."""
        result = parse("haplotype k", raise_on_error=False)
        assert isinstance(result, Haplotype)
        assert result.species.mhc_prefix == "H2"
        assert result.name == "k"


# ============================================================================
# Verbose mode
# ============================================================================


class TestVerboseMode:
    """Tests for verbose mode output."""

    def test_verbose_parse(self, capsys):
        """Verbose mode logs parsing output and still returns the parsed allele."""
        parser = Parser(verbose=True)
        result = parser.parse("HLA-A*02:01")
        captured = capsys.readouterr()
        assert isinstance(result, Allele)
        assert result.to_string() == "HLA-A*02:01"
        assert captured.out
        # Just verify it doesn't crash with verbose mode


# ============================================================================
# Transform edge cases
# ============================================================================


class TestTransformParseCandidates:
    """Tests for transform_parse_candidate edge cases."""

    def test_transform_none(self):
        """transform_parse_candidate with None returns None."""
        parser = Parser()
        result = parser.transform_parse_candidate(None)
        assert result is None

    def test_collapse_singleton_serotype(self):
        """Serotype with a single allele collapses to Allele when enabled."""
        parser = Parser(collapse_singleton_serotypes=True)
        collapsed = parser.parse("HLA-Aw69")
        assert isinstance(collapsed, Allele)
        assert collapsed.to_string() == "HLA-A*69:01"
        multi = parser.parse("HLA-A2")
        assert isinstance(multi, Serotype)
        # Result type depends on the serotype data

    def test_use_allele_aliases(self):
        """Parser with use_allele_aliases=True transforms alleles."""
        parser = Parser(use_allele_aliases=True)
        # This should use allele aliases if available
        result = parser.parse("HLA-A*02:01")
        assert result is not None


# ============================================================================
# parse_allele_or_gene_candidates edge cases
# ============================================================================


class TestParseAlleleOrGeneCandidates:
    """Tests for parse_allele_or_gene_candidates edge cases."""

    def test_whitespace_returns_empty(self):
        """Input with whitespace returns empty list."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_allele_or_gene_candidates(species, "A 02 01")
        eq_(result, [])


# ============================================================================
# parse_haplotype_with_class2_locus edge cases
# ============================================================================


class TestParseHaplotypeWithClass2Locus:
    """Tests for parse_haplotype_with_class2_locus_from_any_string_split."""

    def test_mouse_ia_haplotype(self):
        """Parse mouse I-A locus with haplotype like 'IAk'."""
        parser = Parser()
        species = Species.get("H2")
        result = parser.parse_haplotype_with_class2_locus_from_any_string_split(species, "IAk")
        assert isinstance(result, Haplotype)
        assert result.name == "k"
        assert result.locus_restriction == Class2Locus.get("H2", "A")
        # Should try to parse as locus + haplotype


# ============================================================================
# MhcClass from token
# ============================================================================


class TestMhcClassFromToken:
    """Tests for MhcClass parsing from tokens."""

    def test_parse_class_i_token_alone(self):
        """Parse 'class I' as token returns MhcClass."""
        result = parse("class I")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class1

    def test_parse_class_ii_token_alone(self):
        """Parse 'class II' as token returns MhcClass."""
        result = parse("class II")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class2


# ============================================================================
# Species and class combined parsing
# ============================================================================


class TestSpeciesClassParsing:
    """Tests for combined species and MHC class parsing."""

    def test_species_class_i(self):
        """Parse 'H2 class I' returns MhcClass for that species."""
        result = parse("H2 class I")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class1
        assert result.species.is_mouse

    def test_species_class_ii(self):
        """Parse 'HLA class II' returns MhcClass for that species."""
        result = parse("HLA class II")
        assert result is not None
        assert type(result) is MhcClass
        assert result.is_class2
        assert result.species.is_human


# ============================================================================
# Class2 pair with hyphen separator
# ============================================================================


class TestClass2PairHyphenSep:
    """Tests for Class II pair parsing with hyphen separator."""

    def test_class2_pair_hyphen(self):
        """Parse Class II pair with hyphen separator."""
        parser = Parser()
        species = Species.get("HLA")
        result = parser.parse_class2_pair_with_hyphen_sep(species, "DRA*01:01-DRB1*01:01")
        assert type(result) is Pair
        assert result.alpha.to_string() == "HLA-DRA*01:01"
        assert result.beta.to_string() == "HLA-DRB1*01:01"

    def test_class2_pair_hyphen_more_parts(self):
        """parse_class2_pair_with_hyphen_sep with >2 parts returns None."""
        parser = Parser()
        species = Species.get("HLA")
        assert parser.parse_class2_pair_with_hyphen_sep(species, "DRA-01-01-DRB1-01-01") is None
        # Should return None because it's not a simple 2-part split


# ============================================================================
# Additional edge cases for higher coverage
# ============================================================================


class TestGetHaplotype:
    """Tests for Parser.get_haplotype edge cases."""

    def test_get_haplotype_invalid_species(self):
        """get_haplotype with invalid species returns None."""
        parser = Parser()
        result = parser.get_haplotype("INVALID_SPECIES", "k")
        assert result is None

    def test_get_haplotype_invalid_name(self):
        """get_haplotype with invalid haplotype name returns None."""
        parser = Parser()
        result = parser.get_haplotype("H2", "invalid_haplotype_xyz")
        assert result is None

    def test_get_haplotype_valid(self):
        """get_haplotype with valid inputs returns Haplotype."""
        parser = Parser()
        result = parser.get_haplotype("H2", "b")
        assert result is not None
        assert type(result) is Haplotype


class TestParseGeneCandiates:
    """Tests for Parser.parse_gene_candidates edge cases."""

    def test_parse_gene_candidates_whitespace(self):
        """parse_gene_candidates with whitespace returns empty list."""
        parser = Parser()
        species = Species.get("HLA")
        result = list(parser.parse_gene_candidates(species, "A 02 01"))
        eq_(result, [])


class TestParseAndApplyMutations:
    """Tests for Parser.parse_and_apply_mutations edge cases."""

    def test_serotype_collapses_before_mutation(self):
        """Multi-allele serotype does not collapse for mutations; singleton serotype does."""
        parser = Parser()
        multi = parser.get_serotype("HLA", "A2")
        assert multi is not None
        assert parser.parse_and_apply_mutations(multi, [Token("G86Y", "G86Y")]) is None
        singleton = parser.get_serotype("HLA", "Aw69")
        assert singleton is not None
        mutated = parser.parse_and_apply_mutations(singleton, [Token("G86Y", "G86Y")])
        assert isinstance(mutated, Allele)
        assert mutated.mutations == (Mutation.get(86, "G", "Y"),)

    def test_haplotype_collapses_before_mutation(self):
        """Multi-allele haplotype cannot accept a single-allele mutation."""
        parser = Parser()
        haplotype = parser.get_haplotype("H2", "b")
        assert haplotype is not None
        assert parser.parse_and_apply_mutations(haplotype, [Token("G86Y", "G86Y")]) is None

    def test_parse_and_apply_mutations_none_result(self):
        """parse_and_apply_mutations with None result returns None."""
        parser = Parser()
        tokens = [Token("G86Y", "G86Y")]
        result = parser.parse_and_apply_mutations(None, tokens)
        assert result is None

    def test_parse_and_apply_mutations_wrong_type(self):
        """parse_and_apply_mutations with wrong type returns None."""
        parser = Parser()
        species = Species.get("HLA")
        tokens = [Token("G86Y", "G86Y")]
        result = parser.parse_and_apply_mutations(species, tokens)
        assert result is None

    def test_parse_and_apply_mutations_only_mutant_tokens(self):
        """parse_and_apply_mutations with only 'mutant' tokens returns None."""
        parser = Parser()
        allele = parse("HLA-A*02:01")
        # Create a token that is_mutant
        mutant_token = Token("mutant", "mutant")
        result = parser.parse_and_apply_mutations(allele, [mutant_token])
        assert result is None


class TestApplyMutationsToPair:
    """Tests for apply_mutations with Pair objects."""

    def test_apply_mutations_to_pair_with_gene_selector(self):
        """Apply mutations to pair with gene selector matching alpha."""
        from collections import defaultdict

        parser = Parser()
        pair = parse("HLA-DRA*01:01/DRB1*01:01")
        assert type(pair) is Pair

        alpha_gene = pair.alpha.gene
        mut = Mutation.get(86, "G", "Y")
        gene_to_mut = defaultdict(list)
        gene_to_mut[alpha_gene] = [mut]

        result = parser.apply_mutations(pair, [], defaultdict(list), gene_to_mut)
        assert result is not None
        assert type(result) is Pair
        assert result.alpha.is_mutant

    def test_apply_mutations_to_pair_with_beta_gene_selector(self):
        """Apply mutations to pair with gene selector matching beta."""
        from collections import defaultdict

        parser = Parser()
        pair = parse("HLA-DRA*01:01/DRB1*01:01")
        assert type(pair) is Pair

        beta_gene = pair.beta.gene
        mut = Mutation.get(86, "G", "Y")
        gene_to_mut = defaultdict(list)
        gene_to_mut[beta_gene] = [mut]

        result = parser.apply_mutations(pair, [], defaultdict(list), gene_to_mut)
        assert result is not None
        assert type(result) is Pair
        assert result.beta.is_mutant


class TestAlphaAndBetaTokenParsing:
    """Tests for alpha/beta token parsing with various result types."""

    def test_alpha_token_with_pair(self):
        """Parsing 'pair alpha' extracts the alpha chain from a Pair."""
        result = parse("HLA-DRA*01:01/DRB1*01:01 alpha", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_class2_alpha
        eq_(result, Allele.get("HLA", "DRA", "01", "01"))

    def test_beta_token_with_pair(self):
        """Parsing 'pair beta' extracts the beta chain from a Pair."""
        result = parse("HLA-DRA*01:01/DRB1*01:01 beta", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_class2_beta
        eq_(result, Allele.get("HLA", "DRB1", "01", "01"))

    def test_alpha_beta_token_with_gene_pair_and_reversed_pair(self):
        """Trailing alpha/beta also works on Gene pairs and reversed allele pairs."""
        eq_(parse("HLA-DRA/DRB1 alpha", raise_on_error=True), Gene.get("HLA", "DRA"))
        eq_(parse("HLA-DRA/DRB1 beta", raise_on_error=True), Gene.get("HLA", "DRB1"))
        eq_(
            parse("HLA-DRB1*01:01/DRA*01:01 alpha", raise_on_error=True),
            Allele.get("HLA", "DRA", "01", "01"),
        )

    def test_beta_token_with_beta_allele(self):
        """Parsing 'DRB1*01:01 beta' preserves the beta allele."""
        result = parse("DRB1*01:01 beta", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_class2_beta
        eq_(result, Allele.get("HLA", "DRB1", "01", "01"))

    def test_alpha_token_with_class2_locus(self):
        """Parsing 'Class2Locus alpha' extracts alpha gene."""
        result = parse("HLA-DR alpha", raise_on_error=True)
        assert type(result) is Gene
        eq_(result, Gene.get("HLA", "DRA"))

    def test_beta_token_with_class2_locus(self):
        """Parsing 'Class2Locus beta' extracts beta gene."""
        result = parse("HLA-DR beta", raise_on_error=True)
        assert type(result) is Gene
        eq_(result, Gene.get("HLA", "DRB1"))


class TestMutantTokenParsing:
    """Tests for mutant token parsing."""

    def test_mutant_token_with_invalid_base(self):
        """Parsing with mutant token but invalid base returns None."""
        result = parse("INVALID G86Y mutant", raise_on_error=False)
        assert result is None

    def test_mutant_token_with_valid_allele(self):
        """Parsing with mutant token and valid allele works."""
        result = parse("HLA-A*02:01 G86Y mutant", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_mutant
        eq_(result.to_string(), "HLA-A*02:01 G86Y mutant")


class TestSpeciesClassTokenParsing:
    """Tests for species + class token parsing."""

    def test_mouse_class_i_with_allele(self):
        """Parse 'mouse class I H2-Kb' format."""
        result = parse("mouse class I H2-Kb", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_class1
        eq_(result.to_string(), "H2-K*b")

    def test_mouse_class_ii_with_allele(self):
        """Parse 'mouse class II H2-IAb' format."""
        result = parse("mouse class II H2-IAb", raise_on_error=True)
        assert type(result) is Pair
        assert result.is_class2
        eq_(result.alpha.to_string(), "H2-AA*b")
        eq_(result.beta.to_string(), "H2-AB*b")

    def test_human_class_i_with_allele(self):
        """Parse 'human class I HLA-A*02:01' format."""
        result = parse("human class I HLA-A*02:01", raise_on_error=True)
        assert type(result) is Allele
        assert result.is_class1
        eq_(result.to_string(), "HLA-A*02:01")


class TestSelectSpeciesFromAttributes:
    """Tests for select_species_from_optional_attributes."""

    def test_os_attribute(self):
        """OS attribute selects species."""
        parser = Parser()
        result = parser.select_species_from_optional_attributes({"OS": "Homo sapiens"})
        assert result is not None
        assert result.is_human

    def test_species_attribute(self):
        """species attribute selects species."""
        parser = Parser()
        result = parser.select_species_from_optional_attributes({"species": "mouse"})
        assert result is not None
        assert result.is_mouse

    def test_no_species_attribute(self):
        """No species attribute returns None."""
        parser = Parser()
        result = parser.select_species_from_optional_attributes({"other": "value"})
        assert result is None


class TestParseMultipleCandidatesSpeciesPrefix:
    """Tests for parse_multiple_candidates with species prefix."""

    def test_species_prefix_only(self):
        """Parsing just species name returns species candidates."""
        parser = Parser()
        # Try parsing just "HLA" which should return species
        results = parser.parse_multiple_candidates("HLA")
        assert len(results) > 0

    def test_species_prefix_with_class(self):
        """Parsing 'HLA class I' returns MhcClass."""
        parser = Parser()
        results = parser.parse_multiple_candidates("HLA class I")
        assert len(results) > 0
        assert any(type(r) is MhcClass for r in results)


class TestParseWithClassTokenNoOtherTokens:
    """Tests for parse_with_class_token_to_multiple_candidates with no other tokens."""

    def test_class_token_only_with_species(self):
        """Parsing class token alone returns MhcClass."""
        parser = Parser()
        class_token = tokenize("class I").tokens[0]
        results = parser.parse_with_class_token_to_multiple_candidates(
            class_token, [], default_species="HLA"
        )
        assert len(results) > 0


class TestParseWithHaplotypeTokenNoOtherTokens:
    """Tests for parse_with_haplotype_token_to_multiple_candidates edge cases."""

    def test_haplotype_species_only(self):
        """Parsing 'haplotype H2' with no other tokens returns [Species('H2')]."""
        parser = Parser()
        species_token = Token("h2", "H2")
        results = parser.parse_with_haplotype_token_to_multiple_candidates(
            species_token, (), default_species=None
        )
        assert results == [Species.get("H2")]


class TestSlashParsingMoreEdgeCases:
    """More edge cases for slash-separated parsing."""

    def test_allele_slash_allele_different_species(self):
        """Parsing alleles from different species separated by slash fails."""
        assert parse("HLA-A*02:01/H2-Kb", raise_on_error=False) is None


class TestTransformAlleleAliases:
    """Tests for allele alias transformations."""

    def test_transform_with_allele_aliases_enabled(self):
        """Transform with allele aliases enabled."""
        parser = Parser(use_allele_aliases=True)
        result = parser.parse("HLA-B*15:01")
        assert isinstance(result, Allele)
        assert result.to_string() == "HLA-B*15:01"

    def test_transform_known_allele(self):
        """Transform checks known alleles."""
        parser = Parser()
        result = parser.parse("HLA-A*02:01")
        assert isinstance(result, Allele)
        assert result.to_string() == "HLA-A*02:01"


class TestTransformSerotypesAndHaplotypes:
    """Tests for transforming serotypes, haplotypes, and pairs."""

    def test_transform_pair_with_changed_components(self):
        """Transforming a Class II pair preserves both chains."""
        parser = Parser(use_allele_aliases=True)
        result = parser.parse("HLA-DRA*01:01/DRB1*01:01")
        assert isinstance(result, Pair)
        assert result.alpha.to_string() == "HLA-DRA*01:01"
        assert result.beta.to_string() == "HLA-DRB1*01:01"


class TestSlashParsingWithAlleleGene:
    """More tests for slash parsing with allele/gene combinations."""

    def test_allele_slash_allele_same_species(self):
        """Parsing alleles from same species forms pair."""
        result = parse("HLA-DRA*01:01/HLA-DRB1*01:01", raise_on_error=False)
        assert type(result) is Pair

    def test_gene_slash_gene(self):
        """Parsing gene/gene combination forms a Pair of Genes."""
        result = parse("HLA-DRA/DRB1", raise_on_error=False)
        assert type(result) is Pair
        assert result.alpha == Gene.get("HLA", "DRA")
        assert result.beta == Gene.get("HLA", "DRB1")


class TestAlphaBetaTokenWithTypes:
    """Tests for alpha/beta token parsing returning specific types."""

    def test_parse_dr_locus_alpha_chain(self):
        """Parse 'HLA-DR alpha chain' to get the DRA gene."""
        result = parse("HLA-DR alpha chain", raise_on_error=False)
        assert result == Gene.get("HLA", "DRA")

    def test_parse_dr_locus_beta_chain(self):
        """Parse 'HLA-DR beta chain' to get the DRB1 gene."""
        result = parse("HLA-DR beta chain", raise_on_error=False)
        assert result == Gene.get("HLA", "DRB1")


class TestMutantTokenEdgeCases:
    """More edge cases for mutant token parsing."""

    def test_mutant_fails_no_mutation(self):
        """Parsing with 'mutant' token when no valid mutation is present returns None."""
        assert parse("HLA-A*02:01 NOTAMUTATION mutant", raise_on_error=False) is None

    def test_parse_unrecognized_complex_mutation_returns_none(self):
        """Unrecognized 'alpha E152A mutant' syntax returns None."""
        assert parse("HLA-A*02:01 alpha E152A mutant", raise_on_error=False) is None


class TestSpeciesMiddleClassToken:
    """Tests for species + class token in middle position."""

    def test_species_class_allele_format(self):
        """Parse 'species class allele' three-token format."""
        result = parse("H2 class I Kb", raise_on_error=False)
        assert isinstance(result, Allele)
        assert result.is_class1

    def test_species_class_ii_allele_format(self):
        """Parse 'species class II allele' format."""
        result = parse("H2 class II IAb", raise_on_error=False)
        assert isinstance(result, Pair)
        assert result.is_class2


class TestParseMultipleCandidatesSpeciesThenTokens:
    """Tests for parsing when species prefix is found."""

    def test_species_then_class_token(self):
        """Parse species name followed by class token."""
        parser = Parser()
        results = parser.parse_multiple_candidates("HLA class I")
        assert len(results) > 0

    def test_species_then_class_ii_token(self):
        """Parse species name followed by class II token."""
        parser = Parser()
        results = parser.parse_multiple_candidates("HLA class II")
        assert len(results) > 0


class TestAdversarialSpeciesStickiness:
    """Regression tests for species-scoped parsing."""

    def test_explicit_species_does_not_switch_to_other_species(self):
        # "Maar-A2" used to belong here, but since #123 put Macaca arctoides
        # under Macaca sp. it inherits the genus A1/A2/A3 loci and resolves to
        # its own species -- which is what stickiness asks for, so it no longer
        # exercises the rule. "Maar-BLB2" (a chicken class II gene) does.
        for s in ["Onmy-DAA2", "Sasa-DAA2", "Maar-BLB2", "Maar-UAA"]:
            assert parse(s, raise_on_error=False) is None

    def test_nested_species_prefix_does_not_override_explicit_species(self):
        for s in ["Onmy-Nini-DAA1", "HLA-Maar-A*01:01"]:
            assert parse(s, raise_on_error=False) is None

    def test_malformed_compact_suffix_does_not_become_partial_allele(self):
        for s in ["BoLA-NC11x", "Saoe-N1x", "Maar-A1x", "Onmy-DAA1x"]:
            assert parse(s, raise_on_error=False) is None

    def test_explicit_species_does_not_fall_back_to_foreign_haplotype(self):
        for s in ["Sasa-RT11", "Saoe-RT11"]:
            assert parse(s, raise_on_error=False) is None

    def test_exact_gene_prefix_blocks_shorter_compact_gene_parse(self):
        for s in ["BoLA-NC11Q", "BoLA-NC11N"]:
            assert parse(s, raise_on_error=False) is None

    def test_valid_species_scoped_compact_names_still_parse(self):
        eq_(parse("Onmy-DAA1", raise_on_error=True), Gene.get("Onmy", "DAA1"))
        eq_(parse("Saoe-N3", raise_on_error=True), Gene.get("Saoe", "N3"))
        eq_(parse("BoLA-NC11", raise_on_error=True), Gene.get("BoLA", "NC11"))


class TestHaplotypeSlashRestriction:
    """Tests for haplotype slash parsing with class restriction."""

    def test_haplotype_slash_with_class_ii(self):
        """Parse 'H2-b/d class II' for class II restriction."""
        result = parse("H2-b/d class II", raise_on_error=False)
        assert isinstance(result, Haplotype)
        assert result.name == "b/d"
        assert result.class_restriction == "II"


class TestGetHaplotypesForAnySpecies:
    """Tests for get_haplotypes_for_any_species."""

    def test_get_haplotypes_for_any_species(self):
        """Finding haplotype 'b' across species returns the mouse H2-b haplotype."""
        parser = Parser()
        results = parser.get_haplotypes_for_any_species("b")
        assert any(h.species == Species.get("H2") and h.name == "b" for h in results)


class TestParseAlleleFromAlleleFieldsAnnotations:
    """Tests for parse_allele_from_allele_fields with annotations."""

    def test_allele_fields_with_functional_annotations_provided(self):
        """Test allele fields with annotations already provided."""
        parser = Parser()
        gene = Gene.get("HLA", "A")
        result = parser.parse_allele_from_allele_fields(
            gene, ["02", "01"], functional_annotations=["N"]
        )
        assert type(result) is Allele
        eq_(result.annotations, ("N",))

    def test_parse_annotated_allele_via_normal_path(self):
        """Test annotated allele via normal parse path."""
        result = parse("HLA-A*02:01N")
        assert result is not None
        assert type(result) is Allele
        eq_(result.annotations, ("N",))
