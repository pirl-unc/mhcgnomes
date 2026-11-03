from mhcgnomes import Allele, Gene
from mhcgnomes.mhc_class_helpers import (
    is_valid_restriction,
    mhc_classes_within,
    restrict_alleles,
    restrict_genes,
)

from .common import eq_


def test_is_valid_restriction_class2_subtypes():
    assert is_valid_restriction("II", "IIa")
    assert is_valid_restriction("II", "IIb")
    assert not is_valid_restriction("II", "Ia")
    assert not is_valid_restriction("IIa", "II")


def test_restrict_alleles_class2_includes_ii_iia_iib():
    alleles = [
        Allele.get("HLA", "DRA", "01", "01"),
        Allele.get("HLA", "DOA", "01", "01"),
        Allele.get("HLA", "DRB6", "01", "01"),
    ]
    restricted = restrict_alleles(alleles, "II")
    eq_(set(restricted), set(alleles))


def test_mhc_classes_within_class1_includes_subtypes():
    eq_(mhc_classes_within("I"), frozenset({"I", "Ia", "Ib", "Ic", "Id"}))


def test_mhc_classes_within_class2_includes_subtypes():
    eq_(mhc_classes_within("II"), frozenset({"II", "IIa", "IIb"}))


def test_mhc_classes_within_subtype_is_only_itself():
    eq_(mhc_classes_within("Ia"), frozenset({"Ia"}))
    eq_(mhc_classes_within("IIb"), frozenset({"IIb"}))


def test_restrict_genes_and_restrict_alleles_share_one_table():
    # HLA-A is class Ia, HLA-E class Ib, HLA-DRB1 class IIa.
    genes = [Gene.get("HLA", "A"), Gene.get("HLA", "E"), Gene.get("HLA", "DRB1")]
    alleles = [Allele.get("HLA", gene.name, "01", "01") for gene in genes]
    expected = {
        "I": ["A", "E"],
        "Ia": ["A"],
        "Ib": ["E"],
        "II": ["DRB1"],
        "IIa": ["DRB1"],
        "IIb": [],
    }
    for mhc_class, gene_names in expected.items():
        eq_([gene.name for gene in restrict_genes(genes, mhc_class)], gene_names)
        eq_([allele.gene_name for allele in restrict_alleles(alleles, mhc_class)], gene_names)
