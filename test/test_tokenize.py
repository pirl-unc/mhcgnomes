from mhcgnomes.tokenize import (
    tokenize,
    split_token_sequences,
)
from mhcgnomes.token import Token
from mhcgnomes.token_canonical_sequences import (
    CLASS1_TOKEN_SEQ,
    CLASS2_TOKEN_SEQ,
    ALPHA_CHAIN_TOKEN_SEQ,
    MUTANT_TOKEN_SEQ,
    BETA_CHAIN_TOKEN_SEQ,
)

from nose.tools import eq_

def test_Token():
    t = Token("l-q", raw_string="L-Q")
    eq_(t, t)
    eq_(t, "l-q")

def test_tokenize_complex_uniprot_string_for_H2_Lq():
    s = "MHC class I L-q alpha-chain gene (H2 haplotype), exons 1-3 (Fragment) OS=Mus musculus OX=10090 PE=3 SV=1"
    tokenization_result = tokenize(s)
    eq_(tokenization_result.raw_string, s)
    eq_(tokenization_result.tokens, (
        CLASS1_TOKEN_SEQ,
        "l-q",
        ALPHA_CHAIN_TOKEN_SEQ,
        "gene",
        "h2",
        "haplotype",
    ))
    eq_(tokenization_result.tokens, (
        Token(CLASS1_TOKEN_SEQ),
        Token("l-q"),
        Token(ALPHA_CHAIN_TOKEN_SEQ),
        Token("gene"),
        Token("h2"),
        Token("haplotype"),
    ))
    eq_(tokenization_result.tokens[1].raw_string, "L-q")
    assert "OS" in tokenization_result.attributes
    eq_(tokenization_result.attributes["OS"], "Mus musculus")
    assert "OX" in tokenization_result.attributes
    eq_(tokenization_result.attributes["OX"], "10090")
    assert "PE" in tokenization_result.attributes
    eq_(tokenization_result.attributes["PE"], "3")
    assert "SV" in tokenization_result.attributes
    eq_(tokenization_result.attributes["SV"], "1")

def test_tokenize_attributes_only():
    s = "OS=Mus musculus OX=10090 PE=3 SV=1"
    tokenization_result = tokenize(s)
    eq_(tokenization_result.raw_string, s)
    eq_(tokenization_result.tokens, ())
    assert "OS" in tokenization_result.attributes
    eq_(tokenization_result.attributes["OS"], "Mus musculus")
    assert "OX" in tokenization_result.attributes
    eq_(tokenization_result.attributes["OX"], "10090")
    assert "PE" in tokenization_result.attributes
    eq_(tokenization_result.attributes["PE"], "3")
    assert "SV" in tokenization_result.attributes
    eq_(tokenization_result.attributes["SV"], "1")


def test_split_token_sequences():
    s = "Class II DRA0101/DRB0101"
    eq_(split_token_sequences(s), ["Class", "II", "DRA0101", "/", "DRB0101"])

def test_tokenize_BoLA_DRA_DRB31501():
    s = "BoLA-DRA-DRB31501"
    eq_(tokenize(s).tokens, (
        s.lower(),
    ))