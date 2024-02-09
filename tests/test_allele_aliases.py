from mhcgnomes import parse

def test_parse_C0301_use_allele_aliases():
    allele = parse("C0301", use_allele_aliases=True)
    assert allele.to_string() == "HLA-C*03:04:01:01"


def test_parse_C0301_no_allele_aliases():
    allele = parse("C0301", use_allele_aliases=False)
    assert allele.to_string() == "HLA-C*03:01"
