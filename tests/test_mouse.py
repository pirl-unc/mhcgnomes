from mhcgnomes import (
    Allele,
    Class2Locus,
    Gene,
    Haplotype,
    Pair,
    parse,
)

from .common import eq_


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


def test_mouse_MR1_weird_uniprot_entry():
    seq = "Major histocompatibility complex class I-related gene protein OS=Mus musculus OX=10090 GN=Mr1 PE=1 SV=2"
    result = parse(seq)
    expected = Gene.get("H2", "MR1")
    eq_(result, expected)


def test_parse_H2_IEd_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=True)
    eq_(type(result), Pair)
    eq_(result.alpha.name, "d")
    eq_(result.beta.name, "d")


def test_parse_H2_IEd_no_simplify():
    result = parse("H2-IEd", collapse_singleton_haplotypes=False)
    eq_(type(result), Haplotype)
    eq_(result.name, "d")
    assert result.locus_restriction is not None


# ---- Mouse class II gene name variants ----


def test_parse_mouse_MHC_II_IE_beta():
    """'mouse MHC II IE-beta' should parse as H2-EB gene."""
    result = parse("mouse MHC II IE-beta")
    assert result is not None, "Failed to parse 'mouse MHC II IE-beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")
    eq_(result.species_prefix, "H2")


def test_parse_MHC_II_I_E_beta():
    """'MHC II I-E beta' should parse as H2-EB gene."""
    result = parse("MHC II I-E beta")
    assert result is not None, "Failed to parse 'MHC II I-E beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_murine_MHC_class_II_I_E_beta():
    """'murine MHC class II I-E beta' should parse as H2-EB gene."""
    result = parse("murine MHC class II I-E beta")
    assert result is not None, "Failed to parse 'murine MHC class II I-E beta'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")
    eq_(result.species_prefix, "H2")


def test_parse_H2_IE_beta_chain():
    """'H2-IE beta chain' should parse as H2-EB gene."""
    result = parse("H2-IE beta chain")
    assert result is not None, "Failed to parse 'H2-IE beta chain'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_I_E_beta_chain():
    """'I-E beta chain' should parse as H2-EB gene."""
    result = parse("I-E beta chain")
    assert result is not None, "Failed to parse 'I-E beta chain'"
    assert isinstance(result, Gene)
    eq_(result.gene_name, "EB")


def test_parse_murine_species():
    """'murine' should be recognized as Mus musculus."""
    from mhcgnomes import Species

    species = Species.get("murine")
    assert species is not None
    eq_(species.prefix, "H2")
