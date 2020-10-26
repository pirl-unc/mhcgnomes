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