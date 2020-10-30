from mhcgnomes import Allele, parse
from nose.tools import eq_


"""
Collection of tests for UniProt descriptions of MHC alleles
"""


def test_parse_uniprot_MOUSE_MHC_class_I_L_q_alpha_chain():
    s = "MOUSE MHC class I L-q alpha-chain"
    result = parse(s)
    eq_(result, Allele.get("H2", "L", "q"))

def test_parse_uniprot_H2_class_I_histocompatibility_antigen_K_B_alpha_chain():
    s = "H-2 class I histocompatibility antigen, K-B alpha chain"
    result = parse(s)
    eq_(result, Allele.get("H2", "K", "b"))

def test_parse_uniprot_H2_class_I_histocompatibility_antigen_K_Q_alpha_chain_fragment():
    s = "H-2 class I histocompatibility antigen, K-Q alpha chain (Fragment)"
    result = parse(s)
    eq_(result, Allele.get("H2", "K", "q"))

def test_parse_uniprot_MHC_class_I_histocompatibility_antigen_L_Q_alpha_chain_fragment_with_attributes():
    s = "MHC class I L-q alpha-chain gene (H2 haplotype), exons 1-3 (Fragment) OS=Mus musculus OX=10090 PE=3 SV=1"
    result = parse(s)
    eq_(result, Allele.get("H2", "L", "q"))