from mhcgnomes import parse, Allele
from nose.tools import eq_

def test_Popy_DRB_W116_01():
    seq = "Popy-DRB*W116:01"
    allele = parse(seq)
    eq_(allele, Allele.get("Popy", "DRB", "W116", "01"))
