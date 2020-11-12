from nose.tools import eq_
from mhcgnomes import (
    parse,
    Allele,
    Class2Locus,
    Class2Pair,
    Gene,
    Haplotype,
)


def test_mouse_class1_alleles_H2_Kk():
    H2Kk = Allele.get("H2", "K", "k")

    eq_(parse("H2-Kk"), H2Kk)

    # with a hyphen in "H-2"
    eq_(parse("H-2-Kk"), H2Kk)

def test_mouse_class1_alleles_H2_Db():
    H2Db = Allele.get("H2", "D", "b")

    eq_(parse("H2-Db"), H2Db)

    # with hyphen in "H-2"
    eq_(parse("H-2-Db"), H2Db)

def test_H2_Kd_without_seps():
    eq_(parse("H2Kd"), Allele.get("H2", "K", "d"))

def test_H2_Lq_with_dash_in_species():
    eq_(parse("H-2-Lq"), Allele.get("H2", "L", "q"))

def test_H2_Lq_without_dash_in_species():
    eq_(parse("H2-Lq"), Allele.get("H2", "L", "q"))

def test_mouse_class2_gene():
    # H2-IAb
    gene = Gene.get("H2", "EB2")
    eq_(parse("H2-IEb2"), gene)

    # with hyphen in "H-2"
    eq_(parse("H-2-IEb2"), gene)

def test_parse_H2r():
    haplotype = parse("H2-r")
    assert isinstance(haplotype, Haplotype)
    eq_(haplotype.to_string(), "H2-r")


def test_parse_H2_IE():
    result = parse("H2-IE")
    eq_(type(result), Class2Locus)
    eq_(result.name, "E")


def test_parse_H2_IEd_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=True)
    eq_(type(result), Class2Pair)
    eq_(result.alpha.name, "d")
    eq_(result.beta.name, "d")

def test_parse_H2_IEd_no_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=False)
    eq_(type(result), Haplotype)
    eq_(result.name, "d")
    assert result.locus_restriction is not None
