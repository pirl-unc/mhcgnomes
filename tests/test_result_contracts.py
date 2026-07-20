from collections import OrderedDict

import pytest

from mhcgnomes import Allele, Gene, Haplotype, MhcClass, Pair, Serotype, Supertype, parse

ANNOTATION_FLAGS = (
    "annotation_null",
    "annotation_cystosolic",
    "annotation_secreted",
    "annotation_questionable",
    "annotation_low_expression",
    "annotation_aberrant_expression",
    "annotation_group",
    "annotation_pseudogene",
    "annotation_splice_variant",
)


def _annotation_values(result):
    return {flag: getattr(result, flag) for flag in ANNOTATION_FLAGS}


def _expected_annotation_values(*true_flags):
    return {flag: flag in true_flags for flag in ANNOTATION_FLAGS}


GOLDEN_PARSE_CASES = [
    {
        "id": "gene",
        "raw": "HLA-A",
        "expected_type": Gene,
        "expected_to_string": "HLA-A",
        "expected_compact": "A",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("gene", "HLA-A"),
                ("mhc_class", "Ia"),
                ("mutations", ""),
                ("is_mutant", False),
                ("pseudogene_status", None),
                ("is_pseudogene", False),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "class_i_allele",
        "raw": "HLA-A*02:01",
        "expected_type": Allele,
        "expected_to_string": "HLA-A*02:01",
        "expected_compact": "A0201",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("gene", "HLA-A"),
                ("mhc_class", "Ia"),
                ("mutations", ""),
                ("is_mutant", False),
                ("pseudogene_status", None),
                ("is_pseudogene", False),
                ("allele", "HLA-A*02:01"),
                ("annotations", ()),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "class_ii_pair",
        "raw": "HLA-DRA*01:02/DRB1*03:01",
        "expected_type": Pair,
        "expected_to_string": "HLA-DRA*01:02/DRB1*03:01",
        "expected_compact": "DRA0102-DRB1*0301",
        "expected_record": OrderedDict(
            [
                ("gene", "DRA/DRB1"),
                ("mhc_class", "IIa"),
                ("is_mutant", False),
                ("allele", "HLA-DRA*01:02/DRB1*03:01"),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "mutant_allele",
        "raw": "HLA-A*02:01 N80I mutant",
        "expected_type": Allele,
        "expected_to_string": "HLA-A*02:01 N80I mutant",
        "expected_compact": "A0201 N80I mutant",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("gene", "HLA-A"),
                ("mhc_class", "Ia"),
                ("mutations", "N80I"),
                ("is_mutant", True),
                ("pseudogene_status", None),
                ("is_pseudogene", False),
                ("allele", "HLA-A*02:01 N80I mutant"),
                ("annotations", ()),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "pseudogene_allele",
        "raw": "Saoe-G*03:12ps",
        "expected_type": Allele,
        "expected_to_string": "Saoe-G*03:12Ps",
        "expected_compact": "G0312",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "Saoe"),
                ("species_name", "Saguinus oedipus"),
                ("species_latin_name", "Saguinus oedipus"),
                ("gene", "Saoe-G"),
                ("mhc_class", "Ib"),
                ("mutations", ""),
                ("is_mutant", False),
                ("pseudogene_status", True),
                ("is_pseudogene", True),
                ("allele", "Saoe-G*03:12Ps"),
                ("annotations", ("Ps",)),
            ]
        ),
        "expected_annotations": _expected_annotation_values("annotation_pseudogene"),
    },
    {
        "id": "serotype",
        "raw": "A2",
        "expected_type": Serotype,
        "expected_to_string": "HLA-A2",
        "expected_compact": "A2",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("serotype", "HLA-A2"),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "haplotype",
        "raw": "H2-k haplotype",
        "expected_type": Haplotype,
        "expected_to_string": "H2-k",
        "expected_compact": "k",
        "expected_record_error": NotImplementedError,
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "supertype",
        "raw": "A2 supertype",
        "expected_type": Supertype,
        "expected_to_string": "HLA A02 supertype",
        "expected_compact": "A02",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("supertype", "A02"),
                ("supertype_string", "HLA A02 supertype"),
                ("representative_allele", "HLA-A*02:01"),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
    {
        "id": "mhc_class_chain",
        "raw": "HLA class II beta",
        "expected_type": MhcClass,
        "expected_to_string": "human class II beta",
        "expected_compact": "human class II beta",
        "expected_record": OrderedDict(
            [
                ("species_prefix", "HLA"),
                ("species_name", "Homo sapiens"),
                ("species_latin_name", "Homo sapiens"),
                ("mhc_class", "II"),
                ("chain", "beta"),
            ]
        ),
        "expected_annotations": _expected_annotation_values(),
    },
]


@pytest.mark.parametrize(
    "case", GOLDEN_PARSE_CASES, ids=[case["id"] for case in GOLDEN_PARSE_CASES]
)
def test_golden_parser_output_contract(case):
    result = parse(case["raw"])

    assert type(result) is case["expected_type"]
    assert result.to_string() == case["expected_to_string"]
    assert result.compact_string() == case["expected_compact"]
    assert _annotation_values(result) == case["expected_annotations"]

    record_error = case.get("expected_record_error")
    if record_error is not None:
        with pytest.raises(record_error):
            result.to_record()
    else:
        assert result.to_record() == case["expected_record"]


@pytest.mark.parametrize(
    "case", GOLDEN_PARSE_CASES, ids=[case["id"] for case in GOLDEN_PARSE_CASES]
)
def test_cached_parse_identity_and_semantics_are_stable(case):
    first = parse(case["raw"])
    second = parse(case["raw"])

    assert first is second
    assert second == first
    assert hash(second) == hash(first)
    assert second.to_string() == first.to_string()
    assert second.to_dict() == first.to_dict()


@pytest.mark.parametrize(
    "case", GOLDEN_PARSE_CASES, ids=[case["id"] for case in GOLDEN_PARSE_CASES]
)
def test_copy_with_new_raw_string_preserves_semantics(case):
    original = parse(case["raw"])
    copied = original.copy(raw_string=f"copy:{case['raw']}")

    assert type(copied) is type(original)
    assert copied == original
    assert hash(copied) == hash(original)
    assert copied.to_string() == original.to_string()
    assert copied.to_dict() != original.to_dict()
    assert copied.raw_string == f"copy:{case['raw']}"


COPY_CHANGE_CASES = [
    pytest.param("HLA-A", lambda result: result.copy(name="B"), id="gene"),
    pytest.param(
        "HLA-A*02:01",
        lambda result: result.copy(allele_fields=("03", "01")),
        id="class_i_allele",
    ),
    pytest.param(
        "HLA-DRA*01:02/DRB1*03:01",
        lambda result: result.copy(beta=parse("HLA-DRB1*04:01", infer_class2_pairing=False)),
        id="class_ii_pair",
    ),
    pytest.param(
        "HLA-A*02:01 N80I mutant",
        lambda result: result.copy(mutations=()),
        id="mutant_allele",
    ),
    pytest.param(
        "Saoe-G*03:12ps",
        lambda result: result.copy(annotations=()),
        id="pseudogene_allele",
    ),
    pytest.param("A2", lambda result: result.copy(name="A3"), id="serotype"),
    pytest.param("H2-k haplotype", lambda result: result.copy(name="d"), id="haplotype"),
    pytest.param("A2 supertype", lambda result: result.copy(name="A03"), id="supertype"),
    pytest.param(
        "HLA class II beta",
        lambda result: result.copy(chain="alpha"),
        id="mhc_class_chain",
    ),
]


@pytest.mark.parametrize("raw, changer", COPY_CHANGE_CASES)
def test_copy_with_semantic_change_changes_equality(raw, changer):
    original = parse(raw)
    changed = changer(original)

    assert type(changed) is type(original)
    assert changed != original
    assert changed.to_dict() != original.to_dict()


@pytest.mark.parametrize(
    "case", GOLDEN_PARSE_CASES, ids=[case["id"] for case in GOLDEN_PARSE_CASES]
)
def test_serialization_parity_for_representative_results(case):
    original = parse(case["raw"])

    from_dict_result = type(original).from_dict(original.to_dict())
    from_tuple_result = type(original).from_tuple(original.to_tuple())

    assert type(from_dict_result) is type(original)
    assert type(from_tuple_result) is type(original)
    assert from_dict_result == original
    assert from_tuple_result == original
    assert from_dict_result.to_string() == original.to_string()
    assert from_tuple_result.to_string() == original.to_string()
