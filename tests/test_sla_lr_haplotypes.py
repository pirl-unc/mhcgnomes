"""
The low-resolution (Lr-) swine haplotype series.

The other half of the ISAG/IUIS-VIC scheme. Lr- types are defined by PCR-SSP
allele *groups* rather than by sequenced alleles, so a member is a one-field
allele: "1*04" is SLA-1*04XX, any allele in group 04.

Source: Tables 1 and 2 of Hammer et al., "Comparative analysis of swine
leukocyte antigen gene diversity in European farmed pigs", Animal Genetics
2021;52:523, read from the Europe PMC full-text XML of PMC8362188 -- the PMC
HTML carries only per-line counts, and the supplementary PDF only primer
layouts and frequency figures.

Two distinctions the tables draw, and this file has to keep:

  * "Blank" is an absent locus; "Blank" with footnote 5 is an *untyped* one.
    Recording the second as absent would assert something the study explicitly
    did not measure, so those rows are left out.
  * "04XX (04:04)" is footnote 1's medium/high-resolution refinement of the
    group to its left. The group is what a low-resolution haplotype asserts.

https://github.com/pirl-unc/mhcgnomes/issues/162
"""

import pytest

from mhcgnomes import Haplotype, parse

from .common import eq_, ok_

CLASS_I = [
    "01.0",
    "02.0",
    "04.0",
    "05.0",
    "06.0",
    "07.0",
    "08.0",
    "11.0",
    "18.0",
    "21.0",
    "22.0",
    "23.0",
    "25.0",
    "26.0",
    "27.0",
    "28.0",
    "29.0",
    "32.0",
    "34.0",
    "35.0",
    "36.0",
    "37.0",
    "39.0",
    "40.0",
    "42.0",
    "43.0",
    "46.0",
    "47.0",
    "49.0",
    "55.0",
    "56.0",
    "57.0",
    "58.0",
    "59.0",
    "61.0",
    "62.0",
    "64.0",
    "66.0",
    "67.0",
]

CLASS_II = [
    "0.01",
    "0.02",
    "0.04",
    "0.05",
    "0.06",
    "0.07",
    "0.09",
    "0.10",
    "0.12",
    "0.13",
    "0.14",
    "0.20",
    "0.22",
    "0.23",
    "0.24",
    "0.26",
    "0.30",
    "0.32",
    "0.33",
    "0.35",
]

# Rows deliberately not curated, and why. Kept as data so that adding one has
# to come here and say what changed.
DELIBERATELY_ABSENT = {
    "01.0/04.0": "composite name",
    "16.0 mod": "ambiguity unresolved, one heterozygous animal",
    "31.0/63.0": "composite name",
    "0.08b": "alphabetical suffix distinguishing near-identical haplotypes",
    "24.0": "SLA-1 untyped, not blank",
    "33.0": "SLA-1 untyped, not blank",
    "0.29": "DRB1 untyped, not blank",
    "38.0": "'+' notation not defined by the source",
    "45.0": "'+' at two loci, notation not defined",
    "0.21": "'+' at DQA, notation not defined",
    "52.0": "'/' means alternatives at one locus",
    "53.0": "'/' at SLA-2",
    "0.11": "'/' at DRB1",
}


@pytest.mark.parametrize("name", CLASS_I)
def test_class1_haplotype_parses(name):
    result = parse(f"Lr-{name}", required_result_types=[Haplotype])
    eq_(result.species.prefix, "SLA")
    eq_(result.to_string(), f"SLA-Lr-{name}")
    ok_(len(result.alleles) + len(result.absent_genes) >= 3, f"Lr-{name} lost members")


@pytest.mark.parametrize("name", CLASS_II)
def test_class2_haplotype_parses(name):
    result = parse(f"Lr-{name}", required_result_types=[Haplotype])
    eq_(result.to_string(), f"SLA-Lr-{name}")
    genes = {allele.gene.name for allele in result.alleles}
    ok_(genes <= {"DRB1", "DQB1", "DQA"}, f"unexpected loci in Lr-{name}: {genes}")


def test_members_are_allele_groups_not_alleles():
    """
    The whole point of the Lr- series: a one-field allele is the group. If
    these ever gain a second field, the haplotype is asserting a specificity
    the typing method cannot see.
    """
    result = parse("Lr-04.0")
    eq_(sorted(a.to_string() for a in result.alleles), ["SLA-1*04", "SLA-2*04", "SLA-3*04"])
    for allele in result.alleles:
        eq_(len(allele.allele_fields), 1)


def test_a_blank_locus_is_recorded_and_an_untyped_one_is_not():
    """
    Table 1 gives Lr-23.0 SLA-2 as "Blank" and Lr-24.0 SLA-1 as "Blank" with
    footnote 5, "Untyped SLA class I locus". Same word, opposite claims.
    """
    eq_([g.to_string() for g in parse("Lr-23.0").absent_genes], ["SLA-2"])
    eq_(parse("Lr-24.0", raise_on_error=False), None)
    eq_(parse("Lr-33.0", raise_on_error=False), None)
    eq_(parse("Lr-0.29", raise_on_error=False), None)


@pytest.mark.parametrize("name", sorted(DELIBERATELY_ABSENT))
def test_the_rows_left_out_stay_out(name):
    eq_(parse(f"Lr-{name}", raise_on_error=False), None)


def test_the_plus_rows_are_out_because_the_notation_is_undefined():
    """
    Not because "+" is hard to represent -- two members at one locus is
    already how Lr-02.0 records "02XX,07XX". Table 1 never explains "+", and
    Table 2's footnote 3 describes one instance as "Positive with both
    DQA*04XX primer sets", which is an assay result rather than a definition.
    Guessing between "a second allele", "a duplicated locus" and "an
    unresolved call" is the kind of thing AGENTS.md exists to stop.
    """
    for name in ["38.0", "45.0", "0.21", "0.25", "0.27"]:
        eq_(parse(f"Lr-{name}", raise_on_error=False), None)


def test_multiple_alleles_at_one_locus_are_both_listed():
    """Table 1 gives Lr-02.0 SLA-1 as "02XX,07XX"."""
    genes = [a.to_string() for a in parse("Lr-02.0").alleles]
    ok_("SLA-1*02" in genes and "SLA-1*07" in genes, genes)


def test_the_high_resolution_series_is_untouched():
    eq_(parse("Hp-17.0").to_string(), "SLA-Hp-17.0")
    eq_([g.to_string() for g in parse("Hp-2.0").absent_genes], ["SLA-3"])
