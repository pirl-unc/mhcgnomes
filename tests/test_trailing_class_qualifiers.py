"""A trailing class sentinel cannot disappear from an allele or pair (#200)."""

import json
import subprocess
import sys

import pytest

from mhcgnomes import (
    ParseError,
    Parser,
    dataframe_from_string_list,
    infer_mhc_class,
    parse,
    parse_gene_class,
)
from mhcgnomes.tokenize import tokenize

COMPOUNDS = [
    f"{name} {qualifier}"
    for name, mhc_class in [
        ("HLA-A*02:01", "I"),
        ("HLA-A*02", "I"),
        ("H2-Kb", "I"),
        ("Mamu-A1*001:01", "I"),
        ("HLA-DRB1*04:01", "II"),
        ("HLA-DQA1*01:01/HLA-DQB1*05:01", "II"),
    ]
    for qualifier in [f"class {mhc_class}", f"MHC class {mhc_class}", f"HLA class {mhc_class}"]
] + [
    "HLA-A*02:01 MHC-I",
    "HLA-A*02:01 class 1",
    "HLA-A*02:01 hla-class I",
    "HLA-A*02:01 class I alpha",
    "HLA-DRB1*04:01 class II beta",
    "Saha-I*27 class I",
]


@pytest.mark.parametrize("name", COMPOUNDS)
@pytest.mark.parametrize("use_allele_aliases", [False, True])
def test_trailing_class_compounds_are_not_single_alleles(name, use_allele_aliases):
    assert parse(name, use_allele_aliases=use_allele_aliases, raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(name, use_allele_aliases=use_allele_aliases)
    parser = Parser(use_allele_aliases=use_allele_aliases)
    assert parser.parse(name, raise_on_error=False) is None
    assert parser.parse_multiple_candidates(name) == []


@pytest.mark.parametrize("name", COMPOUNDS)
def test_gene_class_inference_does_not_revive_the_rejected_compound(name):
    assert parse_gene_class(name, raise_on_error=False) is None
    assert infer_mhc_class(name) is None


@pytest.mark.parametrize(
    "name, expected",
    [
        ("HLA class I", "human class I"),
        ("HLA class II", "human class II"),
        ("class I HLA-A*02:01", "HLA-A*02:01"),
        ("human class I HLA-A*02:01", "HLA-A*02:01"),
        ("mouse MHC class I H2-Kb", "H2-K*b"),
        ("HLA-A class I", "HLA-A"),
        ("H2-b class I", "H2-b class I"),
        ("BF19 class II", "Gaga-BF19 class II"),
        ("Hp-2.0 class I", "SLA-Hp-2.0 class I"),
    ],
)
def test_class_descriptions_and_collection_restrictions_remain_supported(name, expected):
    result = parse(name)
    assert result.to_string() == expected
    assert result.raw_string == name


def test_public_class_token_helper_can_disallow_allele_and_pair_results():
    parser = Parser()
    tokens = tokenize("HLA-A*02:01 class I").tokens
    assert parser.parse_with_class_token_to_multiple_candidates(tokens[-1], tokens[:-1])
    assert not parser.parse_with_class_token_to_multiple_candidates(
        tokens[-1], tokens[:-1], allow_alleles_and_pairs=False
    )


def test_dataframe_and_cli_preserve_rejected_input_as_errors():
    names = ["HLA-A*02:01", *COMPOUNDS]
    frame = dataframe_from_string_list(names, raise_on_error=False)
    assert frame["input"].tolist() == names
    assert frame["type"].tolist() == ["Allele", *["ParseError"] * len(COMPOUNDS)]
    completed = subprocess.run(
        [sys.executable, "-m", "mhcgnomes", "--format", "json", *names],
        text=True,
        capture_output=True,
        check=True,
    )
    rows = json.loads(completed.stdout)
    assert [row["input"] for row in rows] == names
    assert [row["type"] for row in rows] == frame["type"].tolist()
    assert all(row["normalized"] == "" for row in rows[1:])
    assert all(frame["error"].iloc[1:])
