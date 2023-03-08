from mhcgnomes import parse, Pair

def test_restrict_num_allele_fields_HLA_DRA_01_01_01_01_DRB1_01_01_01_01():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    assert type(result) == Pair
    assert result.alpha.allele_fields == ("01", "01", "01", "01")
    assert result.beta.allele_fields == ("01", "01", "01", "01")

    result2 = result.restrict_allele_fields(2)
    assert result2.alpha.allele_fields == ("01", "01",)
    assert result2.beta.allele_fields == ("01", "01",)



def test_annotation_null_HLA_DRA_01_01_01_01_DRB1_01_01_01_01N():
    result = parse("DRA*01:01:01:01/DRB*01:01:01:01")
    assert type(result) == Pair
    assert not result.annotation_null

    result = parse("DRA*01:01:01:01/DRB*01:01:01:01N")
    assert type(result) == Pair
    assert result.annotation_null
