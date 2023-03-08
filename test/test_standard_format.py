from mhcgnomes.standard_format import parse_standard_allele_format
from mhcgnomes import Allele

def test_parse_standard_allele_format_HLA_A_02_01():
    result = parse_standard_allele_format(seq="HLA-A*02:01")
    assert result == Allele.get("HLA", "A", "02", "01")

def test_parse_standard_allele_format_HLA_A_02_01_01():
    result = parse_standard_allele_format(seq="HLA-A*02:01:01")
    assert result == Allele.get("HLA", "A", "02", "01", "01")

def test_parse_standard_allele_format_HLA_A_02_01_01_01():
    result = parse_standard_allele_format(seq="HLA-A*02:01:01:01")
    assert result == Allele.get("HLA", "A", "02", "01", "01", "01")


def test_parse_standard_allele_format_HLA_A_02_01_01_02L():
    result = parse_standard_allele_format(seq="HLA-A*02:01:01:02L")
    assert result == Allele.get("HLA", "A", "02", "01", "01", "02", annotation="L")

def test_parse_standard_allele_format_DLA_88_021_01():
    result = parse_standard_allele_format(seq="DLA-88*01:01")
    assert result == Allele.get("DLA", "88", "01", "01")

def test_parse_standard_allele_format_A_02_01():
    result = parse_standard_allele_format(seq="A*02:01", default_species="HLA")
    assert result == Allele.get("HLA", "A", "02", "01")