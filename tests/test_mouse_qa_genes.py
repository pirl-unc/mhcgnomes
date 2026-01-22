"""
Tests for mouse H2-Qa non-classical MHC genes.

The Qa genes (Qa-1, Qa-2, etc.) are non-classical MHC class Ib genes in mice.
They have official names (T23, Q7, etc.) but are commonly referred to by
their Qa names in the literature.

Gene aliases:
- Qa / Qa1 / Qa-1 -> T23
- Qa2 / Qa-2 -> Q7
- Qa10 / Qa-10 -> Q10
"""

import pytest

from mhcgnomes import Allele, Gene, parse


class TestMouseQaGenes:
    """Test parsing of mouse Qa gene nomenclature."""

    @pytest.mark.parametrize(
        "name,expected_gene",
        [
            ("H2-Qa", "T23"),
            ("H2-Qa1", "T23"),
            ("H2-Qa-1", "T23"),
            ("H2-Qa2", "Q7"),
            ("H2-Qa-2", "Q7"),
            ("H2-Qa10", "Q10"),
            ("H2-Qa-10", "Q10"),
        ],
    )
    def test_qa_genes(self, name, expected_gene):
        """Qa gene names should resolve to their official T/Q names."""
        result = parse(name)
        assert isinstance(result, Gene)
        assert result.name == expected_gene

    @pytest.mark.parametrize(
        "name,expected_gene,expected_allele",
        [
            # Valid notations for gene T23 (Qa-1), allele b
            ("H2-Qa-1b", "T23", ("b",)),
            ("H2-Qa1*b", "T23", ("b",)),
            ("H2-Qa*b", "T23", ("b",)),
            # Parenthesis notation also works
            ("H2-Qa-1(b)", "T23", ("b",)),
            ("H2-Qa1(b)", "T23", ("b",)),
        ],
    )
    def test_qa_alleles(self, name, expected_gene, expected_allele):
        """Qa allele names should parse to gene T23, allele b."""
        result = parse(name)
        assert isinstance(result, Allele)
        assert result.gene.name == expected_gene
        assert result.allele_fields == expected_allele

    def test_qa_star_1b_is_wrong_notation(self):
        """
        Qa*1b is wrong notation - the 1 is part of the gene name, not allele.

        This parses but gives the "wrong" result (allele "1b" instead of "b"),
        which is correct behavior - we shouldn't silently fix bad notation.
        The correct notation is Qa1*b or Qa-1b.
        """
        result = parse("H2-Qa*1b")
        assert isinstance(result, Allele)
        assert result.gene.name == "T23"
        # Note: allele is "1b" not "b" - this is expected for wrong notation
        assert result.allele_fields == ("1b",)
