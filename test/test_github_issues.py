import mhcgnomes

def test_A_02_172():
    assert mhcgnomes.parse("HLA-A*02:172", use_allele_aliases=True).allele_fields[:2] == ("02", "172")
