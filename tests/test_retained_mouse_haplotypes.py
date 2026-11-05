"""Retaining a mouse haplotype must retain its designation (#253, #260).

Memberships below follow Table 3 of the Jackson Laboratory H2 haplotype table:
https://www.informatics.jax.org/downloads/datasets/misc/H2Haplotypes/H2_haplotypes.html
The a haplotype has k at both A genes; b has b at both A genes and at EB.
These tests exercise parsing of existing curation, not new assignments.
"""

import json
import subprocess
import sys

import pytest

from mhcgnomes import (
    Allele,
    Gene,
    Haplotype,
    Pair,
    Parser,
    Species,
    dataframe_from_string_list,
    parse,
)


@pytest.mark.parametrize("prefix", ["H2-", "H-2-"])
@pytest.mark.parametrize("species", [None, "Mus musculus"])
@pytest.mark.parametrize("collapse", [False, True])
@pytest.mark.parametrize("infer", [False, True])
@pytest.mark.parametrize("aliases", [False, True])
def test_IAb_preserves_its_designation_in_every_option_combination(
    prefix, species, collapse, infer, aliases
):
    raw = prefix + "IAb"
    result = parse(
        raw,
        species=species,
        collapse_singleton_haplotypes=collapse,
        infer_class2_pairing=infer,
        use_allele_aliases=aliases,
    )
    assert result.raw_string == raw
    assert result.species == Species.get("Mus musculus")
    if collapse:
        assert isinstance(result, Pair)
        assert result.to_string() == "H2-AA*b/AB*b"
    else:
        assert isinstance(result, Haplotype)
        assert result.name == "b"
        assert result.locus_restriction.name == "A"
        assert {a.to_string() for a in result.alleles} == {"H2-AA*b", "H2-AB*b"}
        assert result.to_string() == "H2-A-b"


@pytest.mark.parametrize(
    "spelling, locus, haplotype, collapsed_type, collapsed_name",
    [
        ("IAb", "A", "b", Pair, "H2-AA*b/AB*b"),
        ("IAa", "A", "a", Pair, "H2-AA*k/AB*k"),
        ("IEb", "E", "b", Allele, "H2-EB*b"),
        ("IAd", "A", "d", Pair, "H2-AA*d/AB*d"),
        ("IEk", "E", "k", Pair, "H2-EA*k/EB*k"),
    ],
)
@pytest.mark.parametrize("prefix", ["H2-", "H-2-"])
@pytest.mark.parametrize("infer", [False, True])
def test_retained_locus_haplotypes_round_trip_and_collapse_to_the_same_members(
    spelling, locus, haplotype, collapsed_type, collapsed_name, prefix, infer
):
    raw = prefix + spelling
    parser = Parser(collapse_singleton_haplotypes=False)
    result = parser.parse(raw, infer_class2_pairing=infer)
    assert isinstance(result, Haplotype)
    assert result.name == haplotype
    assert result.locus_restriction.name == locus
    assert result.raw_string == raw
    canonical = f"H2-{locus}-{haplotype}"
    assert result.to_string() == canonical
    reparsed = parser.parse(canonical, infer_class2_pairing=infer)
    assert reparsed == result
    assert reparsed.alleles == result.alleles
    assert reparsed.raw_string == canonical
    collapsed = parse(canonical, infer_class2_pairing=False)
    assert isinstance(collapsed, collapsed_type)
    assert collapsed.to_string() == collapsed_name
    assert collapsed == parse(raw, infer_class2_pairing=False)


@pytest.mark.parametrize("collapse", [False, True])
@pytest.mark.parametrize("infer", [False, True])
@pytest.mark.parametrize(
    "spelling, gene",
    [
        ("AA", "AA"),
        ("AB", "AB"),
        ("aa", "AA"),
        ("ab", "AB"),
        ("EA", "EA"),
        ("EB", "EB"),
        ("IEb2", "EB2"),
        ("IA-alpha", "AA"),
        ("IA-beta", "AB"),
        ("IE-alpha", "EA"),
        ("IE-beta", "EB"),
    ],
)
def test_gene_symbols_and_chain_descriptions_remain_genes(spelling, gene, collapse, infer):
    result = parse(
        f"H2-{spelling}",
        collapse_singleton_haplotypes=collapse,
        infer_class2_pairing=infer,
    )
    assert isinstance(result, Gene)
    assert result.to_string() == f"H2-{gene}"


@pytest.mark.parametrize("raw", ["IAb", "I-A-b", "mouse IAb", "H2-IAb class II"])
@pytest.mark.parametrize("infer", [False, True])
def test_species_context_and_class_qualified_paths_preserve_the_haplotype(raw, infer):
    result = parse(
        raw,
        species="Mus musculus",
        collapse_singleton_haplotypes=False,
        infer_class2_pairing=infer,
    )
    assert isinstance(result, Haplotype)
    assert result.name == "b"
    assert result.locus_restriction.name == "A"
    assert {a.to_string() for a in result.alleles} == {"H2-AA*b", "H2-AB*b"}
    assert result.raw_string == raw


@pytest.mark.parametrize("option", ["preferred_result_types", "required_result_types"])
@pytest.mark.parametrize("result_type", [Gene, Haplotype])
def test_explicit_result_type_requests_still_override_ranking(option, result_type):
    result = parse("H2-IAb", collapse_singleton_haplotypes=False, **{option: result_type})
    assert isinstance(result, result_type)


@pytest.mark.parametrize("infer", [False, True])
def test_dataframe_retains_haplotypes_and_cli_keeps_default_pairs(infer):
    names = ["H2-IAb", "H-2-IAb"]
    frame = dataframe_from_string_list(
        names, collapse_singleton_haplotypes=False, infer_class2_pairing=infer
    )
    assert frame["input"].tolist() == names
    assert frame["normalized"].tolist() == ["H2-A-b"] * 2
    assert frame["type"].tolist() == ["Haplotype"] * 2
    flags = ["--infer-class2-pairing"] if infer else []
    rows = json.loads(
        subprocess.run(
            [sys.executable, "-m", "mhcgnomes", "--format", "json", *flags, *names],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
    )
    assert [row["normalized"] for row in rows] == ["H2-AA*b/AB*b"] * 2
    assert [row["input"] for row in rows] == names
