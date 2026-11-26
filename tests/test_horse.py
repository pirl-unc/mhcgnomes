import pytest

from mhcgnomes import Allele, Gene, Haplotype, parse

from .common import eq_


def test_parse_haplotype_ELA_A1():
    result = parse("ELA-A1")
    assert result is not None
    assert type(result) is Haplotype
    eq_(result.name, "A1")
    assert result.species.is_horse
    eq_(
        {a.to_string() for a in result.alleles},
        {"ELA-2*002:02", "ELA-N*003:02", "ELA-N*006:01"},
    )
    eq_(result.mhc_class, "Ia")


def test_parse_haplotype_ELA_A1_lowercase():
    result = parse("ela-a1")
    assert result is not None
    assert type(result) is Haplotype
    eq_(result.name, "A1")
    assert result.species.is_horse


def test_parse_haplotype_ELA_A3_class1_and_class2():
    result = parse("ELA-A3", raise_on_error=True)
    assert type(result) is Haplotype
    eq_(result.name, "A3")
    allele_strings = {a.to_string() for a in result.alleles}
    for expected in (
        "ELA-1*001:01",
        "ELA-2*001:01",
        "ELA-5*001:01",
        "ELA-6*001:01",
        "ELA-7*002:01",
        "ELA-DRA*001:01",
        "ELA-DRB1*001:01",
        "ELA-DQA1*001:01",
        "ELA-DQB1*001:01",
    ):
        assert expected in allele_strings


@pytest.mark.parametrize("gene_name", ["5", "6", "7"])
def test_equine_nonclassical_class_ib_loci(gene_name):
    gene = parse(f"Eqca-{gene_name}", raise_on_error=True)
    assert type(gene) is Gene
    eq_(gene.mhc_class, "Ib")
    allele = parse(f"Eqca-{gene_name}*001:01", raise_on_error=True)
    assert type(allele) is Allele
    eq_(allele.mhc_class, "Ib")
