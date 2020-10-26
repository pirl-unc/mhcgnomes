"""
Pig allele names from:
    Analyzing the genetic characteristics and function of the swine
    leukocyte antigen 2 gene in a Chinese inbreed of pigs
"""

from mhcgnomes import (
    parse,
    Allele,
)
from nose.tools import eq_


def test_SLA_1_0101_with_seps():
    eq_(parse("SLA-1*01:01"),
        Allele.get("SLA", "1", "01", "01"))


def test_SLA_1_HB01():
    eq_(parse("SLA-1-HB01"),
        Allele.get("SLA", "1", "HB", "01"))

def test_SLA_1_0101_no_seps():
    eq_(parse("SLA-10101"),
        Allele.get("SLA", "1", "01", "01"))


def test_SLA_2_07we01_no_normalization():
    # SLA-2*07we01 is the provisional allele name for SLA-2*07:03
    eq_(parse("SLA-2*07we01", map_allele_aliases=False),
        Allele.get("SLA", "2", "07we01"))


def test_SLA_2_07we01_normalize():
    # SLA-2*07we01 is the provisional allele name for SLA-2*07:03
    eq_(parse("SLA-2*07we01", map_allele_aliases=True),
        Allele.get("SLA", "2", "07", "03"))

def test_SLA_2_jh01_no_normalization():
    # SLA-2*jh01 is the provisional allele name for 2*15:01
    eq_(parse("SLA-2*jh01", map_allele_aliases=False),
        Allele.get("SLA", "2", "jh01"))

def test_SLA_2_jh01_normalize():
    # SLA-2*jh01 is the provisional allele name for 2*15:01
    eq_(parse("SLA-2*jh01", map_allele_aliases=True),
        Allele.get("SLA", "2", "15", "01"))

def test_SLA_2_w09pt22_no_normalization():
    # SLA-2*w09pt22 is the provisional allele name for 2*09:03
    eq_(parse("SLA-2*w09pt22", map_allele_aliases=False),
        Allele.get("SLA", "2", "w09pt22"))


def test_SLA_2_w09pt22_normalize():
    # SLA-2*w09pt22 is the provisional allele name for 2*09:03
    eq_(parse("SLA-2*w09pt22", map_allele_aliases=True),
        Allele.get("SLA", "2", "09", "03"))
