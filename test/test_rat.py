
from nose.tools import eq_
from mhcgnomes import parse, Allele, Species


def test_parse_RT1():
    species = parse("RT1")
    eq_(type(species), Species)
    eq_(species.prefix, "RT1")

def test_Species_get_RT1():
    species = Species.get("RT1")
    eq_(type(species), Species)
    eq_(species.prefix, "RT1")

def test_parse_Rano():
    species = parse("Rano")
    eq_(type(species), Species)
    eq_(species.prefix, "Rano")


def test_Species_get_Rano():
    species = Species.get("Rano")
    eq_(type(species), Species)
    eq_(species.prefix, "Rano")

def test_rat_class1_allele_Bbu():
    eq_(parse("RT1-Bb*u"), Allele.get("RT1", "Bb", "u"))

def test_rat_class1_allele_Bbu_no_star():
    eq_(parse("RT1-Bbu"), Allele.get("RT1", "Bb", "u"))

def test_rat_class1_allele_Db1a():
    eq_(parse("RT1-Db1*a"), Allele.get("RT1", "Db1", "a"))

def test_rat_class1_allele_Db1a_no_star():
    eq_(parse("RT1-Db1a"), Allele.get("RT1", "Db1", "a"))

def test_rat_class1_allele_DMaa():
    eq_(parse("RT1-DMa*a"), Allele.get("RT1", "DMA", "a"))

def test_rat_class1_allele_DMaa_no_star():
    eq_(parse("RT1-DMAa"), Allele.get("RT1", "DMA", "a"))


def test_rat_class1_allele_95f():
    eq_(parse("RT1-9.5*f"), Allele.get("RT1", "9.5", "f"))

def test_rat_class1_allele_95f_no_star():
    eq_(parse("RT1-9.5f"), Allele.get("RT1", "9.5", "f"))

def test_rat_class1_allele_M3_1_av1():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    eq_(parse("RT1-M3-1*av1"), expected)

def test_rat_class1_allele_M3_1_av1_no_star():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    eq_(parse("RT1-M3-1av1"), expected)
