from mhcgnomes import parse, Haplotype, Allele

def test_parse_haplotype_ELA_A1():
    result = parse("ELA-A1")
    assert result is not None
    assert type(result) is Haplotype
    assert result.name == "A1"
    assert result.species.is_horse

def test_parse_haplotype_ELA_A1_lowercase():
    result = parse("ela-a1")
    assert result is not None
    assert type(result) is Haplotype
    assert result.name == "A1"
    assert result.species.is_horse

