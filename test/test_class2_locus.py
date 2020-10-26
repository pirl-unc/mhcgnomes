from mhcgnomes import Class2Locus, parse, Species
from nose.tools import eq_

def test_parse_HLA_DR():
    result = parse("HLA-DR")
    eq_(type(result), Class2Locus)
    expected = Class2Locus(
        species=Species.get("HLA"),
        name="DR")
    eq_(result, expected)
