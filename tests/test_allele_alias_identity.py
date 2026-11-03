"""Aliases preserve field boundaries, identity, context and process stability."""

import json
import os
import subprocess
import sys

import pytest

from mhcgnomes import Species, parse
from mhcgnomes.parser import Parser


# IMGT/HLA 3.66.0 Allelelist.txt: HLA03784 and HLA02465. Legacy compact
# spellings are separate entries in the pinned Allelelist_history.txt.
# https://raw.githubusercontent.com/ANHIG/IMGTHLA/3660/Allelelist.txt
@pytest.mark.parametrize(
    "source,expected",
    [
        ("A*02:172", "A*02:172"),
        ("A*02172", "A*02:17:02:01"),
        ("B*15:112", "B*15:112"),
        ("B*15112", "B*15:11:02"),
        ("A*9272", "A*02:172"),
        ("B*9512", "B*15:112"),
        ("B*08:01", "B*08:01"),
        ("B*0801", "B*08:01:01:01"),
        # Deleted_alleles.txt: HLA02592 -> HLA02578 -> C*04:15:02.
        ("C*04:22", "C*04:15:02"),
        ("Cw*0422", "C*04:15:02"),
    ],
)
def test_alias_identity_across_entry_paths(source, expected):
    for name in [source, "HLA-" + source, source.replace("*", ""), source.lower()]:
        result = parse(name, use_allele_aliases=True)
        assert result.to_string() == "HLA-" + expected
        assert parse(result.to_string(), use_allele_aliases=True) == result
        assert parse(name, species="human", use_allele_aliases=True) == result
        assert Parser(use_allele_aliases=True).parse(name) == result
        # Verbose disables the explicit-species fast path.
        assert Parser(use_allele_aliases=True, verbose=True).parse(name) == result


def test_alias_tables_retain_distinct_field_boundaries():
    human = Species.get("human")
    assert "A*02172" in human.allele_aliases
    assert "A*02:172" not in human.allele_aliases
    assert human.get_allele_alias("A", "02:172") is None
    assert human.get_allele_alias("A", "02172") == ("A", "02:17:02:01")


def _synthetic_species(**overrides):
    human = Species.get("human")
    fields = {field: getattr(human, field) for field in Species.init_field_names()}
    fields.update(overrides)
    return Species(**fields)


def test_lookup_prefers_supplied_gene_then_sorted_alternates():
    # Synthetic conflicting mappings exercise precedence independently of
    # whatever the curated tables happen to contain.
    species = _synthetic_species(
        name="Alias precedence test",
        gene_aliases={"Cx": "C", "Cw": "C"},
        allele_aliases={"C*01:01": "C*02:01", "Cw*01:01": "C*03:01", "Cx*01:01": "C*04:01"},
        known_alleles={"C": ["Ab"], "Cw": ["aB"], "Cx": ["AB"]},
    )
    assert species.get_allele_alias("C", "01:01") == ("C", "02:01")
    assert species.get_allele_alias("Cw", "01:01") == ("C", "03:01")
    assert species.get_known_allele("C", "ab") == ("C", "Ab")
    fallback = _synthetic_species(
        name="Alias fallback test", allele_aliases={"Cw*01:01": "C*03:01", "Cx*01:01": "C*04:01"}
    )
    assert fallback.get_allele_alias("C", "01:01") == ("C", "03:01")


def test_alias_cycle_through_gene_synonym_is_rejected():
    species = _synthetic_species(
        name="Alias cycle test", allele_aliases={"C*01:01": "Cw*02:01", "C*02:01": "C*01:01"}
    )
    with pytest.raises(ValueError, match="Cyclic allele alias"):
        species.get_allele_alias("C", "01:01")


@pytest.mark.parametrize("source", ["SLA-DRB1*kb03N", "SLA-DRB1*kb04N"])
def test_alias_target_keeps_null_annotation(source):
    result = parse(source, use_allele_aliases=True)
    assert result.annotations == ("N",)
    assert result.cell_surface_expression == "absent"
    assert parse(result.to_string(), use_allele_aliases=True) == result


def test_alias_resolution_is_independent_of_hash_seed():
    code = """
import json
from mhcgnomes import parse
names = ["HLA-C*04:22", "HLA-Cw*0422", "HLA-A*02:172", "HLA-A*02172"]
print(json.dumps([parse(n, use_allele_aliases=True).to_string() for n in names]))
"""
    for seed in range(4):
        output = subprocess.check_output(
            [sys.executable, "-c", code],
            env={**os.environ, "PYTHONHASHSEED": str(seed)},
            text=True,
        )
        assert json.loads(output) == [
            "HLA-C*04:15:02",
            "HLA-C*04:15:02",
            "HLA-A*02:172",
            "HLA-A*02:17:02:01",
        ]
