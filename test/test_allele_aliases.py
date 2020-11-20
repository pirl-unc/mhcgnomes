from mhcgnomes import parse
from nose.tools import eq_

def test_parse_C0301_use_allele_aliases():
    allele = parse("C0301", use_allele_aliases=True)
    eq_(allele.to_string(), "HLA-C*03:04:01:01")


def test_parse_C0301_no_allele_aliases():
    allele = parse("C0301", use_allele_aliases=False)
    eq_(allele.to_string(), "HLA-C*03:01")
