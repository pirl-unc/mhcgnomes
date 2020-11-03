from nose.tools import eq_
from mhcgnomes import (
    parse,
    Allele,
    Gene,
    Species
)


def test_macaque_allele_B_08_02():
    allele_name = "Mamu-B*082:02"
    eq_(parse(allele_name).to_string(), "Mamu-B*082:02")
    eq_(parse(allele_name).compact_string(), "B08202")

def test_macaque_allele_B_007_02():
    # expect 3rd zero in the family "007" to be trimmed in the normalized form
    # of this allele
    allele_name = "Mamu-B*007:02"
    eq_(parse(allele_name).to_string(), "Mamu-B*007:02")
    eq_(parse(allele_name).compact_string(), "B00702")

def test_gelada_species_Thge():
    expected = Species.get("Thge")
    assert expected is not None
    eq_(parse('Thge'), expected)


def test_gelada_gene_Thge_DQA1():
    expected = Gene.get("Thge", "DQA1")
    assert expected is not None
    eq_(parse('Thge-DQA1'), expected)


def test_gelada_allele_Thge_DQA1_25_01():
    expected = Allele.get("Thge", "DQA1", "25", "01")
    assert expected is not None
    eq_(parse('Thge-DQA1*25:01'), expected)

def test_monkey_species_Aoni():
    expected = Species.get("Aoni")
    assert expected is not None
    eq_(parse('Aoni'), expected)

def test_monkey_gene_Aoni_DRB3():
    expected = Gene.get("Aoni", "DRB3")
    assert expected is not None
    eq_(parse('Aoni-DRB3'), expected)

def test_monkey_allele_Aoni_DRB3_06_01():
    expected = Allele.get("Aoni", "DRB3", "06", "01")
    assert expected is not None
    eq_(parse('Aoni-DRB3*06:01'), expected)
