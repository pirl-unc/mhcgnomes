"""
Curated-data problems in haplotype and serotype entries (#213).

Parser.find_matching_name_and_parse_alleles drops a member it cannot use: a
"<gene>*Blank" member naming a gene the species does not have, or an allele
name that does not parse. It used to say so with print(), which wrote into the
middle of whatever the caller was printing -- `mhcgnomes --format json` would
have stopped emitting valid JSON. It now uses warnings.warn, and the walk below
fails on either condition, so a curation error in shipped data is caught here
rather than by a user.
"""

import warnings

import pytest

from mhcgnomes import Parser, Species
from mhcgnomes.data import haplotypes, serotypes
from mhcgnomes.normalizing_dictionary import NormalizingDictionary


def _every_entry(table):
    for species_key, entries in table.items():
        species = Species.get(species_key)
        assert species is not None, f"unknown species key {species_key!r}"
        for name in entries:
            yield species, name


@pytest.mark.parametrize(
    "lookup, table",
    [("get_haplotype", haplotypes), ("get_serotype", serotypes)],
    ids=["haplotypes", "serotypes"],
)
def test_every_shipped_entry_loads_without_dropping_members(lookup, table, capsys):
    parser = Parser()
    checked = 0
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        for species, name in _every_entry(table):
            result = getattr(parser, lookup)(species, name)
            assert result is not None, f"{species.prefix} {name!r} did not load"
            checked += 1
    assert checked > 0
    assert capsys.readouterr().out == ""


def _find(members, species="SLA"):
    table = NormalizingDictionary.from_dict({"Test-1": members})
    return Parser().find_matching_name_and_parse_alleles(
        query_name="Test-1", name_to_alleles_dict=table, species=Species.get(species)
    )


def test_unknown_blank_gene_warns_instead_of_printing(capsys):
    with pytest.warns(UserWarning, match="unknown gene 'NOTAGENE' marked blank for 'Test-1'"):
        name, alleles, absent_genes = _find(["NOTAGENE*Blank", "1*01:01"])
    assert capsys.readouterr().out == ""
    assert name == "Test-1"
    assert [allele.to_string() for allele in alleles] == ["SLA-1*01:01"]
    assert absent_genes == []


def test_unparseable_member_warns_instead_of_printing(capsys):
    with pytest.warns(UserWarning, match="unable to parse allele name 'not an allele'"):
        _, alleles, absent_genes = _find(["not an allele", "1*01:01"])
    assert capsys.readouterr().out == ""
    assert [allele.to_string() for allele in alleles] == ["SLA-1*01:01"]
    assert absent_genes == []


def test_known_blank_gene_is_recorded_without_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _, alleles, absent_genes = _find(["3*Blank", "1*01:01"])
    assert [gene.name for gene in absent_genes] == ["3"]
    assert [allele.to_string() for allele in alleles] == ["SLA-1*01:01"]
