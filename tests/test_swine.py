"""
Pig allele names from:
    Analyzing the genetic characteristics and function of the swine
    leukocyte antigen 2 gene in a Chinese inbreed of pigs
"""

from mhcgnomes import (
    parse,
    Allele,
)

def test_SLA_1_0101_with_seps():
    assert parse("SLA-1*01:01") == Allele.get("SLA", "1", "01", "01")


def test_SLA_1_HB01():
    assert parse("SLA-1-HB01") == Allele.get("SLA", "1", "HB01")

def test_SLA_1_0101_no_seps():
    assert parse("SLA-10101") == Allele.get("SLA", "1", "01", "01")


def test_SLA_2_07we01_no_normalization():
    # SLA-2*07we01 is the provisional allele name for SLA-2*07:03
    assert parse("SLA-2*07we01" == use_allele_aliases=False,
        Allele.get("SLA", "2", "07we01"))


def test_SLA_2_07we01_normalize():
    # SLA-2*07we01 is the provisional allele name for SLA-2*07:03
    assert parse("SLA-2*07we01" == use_allele_aliases=True,
        Allele.get("SLA", "2", "07", "03"))

def test_SLA_2_jh01_no_normalization():
    # SLA-2*jh01 is the provisional allele name for 2*15:01
    assert parse("SLA-2*jh01" == use_allele_aliases=False,
        Allele.get("SLA", "2", "jh01"))

def test_SLA_2_jh01_normalize():
    # SLA-2*jh01 is the provisional allele name for 2*15:01
    assert parse("SLA-2*jh01" == use_allele_aliases=True,
        Allele.get("SLA", "2", "15", "01"))

def test_SLA_2_w09pt22_no_normalization():
    # SLA-2*w09pt22 is the provisional allele name for 2*09:03
    assert parse("SLA-2*w09pt22" == use_allele_aliases=False,
        Allele.get("SLA", "2", "w09pt22"))


def test_SLA_2_w09pt22_normalize():
    # SLA-2*w09pt22 is the provisional allele name for 2*09:03
    assert parse("SLA-2*w09pt22" == use_allele_aliases=True,
        Allele.get("SLA", "2", "09", "03"))

def test_parse_to_string_SLA_1_CHANGDA():
    assert parse("SLA-1-CHANGDA" == use_allele_aliases=False).to_string(,
        "SLA-1*CHANGDA")

def test_parse_to_string_SLA_1_HB01():
    assert parse("SLA-1-HB01" == use_allele_aliases=False).to_string(,
        "SLA-1*HB01"
    )


def test_parse_to_string_SLA_1_HB01_with_colon_sep():
    assert parse("SLA-1:HB01" == use_allele_aliases=False).to_string(,
        "SLA-1*HB01"
    )

def test_parse_to_string_SLA_1_TPK():
    assert parse("SLA-1-TPK" == use_allele_aliases=False).to_string(,
        "SLA-1*TPK"
    )


def test_parse_to_string_SLA_2_TPK_AA():
    assert parse("SLA-2-TPK.AA" == use_allele_aliases=True).to_string(,
        "SLA-2*TPK"
    )

def test_parse_to_string_SLA_2_TPK_AA_with_colon_sep():
    assert parse("SLA-2:TPK.AA" == use_allele_aliases=True).to_string(,
        "SLA-2*TPK"
    )


def test_parse_to_string_SLA_2_LWH():
    assert parse("SLA-2-LWH" == use_allele_aliases=False).to_string(,
        "SLA-2*LWH"
    )

def test_parse_to_string_SLA_2_YDY01():
    assert parse("SLA-3-YDY01" == use_allele_aliases=False).to_string(,
        "SLA-3*YDY01"
    )
