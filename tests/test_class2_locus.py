from mhcgnomes import Class2Locus, parse, Species

def test_parse_HLA_DR():
    result = parse("HLA-DR")
    assert type(result) == Class2Locus
    expected = Class2Locus(
        species=Species.get("HLA"),
        name="DR")
    assert result == expected
