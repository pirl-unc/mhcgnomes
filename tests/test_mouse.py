from mhcgnomes import (
    parse,
    Allele,
    Class2Locus,
    Pair,
    Gene,
    Haplotype,
)


def test_mouse_class1_alleles_H2_Kk():
    H2Kk = Allele.get("H2", "K", "k")
    assert parse("H2-Kk") == H2Kk

    # with a hyphen in "H-2"
    assert parse("H-2-Kk") == H2Kk

def test_mouse_class1_alleles_H2_Db():
    H2Db = Allele.get("H2", "D", "b")

    assert parse("H2-Db") == H2Db

    # with hyphen in "H-2"
    assert parse("H-2-Db") == H2Db

def test_H2_Kd_without_seps():
    assert parse("H2Kd") == Allele.get("H2", "K", "d")

def test_H2_Lq_with_dash_in_species():
    assert parse("H-2-Lq") == Allele.get("H2", "L", "q")

def test_H2_Lq_without_dash_in_species():
    assert parse("H2-Lq") == Allele.get("H2", "L", "q")

def test_mouse_class2_gene():
    # H2-IAb
    gene = Gene.get("H2", "EB2")
    assert parse("H2-IEb2") == gene

    # with hyphen in "H-2"
    assert parse("H-2-IEb2") == gene

def test_parse_H2r():
    haplotype = parse("H2-r")
    assert isinstance(haplotype, Haplotype)
    assert haplotype.to_string() == "H2-r"


def test_parse_H2_IE():
    result = parse("H2-IE")
    assert type(result) == Class2Locus
    assert result.name == "E"


def test_mouse_MR1_weird_uniprot_entry():
    seq = "Major histocompatibility complex class I-related gene protein OS=Mus musculus OX=10090 GN=Mr1 PE=1 SV=2"
    result = parse(seq)
    expected = Gene.get("H2", "MR1")
    assert result == expected


def test_parse_H2_IEd_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=True)
    assert type(result) == Pair
    assert result.alpha.name == "d"
    assert result.beta.name == "d"

def test_parse_H2_IEd_no_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=False)
    assert type(result) == Haplotype
    assert result.name == "d"
    assert result.locus_restriction is not None
