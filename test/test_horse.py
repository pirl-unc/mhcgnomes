from mhcgnomes import parse, Haplotype
from nose.tools import eq_

def test_parse_haplotype_ELA_A1():
    result = parse("ELA-A1")
    assert result is not None
    assert type(result) is Haplotype
    eq_(result.name, "A1")
    assert result.species.is_horse

def test_parse_haplotype_ELA_A1_lowercase():
    result = parse("ela-a1")
    assert result is not None
    assert type(result) is Haplotype
    eq_(result.name, "A1")
    assert result.species.is_horse
