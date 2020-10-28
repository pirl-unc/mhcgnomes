from mhcgnomes import parse, Allele
from mhcgnomes.allele_annotations import (
    parse_functional_annotations_from_allele_fields,
)
from nose.tools import eq_

def test_questionable_A_01_281Q():
    result = parse("A*01:281Q")
    eq_(result, Allele.get("HLA", "A", "01", "281", annotation="Q"))
    eq_(result.annotations, ("Q",))
    assert result.annotation_questionable

def test_questionable_A01281Q():
    result = parse("A01281Q")
    eq_(result, Allele.get("HLA", "A", "01", "281", annotation="Q"))
    eq_(result.annotations, ("Q",))
    assert result.annotation_questionable

def test_null_E_01_08_01N():
    result = parse("E*01:08:01N")
    eq_(result, Allele.get("HLA", "E", "01", "08", "01", annotation="N"))
    eq_(result.annotations, ("N",))
    assert result.annotation_null


def test_null_E010801N():
    result = parse("E010801N")
    eq_(result, Allele.get("HLA", "E", "01", "08", "01", annotation="N"))
    eq_(result.annotations, ("N",))
    assert result.annotation_null

def test_parse_functional_annotations_from_allele_fields_E010801N():
    results = parse_functional_annotations_from_allele_fields("010801N")
    assert len(results) == 2
    eq_(results[0], ("010801",))
    eq_(results[1], ["N",])

def test_secreted_B_44_02_01_02S():
    result = parse("B*44:02:01:02S")
    eq_(result, Allele.get("HLA", "B", "44", "02", "01", "02", annotation="S"))
    eq_(result.annotations, ("S",))
    assert result.annotation_secreted

def test_secreted_B_44020102S():
    result = parse("B*44020102S")
    eq_(result, Allele.get("HLA", "B", "44", "02", "01", "02", annotation="S"))
    eq_(result.annotations, ("S",))
    assert result.annotation_secreted

