from mhcgnomes import Allele, parse
from nose.tools import eq_


"""
Collection of tests for UniProt descriptions of MHC alleles
"""


def test_parse_uniprot_MOUSE_MHC_class_I_L_q_alpha_chain():
    s = "MOUSE MHC class I L-q alpha-chain"
    result = parse(s)
    eq_(result, Allele.get("H2", "L", "q"))

def TODO_parse_uniprot():
    s = "H-2 class I histocompatibility antigen, K-B alpha chain"
    result = parse(s)
    eq_(result, Allele.get("H2", "K", "b"))
