from mhcgnomes import Allele
from mhcgnomes.mhc_class_helpers import is_valid_restriction, restrict_alleles

from .common import eq_


def test_is_valid_restriction_class2_subtypes():
    assert is_valid_restriction("II", "IIa")
    assert is_valid_restriction("II", "IIb")
    assert not is_valid_restriction("II", "Ia")
    assert not is_valid_restriction("IIa", "II")


def test_restrict_alleles_class2_includes_ii_iia_iib():
    alleles = [
        Allele.get("HLA", "DRA", "01", "01"),
        Allele.get("HLA", "DOA", "01", "01"),
        Allele.get("HLA", "DRB6", "01", "01"),
    ]
    restricted = restrict_alleles(alleles, "II")
    eq_(set(restricted), set(alleles))
