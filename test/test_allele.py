from mhcgnomes import Allele
from nose.tools import eq_

def test_allele_get_A0201():
    allele = Allele.get("HLA", "A", "02", "01")
    assert allele is not None
    assert type(allele) is Allele
    eq_(allele.species_prefix, "HLA")
    eq_(allele.gene_name, "A")
    eq_(list(allele.allele_fields), ["02", "01"])
    eq_(allele.mhc_class, "Ia")


def test_restrict_num_allele_fields_A02010101():
    allele_eight_digit = Allele.get("HLA", "A", "02", "01", "01", "01")
    assert allele_eight_digit is not None
    assert type(allele_eight_digit) is Allele
    eq_(allele_eight_digit.num_allele_fields, 4)
    allele_four_digit = allele_eight_digit.restrict_num_allele_fields(2)
    eq_(allele_four_digit.num_allele_fields, 2)
