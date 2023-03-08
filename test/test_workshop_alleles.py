from mhcgnomes import parse, Allele

def test_Popy_DRB_W116_01():
    seq = "Popy-DRB*W116:01"
    allele = parse(seq)
    assert allele == Allele.get("Popy", "DRB", "W116", "01")
