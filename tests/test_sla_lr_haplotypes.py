"""
The low-resolution (Lr-) swine haplotype series.

The other half of the ISAG/IUIS-VIC scheme. Lr- types are defined by PCR-SSP
allele *groups* rather than by sequenced alleles, so a member is a one-field
allele: "1*04" is SLA-1*04XX, any allele in group 04.

Sources (read verbatim from Europe PMC full-text XML and supplementary files):
  * Hammer et al., Animal Genetics 2021;52:523 (PMID 34028065, PMC8362188),
    Tables 1 & 2 and Table S2b.
  * Hammer et al., Front Immunol 2024;15:1360022 (PMID 38469309, PMC10925748),
    Abstract, Tables 1-3, and Supplementary Tables 3 & 4 (DataSheet_1.docx).
  * de León et al., Vaccines 2020;8:E513 (PMID 32911818, PMC7563261),
    Table 5 & Discussion.
  * Techakriengkrai et al., Front Vet Sci 2021;8:637682 (PMID 33996967,
    PMC8121083), Tables 2-4.
  * Choi et al., Asian-Australas J Anim Sci 2016;29:169 (PMID 26950861,
    PMC4811781), Table 1; Ando et al., Cells 2019;8:E783 (PMID 31357541,
    PMC6721486), Table 1.

https://github.com/pirl-unc/mhcgnomes/issues/162
"""

import pytest

from mhcgnomes import Haplotype, parse

from .common import eq_, ok_

CLASS_I = [
    "01.0",
    "02.0",
    "03.0",
    "04.0",
    "05.0",
    "06.0",
    "07.0",
    "08.0",
    "10.0",
    "11.0",
    "17.0",
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
    "0.03",
    "0.04",
    "0.05",
    "0.06",
    "0.07",
    "0.08",
    "0.09",
    "0.10",
    "0.11",
    "0.12",
    "0.13",
    "0.14",
    "0.15",
    "0.19",
    "0.20",
    "0.21",
    "0.22",
    "0.23",
    "0.24",
    "0.25",
    "0.26",
    "0.27",
    "0.30",
    "0.32",
    "0.33",
    "0.35",
    "0.36",
]

# Rows deliberately not curated, and why. Kept as data so that adding one has
# to come here and say what changed.
DELIBERATELY_ABSENT = {
    "01.0/04.0": "composite name",
    "16.0 mod": "ambiguity unresolved, one heterozygous animal",
    "31.0/63.0": "composite name",
    "0.08b": "alphabetical suffix distinguishing near-identical haplotypes",
    "0.15a": "alphabetical suffix distinguishing near-identical haplotypes",
    "0.15b": "alphabetical suffix distinguishing near-identical haplotypes",
    "0.19a": "alphabetical suffix distinguishing near-identical haplotypes",
    "0.19b": "alphabetical suffix distinguishing near-identical haplotypes",
    "24.0": "SLA-1 untyped, not blank",
    "33.0": "SLA-1 untyped, not blank",
    "0.17": "DQA listed as 'Blank or Null' in PMC10925748",
    "0.29": "DRB1 untyped, not blank",
    "38.0": "class I '+' notation not defined by the source",
    "45.0": "class I '+' at two loci, notation not defined",
    "52.0": "cross-group '/' alternatives at SLA-2",
    "53.0": "cross-group '/' alternatives at SLA-2",
    "50.0": "only in PMC8121083 whose class I primer panel omits SLA-1*03/*15 and duplicated SLA-1",
    "81.0": "only in PMC8121083; identical to its truncated Lr-35.0 row",
    "0.16": "only in PMC6721486 which did not type DQA",
    "0.18": "only in PMC6721486 which did not type DQA",
    "0.37": "only in PMC6721486 which did not type DQA",
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


def test_the_class1_plus_rows_are_out_because_the_notation_is_undefined():
    """
    Class I "+" rows (Lr-38.0, Lr-45.0) remain excluded because no checked
    primary source defines "+" at SLA-1 or SLA-2. By contrast, class II
    DQA "04XX+05XX" (Lr-0.21, Lr-0.25, Lr-0.27) is confirmed as allele group
    DQA*04 in PMC10925748 Abstract, PMC7563261 Table 5 & Discussion,
    PMC4811781 Table 1 ("04XX+w05XX"), and PMC8362188 Table 2 fn 3 / Table S2b.
    """
    for name in ["38.0", "45.0"]:
        eq_(parse(f"Lr-{name}", raise_on_error=False), None)


def test_resolved_dqa_04_and_same_group_slash_class2_haplotypes():
    expected = {
        "Lr-0.03": ["SLA-DQA*01", "SLA-DQB1*03", "SLA-DRB1*03"],
        "Lr-0.08": ["SLA-DQA*02", "SLA-DQB1*02", "SLA-DRB1*08"],
        "Lr-0.11": ["SLA-DQA*03", "SLA-DQB1*04", "SLA-DRB1*09"],
        "Lr-0.15": ["SLA-DQA*02", "SLA-DQB1*02", "SLA-DRB1*04"],
        "Lr-0.19": ["SLA-DQA*03", "SLA-DQB1*07", "SLA-DRB1*04"],
        "Lr-0.21": ["SLA-DQA*04", "SLA-DQB1*05", "SLA-DRB1*01"],
        "Lr-0.25": ["SLA-DQA*04", "SLA-DQB1*09", "SLA-DRB1*13"],
        "Lr-0.27": ["SLA-DQA*04", "SLA-DQB1*09", "SLA-DRB1*09"],
        "Lr-0.36": ["SLA-DQA*04", "SLA-DQB1*10", "SLA-DRB1*01"],
    }
    for name, alleles in expected.items():
        result = parse(name, required_result_types=[Haplotype])
        eq_(sorted(a.to_string() for a in result.alleles), alleles)


def test_gottingen_minipig_class1_haplotypes_from_pmc10925748():
    """Lr-03.0 (SLA-1 Null), Lr-10.0, and Lr-17.0 from PMC10925748 Supp Table 3."""
    lr03 = parse("Lr-03.0", required_result_types=[Haplotype])
    eq_(sorted(a.to_string() for a in lr03.alleles), ["SLA-2*03", "SLA-3*03"])
    eq_([g.to_string() for g in lr03.absent_genes], ["SLA-1"])

    lr10 = parse("Lr-10.0", required_result_types=[Haplotype])
    eq_(sorted(a.to_string() for a in lr10.alleles), ["SLA-1*05", "SLA-2*03", "SLA-3*08"])

    lr17 = parse("Lr-17.0", required_result_types=[Haplotype])
    eq_(sorted(a.to_string() for a in lr17.alleles), ["SLA-1*08", "SLA-2*06", "SLA-3*03"])


@pytest.mark.parametrize(
    "unpadded,canonical",
    [
        ("Lr-1.0", "SLA-Lr-01.0"),
        ("Lr-3.0", "SLA-Lr-03.0"),
        ("Lr-4.0", "SLA-Lr-04.0"),
        ("SLA-Lr-4.0", "SLA-Lr-04.0"),
        ("Lr-0.1", "SLA-Lr-0.01"),
        ("SLA-Lr-0.1", "SLA-Lr-0.01"),
        ("Lr-0.3", "SLA-Lr-0.03"),
        ("Lr-0.8", "SLA-Lr-0.08"),
    ],
)
def test_unpadded_and_padded_lr_spellings_resolve_identically(unpadded, canonical):
    """Published SLA papers mix Lr-4.0 / Lr-04.0 and Lr-0.1 / Lr-0.01."""
    result = parse(unpadded, required_result_types=[Haplotype])
    eq_(result.to_string(), canonical)
    eq_(result, parse(canonical, required_result_types=[Haplotype]))


def test_unpadded_lr_works_with_sus_scrofa_and_class_restriction():
    result = parse("Lr-4.0", default_species="Sus scrofa")
    eq_(result.to_string(), "Susc-Lr-04.0")
    eq_(result, parse("Lr-04.0", default_species="Sus scrofa"))
    restricted = parse("Lr-4.0 class I")
    eq_(restricted.to_string(), "SLA-Lr-04.0 class I")


@pytest.mark.parametrize("bad", ["Lr-00.01", "Lr-004.0", "Lr-0.010", "Lr-0.8b"])
def test_malformed_zero_padding_does_not_resolve(bad):
    eq_(parse(bad, raise_on_error=False), None)


def test_multiple_alleles_at_one_locus_are_both_listed():
    """Table 1 gives Lr-02.0 SLA-1 as "02XX,07XX"."""
    genes = [a.to_string() for a in parse("Lr-02.0").alleles]
    ok_("SLA-1*02" in genes and "SLA-1*07" in genes, genes)


def test_the_high_resolution_series_is_untouched():
    eq_(parse("Hp-17.0").to_string(), "SLA-Hp-17.0")
    eq_([g.to_string() for g in parse("Hp-2.0").absent_genes], ["SLA-3"])
