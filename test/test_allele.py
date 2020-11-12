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


def test_no_annotations():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant

def test_annotation_null():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="N")
    assert allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_cytosolic():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="C")
    assert not allele.annotation_null
    assert allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant

def test_annotation_secreted():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="S")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant

def test_annotation_questionable():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Q")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant


def test_annotation_group():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="G")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert allele.annotation_group
    assert not allele.annotation_splice_variant

def test_annotation_splice_variant():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Sp")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert not allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert allele.annotation_splice_variant

def test_annotation_pseudogene():
    allele = Allele.get("HLA", "A", "02", "01", "01", "01", annotation="Ps")
    assert not allele.annotation_null
    assert not allele.annotation_cystosolic
    assert not allele.annotation_aberrant_expression
    assert not allele.annotation_secreted
    assert allele.annotation_pseudogene
    assert not allele.annotation_questionable
    assert not allele.annotation_low_expression
    assert not allele.annotation_group
    assert not allele.annotation_splice_variant
