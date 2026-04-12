"""
Parser support for Tasmanian devil (Sarcophilus harrisii) MHC class I names
from the DFT2 paper (Caldwell et al. 2018, eLife 7:e35314 / PMC6092122).

The paper uses a "SahaI*NN" shorthand where the number runs across multiple
class I loci (Saha-UA/UB/UC/UD). Table 1 assigns specific numbers to loci;
the rest are left unattributed. mhcgnomes routes paper names through a
curated alias table (see data/curated_allele_aliases.yaml) to either
locus-typed Alleles or AlleleWithoutGene values depending on paper
attribution.
"""

import pytest

from mhcgnomes import AlleleWithoutGene, parse

from .common import eq_


@pytest.mark.parametrize(
    ("paper_name", "canonical"),
    [
        # Paper Table 1 explicit locus assignments
        ("SahaI*27", "Saha-UC*27"),
        ("SahaI*32", "Saha-UD*32"),
        ("SahaI*35", "Saha-UA*35"),
        ("SahaI*46", "Saha-UA*46"),
        ("SahaI*90", "Saha-UB*90"),
        # SahaI*27-1 is a single-substitution sibling of SahaI*27 at Saha-UC
        ("SahaI*27-1", "Saha-UC*27:01"),
        # The paper text uses en-dash (U+2013); folded to ASCII hyphen
        ("SahaI*27\u20131", "Saha-UC*27:01"),
        # Dashed species-gene form should resolve the same way
        ("Saha-I*27", "Saha-UC*27"),
        ("Saha-I*90", "Saha-UB*90"),
    ],
)
def test_assigned_sahai_names(paper_name, canonical):
    allele = parse(paper_name, use_allele_aliases=True)
    eq_(allele.to_string(), canonical)


@pytest.mark.parametrize(
    "paper_name",
    ["SahaI*29", "SahaI*33", "SahaI*36", "SahaI*37", "SahaI*97"],
)
def test_unassigned_sahai_names_become_allele_without_gene(paper_name):
    # Paper Table 1 does not attribute these to a specific Saha locus, so
    # the curated alias table routes them to an AlleleWithoutGene carrying
    # just the numeric designator.
    result = parse(paper_name, use_allele_aliases=True)
    assert isinstance(result, AlleleWithoutGene), (
        f"{paper_name!r} should produce AlleleWithoutGene, got {type(result).__name__}"
    )
    expected_number = paper_name.split("*")[1]
    eq_(result.name, expected_number)
    eq_(result.species.mhc_prefix, "Saha")


def test_saha_loci_parse_as_genes():
    # UA and UD were previously absent from species.yaml; they should now
    # parse as first-class Saha genes alongside UB/UC/UK/UM.
    for locus in ("UA", "UB", "UC", "UD", "UK", "UM"):
        gene = parse(f"Saha-{locus}")
        eq_(gene.to_string(), f"Saha-{locus}")


def test_saha_uc_sub_allele_suffix():
    # The numeric "-N" sub-allele suffix (paper uses this for SahaI*27-1)
    # should parse as a two-field allele regardless of whether the alias
    # table is involved.
    allele = parse("Saha-UC*27-1")
    eq_(allele.to_string(), "Saha-UC*27:01")


def test_em_dash_normalizes_to_hyphen():
    # Em-dash (U+2014) should fold to ASCII hyphen in the same way as
    # en-dash (U+2013), so round-tripping unicode-normalized paper text
    # produces the same parse.
    allele = parse("Saha-UC*27\u20141")
    eq_(allele.to_string(), "Saha-UC*27:01")
