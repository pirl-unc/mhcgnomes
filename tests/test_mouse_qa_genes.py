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


class TestNetmhcQaSpellings:
    """NetMHCpan 4.1 and 4.2 list ``H-2-Qa1``/``H-2-Qa2`` (and ``H2-`` forms) as molecules (#190).

    The predictor does not name the allele, and Qa-1 is polymorphic, so mhcgnomes
    keeps these as class-Ib Gene results with the T23/Q7 identity rather than
    inventing an allele. Callers needing one molecule must apply their own policy.
    """

    @pytest.mark.parametrize(
        "name,gene",
        [
            ("H-2-Qa1", "T23"),
            ("H2-Qa1", "T23"),
            ("H-2-Qa2", "Q7"),
            ("H2-Qa2", "Q7"),
        ],
    )
    @pytest.mark.parametrize("use_allele_aliases", [False, True])
    def test_gene_level_identity_and_class(self, name, gene, use_allele_aliases):
        result = parse(name, use_allele_aliases=use_allele_aliases)
        assert type(result) is Gene
        assert result.name == gene
        assert result.mhc_class == "Ib"
        assert result.species.name == "Mus musculus"
        assert result.to_string() == "H2-" + gene
