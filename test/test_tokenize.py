from mhcgnomes.tokenize import tokenize, CLASS1_TOKEN, ALPHA_CHAIN_TOKEN
from nose.tools import eq_

def test_tokenize_complex_uniprot_string_for_H2_Lq():
    s = "MHC class I L-q alpha-chain gene (H2 haplotype), exons 1-3 (Fragment) OS=Mus musculus OX=10090 PE=3 SV=1"
    tokens, raw_string_parts, attributes = tokenize(s)
    eq_(tokens, (
        CLASS1_TOKEN,
        "l-q",
        ALPHA_CHAIN_TOKEN,
        "h2",
        "haplotype",
        "exons",
        "1-3"
    ))
    assert "OS" in attributes
    eq_(raw_string_parts[1], "L-q")