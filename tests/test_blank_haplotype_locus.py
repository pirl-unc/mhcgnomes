"""
A haplotype locus that is positively absent, as against one nobody typed.

Published swine haplotypes state it. Table 2 of PMC5472656 gives Hp-2.0's
SLA-3 as *null*, and low-resolution types are written "SLA-1*15XX or Blank".
Leaving the locus out of the member list records it as untyped, which is a
different claim, so #143 could only put the fact in a YAML comment.

`<gene>*Blank` in haplotypes.yaml now says it, and it comes back as
`Haplotype.absent_genes`.

https://github.com/pirl-unc/mhcgnomes/issues/162
"""

import pytest

from mhcgnomes import Haplotype, Serotype, parse
from mhcgnomes.errors import ParseError
from mhcgnomes.parser import Parser, _blank_locus_gene_name

from .common import eq_, ok_


def _absent(haplotype):
    return sorted(gene.to_string() for gene in haplotype.absent_genes)


def test_the_swine_haplotype_records_its_null_locus():
    haplotype = parse("Hp-2.0", required_result_types=[Haplotype])
    eq_(
        sorted(a.to_string() for a in haplotype.alleles),
        ["SLA-1*02:01", "SLA-1*07:01", "SLA-2*02:01"],
    )
    eq_(_absent(haplotype), ["SLA-3"])


def test_a_haplotype_with_no_blank_has_an_empty_tuple_not_none():
    haplotype = parse("Hp-17.0", required_result_types=[Haplotype])
    eq_(haplotype.absent_genes, ())


@pytest.mark.parametrize(
    "member,expected",
    [
        ("3*Blank", "3"),
        ("3*blank", "3"),
        ("3*null", "3"),
        ("DRB1*BLANK", "DRB1"),
        ("3*02:01", None),  # a real allele
        ("3", None),  # a bare gene
        ("*Blank", None),  # no gene named
        ("3*01*Blank", None),  # not a single field
    ],
)
def test_the_member_syntax_is_recognized_exactly(member, expected):
    eq_(_blank_locus_gene_name(member), expected)


# ---------------------------------------------------------------------------
# The bug this was always going to have
# ---------------------------------------------------------------------------


def test_a_class_restriction_keeps_the_absent_locus_it_is_about():
    """
    restrict_mhc_class rebuilds the Haplotype from scratch, so a new field is
    exactly what such a method forgets -- the #137 failure shape.

    The first version of this used is_valid_restriction, which answers "may
    this restriction be applied at all" and returns False for ("Ia", "I"). That
    dropped SLA-3 from a class I reading while the class I alleles beside it
    survived, because they go through restrict_alleles.
    """
    unrestricted = parse("Hp-2.0", required_result_types=[Haplotype])
    eq_(_absent(unrestricted), ["SLA-3"])

    class1 = unrestricted.restrict_mhc_class("I")
    eq_(_absent(class1), ["SLA-3"], "a class I locus vanished from a class I reading")
    eq_(len(class1.alleles), 3)

    class2 = unrestricted.restrict_mhc_class("II")
    eq_(_absent(class2), [])
    eq_(len(class2.alleles), 0)


def test_the_parsed_class_restricted_form_agrees():
    eq_(_absent(parse("Hp-2.0 class I")), ["SLA-3"])
    eq_(_absent(parse("Hp-2.0 class II")), [])


def test_a_class2_locus_restriction_also_carries_the_field():
    # The other rebuilder. SLA-3 is class I, so no class II locus keeps it --
    # what matters is that the code path runs rather than raising or dropping
    # the attribute.
    haplotype = parse("Hp-2.0", required_result_types=[Haplotype])
    for locus in ["DR", "DQ"]:
        restricted = haplotype.restrict_class2_locus(parse(f"SLA-{locus}"))
        if restricted is not None:
            eq_(restricted.absent_genes, ())


# ---------------------------------------------------------------------------
# Serotypes share the loader and must not silently accept it
# ---------------------------------------------------------------------------


def test_a_serotype_that_marks_a_locus_blank_is_an_error():
    """
    _find_matching_name_and_parse_alleles is shared with Serotype. A serotype
    is a set of cross-reacting alleles, not a locus map, so "blank" says
    nothing there -- and a silent drop is how the swine haplotypes lost their
    alleles for years (#143).
    """
    from mhcgnomes.normalizing_dictionary import NormalizingDictionary
    from mhcgnomes.species import Species

    human = Species.get("HLA")
    table = NormalizingDictionary()
    table["FakeSero"] = ["A*02:01", "B*Blank"]

    parser = Parser()
    normalized, alleles, absent = parser._find_matching_name_and_parse_alleles(
        query_name="FakeSero", name_to_alleles_dict=table, species=human
    )
    # The helper reports it rather than dropping it...
    eq_(normalized, "FakeSero")
    eq_([gene.to_string() for gene in absent], ["HLA-B"])
    eq_([allele.to_string() for allele in alleles], ["HLA-A*02:01"])

    # ...and get_serotype refuses it out loud.
    original = human.serotypes
    try:
        object.__setattr__(human, "serotypes", table)
        with pytest.raises(ParseError, match="blank"):
            parser.get_serotype(human, "FakeSero")
    finally:
        object.__setattr__(human, "serotypes", original)


def test_ordinary_serotypes_still_parse():
    result = parse("HLA-A2", required_result_types=[Serotype])
    ok_(len(result.alleles) > 0)
