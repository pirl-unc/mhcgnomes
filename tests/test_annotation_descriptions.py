"""
Public meanings for allele-name annotations, and the cytosolic spelling (#217).
"""

import warnings

import pytest

from mhcgnomes import Pair, parse
from mhcgnomes.allele_annotations import annotation_descriptions, valid_functional_annotations


def test_every_parsed_annotation_has_a_description():
    assert set(annotation_descriptions) == valid_functional_annotations
    assert all(isinstance(text, str) and text for text in annotation_descriptions.values())


@pytest.mark.parametrize(
    "name, annotation",
    [
        ("HLA-A*01:11N", "N"),
        ("HLA-A*24:02:01:02L", "L"),
        ("HLA-B*44:02:01:02S", "S"),
        ("HLA-A*01:01C", "C"),
        ("HLA-A*01:01A", "A"),
        ("HLA-A*32:11Q", "Q"),
        ("HLA-A*02:01:01G", "G"),
        ("HLA-A*02:01P", "P"),
        ("Caja-B5*01:01Ps", "Ps"),
        ("Mamu-B*074:03Sp", "Sp"),
    ],
)
def test_allele_annotation_descriptions(name, annotation):
    allele = parse(name)
    assert allele.annotations == (annotation,)
    assert allele.annotation_descriptions == {annotation: annotation_descriptions[annotation]}


def test_no_annotation_no_descriptions():
    assert parse("HLA-A*02:01").annotation_descriptions == {}


@pytest.mark.parametrize(
    "name, expected",
    [
        ("HLA-A*01:11N", "absent"),
        ("HLA-B*44:02:01:02S", "absent"),
        ("HLA-A*01:01C", "absent"),
        ("Caja-B5*01:01Ps", "absent"),
        # A pseudogene by gene curation, with no suffix.
        ("HLA-H*02:01", "absent"),
        ("HLA-A*01:01A", "uncertain"),
        ("HLA-A*32:11Q", "uncertain"),
        ("HLA-A*24:02:01:02L", "low"),
        # Nothing in these names bears on expression.
        ("HLA-A*02:01", None),
        ("HLA-A*02:01:01G", None),
        ("HLA-A*02:01P", None),
        ("Mamu-B*074:03Sp", None),
    ],
)
def test_cell_surface_expression(name, expected):
    assert parse(name).cell_surface_expression == expected


def test_cytosolic_is_spelled_correctly():
    assert parse("HLA-A*01:01C").annotation_cytosolic is True
    assert parse("HLA-A*02:01").annotation_cytosolic is False


@pytest.mark.parametrize(
    "name, expected",
    [
        ("HLA-A*01:01C", True),
        ("HLA-A*02:01", False),
        ("HLA-DRA*01:01/DRB1*01:01", False),
        ("HLA-A", False),  # a Gene: the Result default
    ],
)
def test_misspelled_property_still_works_but_is_deprecated(name, expected):
    result = parse(name)
    with pytest.warns(DeprecationWarning, match="annotation_cytosolic"):
        assert result.annotation_cystosolic is expected


def test_pair_cytosolic_does_not_warn_through_its_chains():
    pair = parse("HLA-DRA*01:01/DRB1*01:01")
    assert type(pair) is Pair
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert pair.annotation_cytosolic is False
