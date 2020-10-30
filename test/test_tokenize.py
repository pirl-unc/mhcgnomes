from mhcgnomes.tokenize import tokenize, split, CLASS1_TOKEN, ALPHA_CHAIN_TOKEN
from nose.tools import eq_

def test_tokenize_complex_uniprot_string_for_H2_Lq():
    s = "MHC class I L-q alpha-chain gene (H2 haplotype), exons 1-3 (Fragment) OS=Mus musculus OX=10090 PE=3 SV=1"
    tokens, raw_string_parts, attributes = tokenize(s)
    eq_(tokens, (
        CLASS1_TOKEN,
        "l-q",
        ALPHA_CHAIN_TOKEN,
        "gene",
        "h2",
        "haplotype",
    ))
    eq_(raw_string_parts[1], "L-q")
    assert "OS" in attributes
    eq_(attributes["OS"], "Mus musculus")
    assert "OX" in attributes
    eq_(attributes["OX"], "10090")
    assert "PE" in attributes
    eq_(attributes["PE"], "3")
    assert "SV" in attributes
    eq_(attributes["SV"], "1")

def test_tokenize_attributes_only():
    s = "OS=Mus musculus OX=10090 PE=3 SV=1"
    tokens, raw_string_parts, attributes = tokenize(s)
    eq_(tokens, ())
    eq_(raw_string_parts, ())
    assert "OS" in attributes
    eq_(attributes["OS"], "Mus musculus")
    assert "OX" in attributes
    eq_(attributes["OX"], "10090")
    assert "PE" in attributes
    eq_(attributes["PE"], "3")
    assert "SV" in attributes
    eq_(attributes["SV"], "1")


def test_split():
    s = "Class II DRA0101/DRB0101"
    eq_(split(s), ["Class", "II", "DRA0101", "/", "DRB0101"])
