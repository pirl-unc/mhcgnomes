"""Class metadata on Serotype and ResultWithMultipleAlleles collections (#254)."""

import json
import subprocess
import sys

import pytest

from mhcgnomes import (
    Allele,
    AlleleWithoutGene,
    AmbiguousAlleles,
    Class2Locus,
    Haplotype,
    ParseError,
    Parser,
    Serotype,
    Species,
    Supertype,
    dataframe_from_string_list,
    infer_mhc_class,
    parse,
    parse_gene_class,
    parse_outcome_to_row,
)
from mhcgnomes.cli import outcome_to_cli_row
from mhcgnomes.mhc_class_helpers import common_mhc_class


def test_common_mhc_class_handles_empty_homogeneous_subtype_and_mixed():
    hla = Species.get("HLA")
    a_allele = Allele.get("HLA", "A", "02", "01")
    b_allele = Allele.get("HLA", "B", "44", "02")
    e_allele = Allele.get("HLA", "E", "01", "01")
    drb_allele = Allele.get("HLA", "DRB1", "01", "01")
    dmb_allele = Allele.get("HLA", "DMB", "01", "01")
    no_class_allele = AlleleWithoutGene.get("BoLA", "T2C", mhc_class=None)

    assert common_mhc_class([]) is None
    assert common_mhc_class([a_allele, b_allele]) == "Ia"
    assert common_mhc_class([a_allele, e_allele]) == "I"
    assert common_mhc_class([drb_allele]) == "IIa"
    assert common_mhc_class([drb_allele, dmb_allele]) == "II"
    assert common_mhc_class([a_allele, drb_allele]) is None
    assert common_mhc_class([a_allele, no_class_allele]) is None
    assert common_mhc_class([hla]) is None


def test_serotype_class_metadata_properties():
    b12 = parse("HLA-B12")
    assert isinstance(b12, Serotype)
    assert b12.has_mhc_class is True
    assert b12.mhc_class == "Ia"
    assert b12.is_class1 is True
    assert b12.is_class2 is False
    assert b12.is_class2_alpha is False
    assert b12.is_class2_beta is False

    dr1 = parse("HLA-DR1")
    assert isinstance(dr1, Serotype)
    assert dr1.has_mhc_class is True
    assert dr1.mhc_class == "IIa"
    assert dr1.is_class1 is False
    assert dr1.is_class2 is True
    assert dr1.is_class2_alpha is False
    assert dr1.is_class2_beta is True


@pytest.mark.parametrize(
    "name, expected_name, expected_class",
    [
        ("HLA-B12 class I", "B12", "Ia"),
        ("class I HLA-B12", "B12", "Ia"),
        ("human class I HLA-B12", "B12", "Ia"),
        ("HLA-B44 class I", "B44", "Ia"),
        ("HLA-DR1 class II", "DR1", "IIa"),
        ("class II HLA-DR1", "DR1", "IIa"),
        ("HLA-DQ2 class II", "DQ2", "IIa"),
    ],
)
@pytest.mark.parametrize("use_allele_aliases", [False, True])
def test_class_qualified_serotype_names_succeed(
    name, expected_name, expected_class, use_allele_aliases
):
    result = parse(name, use_allele_aliases=use_allele_aliases)
    assert isinstance(result, Serotype)
    assert result.name == expected_name
    assert result.raw_string == name
    assert result.has_mhc_class is True
    assert result.mhc_class == expected_class


@pytest.mark.parametrize(
    "name",
    [
        "HLA-B12 class II",
        "class II HLA-B12",
        "HLA-DR1 class I",
        "class I HLA-DR1",
        "Patr-DR1 class I",
        "Patr-DR1 class II",
        "DLA-A2 class I",
        "HLA A2 supertype class II",
        # Ensure #200 rejected syntax and invalid chain-qualified serotypes remain rejected
        "HLA-A*02:01 class I",
        "HLA-A*02 class I",
        "HLA-B12 class I alpha",
        "HLA-DR1 class II beta",
        "HLA-B12 alpha",
        "HLA-DR1 beta",
    ],
)
def test_mismatched_empty_or_invalid_class_qualified_names_fail(name):
    assert parse(name, raise_on_error=False) is None
    with pytest.raises(ParseError):
        parse(name)
    assert infer_mhc_class(name) is None
    assert parse_gene_class(name, raise_on_error=False) is None


def test_empty_collections_do_not_vacuously_report_any_class():
    hla = Species.get("HLA")
    empty_collections = [
        parse("Patr-DR1"),
        parse("DLA-A2"),
        parse("BoLA-DRB6"),
        parse("BF19"),
        Serotype(species=hla, name="Empty", alleles=[]),
        Supertype(species=hla, name="Empty", alleles=[]),
        Haplotype(species=hla, name="Empty", alleles=[]),
        AmbiguousAlleles(species=hla, alleles=[]),
    ]
    for obj in empty_collections:
        assert obj.mhc_class is None
        assert obj.has_mhc_class is False
        assert obj.is_class1 is False
        assert obj.is_class2 is False
        assert obj.is_class2_alpha is False
        assert obj.is_class2_beta is False

    # Parser class filters reject empty collections for both classes
    for name in ("Patr-DR1", "DLA-A2", "BoLA-DRB6", "BF19"):
        assert parse(name, only_class1=True, raise_on_error=False) is None
        assert parse(name, only_class2=True, raise_on_error=False) is None
        assert infer_mhc_class(name) is None
        assert parse_gene_class(name, raise_on_error=False) is None


def test_mixed_and_subtype_collections_behave_explicitly():
    hla = Species.get("HLA")
    a_allele = Allele.get("HLA", "A", "02", "01")
    e_allele = Allele.get("HLA", "E", "01", "01")
    drb_allele = Allele.get("HLA", "DRB1", "01", "01")
    dmb_allele = Allele.get("HLA", "DMB", "01", "01")

    mixed_i_ii = Serotype(species=hla, name="Mixed", alleles=[a_allele, drb_allele])
    assert mixed_i_ii.mhc_class is None
    assert mixed_i_ii.has_mhc_class is False
    assert mixed_i_ii.is_class1 is False
    assert mixed_i_ii.is_class2 is False

    mixed_class1_subtypes = Serotype(species=hla, name="MixedI", alleles=[a_allele, e_allele])
    assert mixed_class1_subtypes.mhc_class == "I"
    assert mixed_class1_subtypes.has_mhc_class is True
    assert mixed_class1_subtypes.is_class1 is True
    assert mixed_class1_subtypes.is_class2 is False

    mixed_class2_subtypes = Serotype(species=hla, name="MixedII", alleles=[drb_allele, dmb_allele])
    assert mixed_class2_subtypes.mhc_class == "II"
    assert mixed_class2_subtypes.has_mhc_class is True
    assert mixed_class2_subtypes.is_class1 is False
    assert mixed_class2_subtypes.is_class2 is True

    bola = Species.get("BoLA")
    ambig_partial_unknown = AmbiguousAlleles(
        species=bola,
        alleles=[
            AlleleWithoutGene.get("BoLA", "X1", mhc_class="I"),
            AlleleWithoutGene.get("BoLA", "X2", mhc_class=None),
        ],
    )
    assert ambig_partial_unknown.mhc_class is None
    assert ambig_partial_unknown.has_mhc_class is False
    assert ambig_partial_unknown.is_class1 is False


def test_haplotype_and_supertype_class_metadata():
    h2_b = parse("H2-b")
    assert h2_b.mhc_class is None
    assert h2_b.has_mhc_class is False
    assert h2_b.is_class1 is False
    assert h2_b.is_class2 is False

    h2_b_c1 = parse("H2-b class I")
    assert h2_b_c1.mhc_class == "I"
    assert h2_b_c1.has_mhc_class is True
    assert h2_b_c1.is_class1 is True
    assert h2_b_c1.is_class2 is False

    h2_b_c2 = parse("H2-b class II")
    assert h2_b_c2.mhc_class == "II"
    assert h2_b_c2.has_mhc_class is True
    assert h2_b_c2.is_class1 is False
    assert h2_b_c2.is_class2 is True

    bf19_c2 = parse("BF19 class II")
    assert bf19_c2.mhc_class == "II"
    assert bf19_c2.has_mhc_class is True
    assert bf19_c2.is_class1 is False
    assert bf19_c2.is_class2 is True

    empty_locus_hap = Haplotype(
        species=Species.get("H2"),
        name="empty_e",
        alleles=[],
        locus_restriction=Class2Locus.get("H2", "E"),
    )
    assert empty_locus_hap.mhc_class == "II"
    assert empty_locus_hap.has_mhc_class is True
    assert empty_locus_hap.is_class2 is True
    assert empty_locus_hap.is_class1 is False

    a2_supertype = parse("HLA A2 supertype")
    assert isinstance(a2_supertype, Supertype)
    assert a2_supertype.mhc_class == "Ia"
    assert a2_supertype.has_mhc_class is True
    assert a2_supertype.is_class1 is True
    assert parse("HLA A2 supertype class I") == a2_supertype


def test_class_metadata_agrees_across_properties_filters_inference_dataframe_and_cli():
    cases = [
        ("HLA-B12", "Ia", True, False),
        ("HLA-B12 class I", "Ia", True, False),
        ("HLA-DR1", "IIa", False, True),
        ("HLA-DR1 class II", "IIa", False, True),
        ("HLA A2 supertype", "Ia", True, False),
        ("H2-b class I", "I", True, False),
        ("H2-b class II", "II", False, True),
        ("BF19 class II", "II", False, True),
        ("SLA-Hp-2.0", "Ia", True, False),
        ("Saha-I*74/88", "I", True, False),
        ("H2-b", None, False, False),
        ("BF19", None, False, False),
        ("Patr-DR1", None, False, False),
    ]
    names = [name for name, _, _, _ in cases]
    frame = dataframe_from_string_list(names, raise_on_error=False)
    completed = subprocess.run(
        [sys.executable, "-m", "mhcgnomes", "--format", "json", *names],
        text=True,
        capture_output=True,
        check=True,
    )
    cli_rows = json.loads(completed.stdout)

    for idx, (name, expected_class, expected_c1, expected_c2) in enumerate(cases):
        parsed = parse(name)
        assert parsed.mhc_class == expected_class
        assert parsed.has_mhc_class is (expected_class is not None)
        assert parsed.is_class1 is expected_c1
        assert parsed.is_class2 is expected_c2

        # Parser filters agree
        c1_result = parse(name, only_class1=True, raise_on_error=False)
        c2_result = parse(name, only_class2=True, raise_on_error=False)
        assert (c1_result is not None) is expected_c1
        assert (c2_result is not None) is expected_c2

        # Class inference agrees
        assert infer_mhc_class(name) == expected_class
        gene_info = parse_gene_class(name, raise_on_error=False)
        assert (gene_info.mhc_class if gene_info is not None else None) == expected_class

        # Outcome row, DataFrame, and CLI agree
        expected_str = "" if expected_class is None else expected_class
        row = parse_outcome_to_row(name, parsed)
        assert row["mhc_class"] == expected_str
        assert outcome_to_cli_row(name, parsed)["mhc_class"] == expected_str
        assert frame["mhc_class"].iloc[idx] == expected_str
        assert cli_rows[idx]["mhc_class"] == expected_str


def test_allele_without_gene_none_class_has_mhc_class_false():
    allele = AlleleWithoutGene.get("BoLA", "T2C", mhc_class=None)
    assert allele.mhc_class is None
    assert allele.has_mhc_class is False
    assert allele.is_class1 is False
    assert allele.is_class2 is False
    assert Parser().parse("BoLA-T2C", only_class1=True, raise_on_error=False) is None
    assert Parser().parse("BoLA-T2C", only_class2=True, raise_on_error=False) is None
    assert infer_mhc_class("BoLA-T2C") is None
