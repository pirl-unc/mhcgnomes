from mhcgnomes import parse, Class2Pair
from nose.tools import eq_

def test_restrict_num_allele_fields_HLA_DRA_01_01_01_01_DRB1_01_01_01_01():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    eq_(type(result), Class2Pair)
    eq_(result.alpha.allele_fields, ("01", "01", "01", "01"))
    eq_(result.beta.allele_fields, ("01", "01", "01", "01"))

    result2 = result.restrict_num_allele_fields(2)
    eq_(result2.alpha.allele_fields, ("01", "01",))
    eq_(result2.beta.allele_fields, ("01", "01",))



def test_annotation_null_HLA_DRA_01_01_01_01_DRB1_01_01_01_01N():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    eq_(type(result), Class2Pair)
    assert not result.annotation_null

    result = parse("DRA*01:01:01:01/DRB*01:01:01:01N")
    eq_(type(result), Class2Pair)
    assert result.annotation_null
