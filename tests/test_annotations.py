from mhcgnomes import parse, Allele
from mhcgnomes.allele_annotations import (
    parse_annotations_from_allele_fields,
)

def test_questionable_A_01_281Q():
    result = parse("A*01:281Q")
    assert result == Allele.get("HLA", "A", "01", "281", annotation="Q")
    assert result.annotations == ("Q",)
    assert result.annotation_questionable

def test_questionable_A01281Q():
    result = parse("A01281Q")
    assert result == Allele.get("HLA", "A", "01", "281", annotation="Q")
    assert result.annotations == ("Q",)
    assert result.annotation_questionable

def test_null_E_01_08_01N():
    result = parse("E*01:08:01N")
    assert result == Allele.get("HLA", "E", "01", "08", "01", annotation="N")
    assert result.annotations == ("N",)
    assert result.annotation_null


def test_null_E010801N():
    result = parse("E010801N")
    assert result == Allele.get("HLA", "E", "01", "08", "01", annotation="N")
    assert result.annotations == ("N",)
    assert result.annotation_null

def test_parse_functional_annotations_from_allele_fields_E010801N():
    results = parse_annotations_from_allele_fields("010801N")
    assert len(results) == 3
    assert results[0] == ("010801",)
    assert results[1] == ()
    assert results[2] == ("N",)

def test_parse_workshop_annotation_from_allele_fields_W113G():
    results = parse_annotations_from_allele_fields("W113G")
    assert len(results) == 3
    assert results[0] == ("113",)
    assert results[1] == ("W",)
    assert results[2] == ("G",)

def test_secreted_B_44_02_01_02S():
    result = parse("B*44:02:01:02S")
    assert result == Allele.get("HLA", "B", "44", "02", "01", "02", annotation="S")
    assert result.annotations == ("S",)
    assert result.annotation_secreted

def test_secreted_B_44020102S():
    result = parse("B*44020102S")
    assert result == Allele.get("HLA", "B", "44", "02", "01", "02", annotation="S")
    assert result.annotations == ("S",)
    assert result.annotation_secreted

