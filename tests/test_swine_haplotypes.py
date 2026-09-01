"""
Swine (SLA) haplotypes, and the guard that every curated haplotype keeps its
alleles.

The two SLA entries that existed before this wrote their members with the
species prefix -- "SLA-1*01:01" rather than "1*01:01" -- but the loader hands
the parser the string *after* the species. So both haplotypes resolved with an
empty allele list and printed a warning to stdout on every parse, and one of
them had the SLA-2 column filed under SLA-3.

Naming, from Reiner et al. 2024 (PMC10925748): the ISAG/IUIS-VIC committee
gives swine haplotypes their own prefix -- `Hp-` high resolution, `Lr-` low
resolution -- numbered <class I>.<class II>.

Allele composition from Table 2 ("Known haplotypes") of Baekbo et al. 2017,
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5472656/

https://github.com/pirl-unc/mhcgnomes/issues/143
"""

import io
from contextlib import redirect_stdout

import pytest

from mhcgnomes import Haplotype, parse
from mhcgnomes.data import haplotypes as raw_haplotypes
from mhcgnomes.parser import _blank_locus_gene_name

from .common import eq_, ok_

# Every class I haplotype the SLA Nomenclature Committee has designated, with
# the alleles Table 2 lists for it.
SLA_HAPLOTYPES = {
    "Hp-1a.0": ["SLA-1*01:01", "SLA-2*01:01", "SLA-3*01:01"],
    "Hp-2.0": ["SLA-1*02:01", "SLA-1*07:01", "SLA-2*02:01"],  # plus SLA-3 blank
    "Hp-4b.0": ["SLA-1*04:01", "SLA-2*04:02:01", "SLA-3*04:01"],
    "Hp-6.0": ["SLA-1*08:05", "SLA-2*05:04", "SLA-3*06:01"],
    "Hp-7.0": ["SLA-1*08:01", "SLA-2*05:02", "SLA-3*07:01:01"],
    "Hp-17.0": ["SLA-1*08:04", "SLA-2*06:03", "SLA-3*03:05"],
    "Hp-28.0": ["SLA-1*09:01", "SLA-1*15:01", "SLA-2*05:03", "SLA-3*07:01:02"],
    "Hp-32.0": ["SLA-1*07:02", "SLA-2*02:02", "SLA-3*04:02"],
    "Hp-62.0": ["SLA-1*14:01", "SLA-2*06:02"],
}


@pytest.mark.parametrize("name,allele_names", sorted(SLA_HAPLOTYPES.items()))
def test_swine_haplotype_carries_its_alleles(name, allele_names):
    result = parse(name, required_result_types=[Haplotype])
    # haplotypes.yaml is keyed by MHC prefix, and SLA belongs to the genus
    # node rather than to Sus scrofa -- which is why #143 reported "no Sus
    # scrofa entry at all" when the entry was there under SLA.
    eq_(result.species.prefix, "SLA")
    eq_(result.species.name, "Sus sp.")
    eq_(sorted(allele.to_string() for allele in result.alleles), sorted(allele_names))


@pytest.mark.parametrize("name", sorted(SLA_HAPLOTYPES))
def test_swine_haplotype_parses_with_and_without_the_species_prefix(name):
    # The Hp- prefix is the haplotype's own; SLA- is the gene and allele
    # prefix. Both spellings appear in print.
    eq_(parse(name).to_string(), f"SLA-{name}")
    eq_(parse(f"SLA-{name}").to_string(), f"SLA-{name}")


def test_hp_2_0_records_its_null_sla3_rather_than_omitting_it():
    """
    Table 2 gives SLA-3 as *null* for this haplotype. Since #162 that is data
    rather than a comment.
    """
    eq_([gene.to_string() for gene in parse("Hp-2.0").absent_genes], ["SLA-3"])


def test_hp_2_0_has_no_class3_allele():
    """
    Table 2 gives Hp-2.0 as SLA-1*0201/*0701, SLA-3 *null*, SLA-2*0201. The
    curated entry read SLA-3*02:01, which is the SLA-2 column misfiled a locus
    over. SLA-3*02:01 is a real allele, so nothing complained.
    """
    genes = {allele.gene.name for allele in parse("Hp-2.0").alleles}
    eq_(genes, {"1", "2"})
    ok_(parse("SLA-3*02:01") is not None, "SLA-3*02:01 exists; it just is not in this haplotype")


def test_undesignated_haplotype_spellings_do_not_resolve():
    # Only the high-resolution class I series is curated. The class II series
    # (Hp-0.03) and the low-resolution one (Lr-4.0) are defined by allele
    # *groups* such as SLA-1*15XX, which this file has no way to express.
    for name in ["Hp-4.0", "Hp-1.1", "Hp-0.03", "Lr-4.0", "SLA-1.1"]:
        eq_(parse(name, raise_on_error=False), None)


# ---------------------------------------------------------------------------
# The general form of the bug: a haplotype that quietly loses its alleles
# ---------------------------------------------------------------------------

ALL_HAPLOTYPES = sorted(
    (prefix, name, tuple(alleles))
    for prefix, entries in raw_haplotypes.items()
    for name, alleles in entries.items()
)


@pytest.mark.parametrize("prefix,name,allele_names", ALL_HAPLOTYPES)
def test_every_curated_haplotype_keeps_every_allele(prefix, name, allele_names):
    """
    A member allele the parser cannot read is dropped with a warning printed to
    stdout, which nothing reads and no test caught. The result is a Haplotype
    that claims a name and carries nothing.
    """
    # Ask for the haplotype reading specifically: "H2-d" is also the mouse D
    # gene and "RT1-b" also a rat class II locus, and those readings win.
    captured = io.StringIO()
    with redirect_stdout(captured):
        result = parse(f"{prefix}-{name}", required_result_types=[Haplotype], raise_on_error=False)
    ok_(result is not None, f"{prefix}-{name} has no haplotype reading")
    # A "<gene>*Blank" member is a locus the haplotype positively lacks, so it
    # lands in absent_genes rather than alleles (#162). It is still a member,
    # and still must not be dropped.
    blank_members = [m for m in allele_names if _blank_locus_gene_name(m) is not None]
    expected_alleles = len(allele_names) - len(blank_members)
    eq_(
        len(result.alleles),
        expected_alleles,
        f"{prefix}-{name} kept {len(result.alleles)} of {expected_alleles} alleles"
        + (f"; parser said: {captured.getvalue().strip()}" if captured.getvalue() else ""),
    )
    eq_(
        len(result.absent_genes),
        len(blank_members),
        f"{prefix}-{name} kept {len(result.absent_genes)} of {len(blank_members)} blank loci",
    )
