from mhcgnomes import parse, Allele, Species, Gene


def test_parse_RT1():
    species = parse("RT1")
    assert type(species) == Species
    assert species.prefix == "RT1"

def test_Species_get_RT1():
    species = Species.get("RT1")
    assert type(species) == Species
    assert species.prefix == "RT1"

def test_parse_Rano():
    species = parse("Rano")
    assert type(species) == Species
    assert species.prefix == "Rano"


def test_Species_get_Rano():
    species = Species.get("Rano")
    assert type(species) == Species
    assert species.prefix == "Rano"

def test_rat_class1_allele_Bbu():
    assert parse("RT1-Bb*u") == Allele.get("RT1", "Bb", "u")

def test_rat_class1_allele_Bbu_no_star():
    assert parse("RT1-Bbu") == Allele.get("RT1", "Bb", "u")

def test_rat_class1_allele_Db1a():
    assert parse("RT1-Db1*a") == Allele.get("RT1", "Db1", "a")

def test_rat_class1_allele_Db1a_no_star():
    assert parse("RT1-Db1a") == Allele.get("RT1", "Db1", "a")

def test_rat_class1_allele_DMaa():
    assert parse("RT1-DMa*a") == Allele.get("RT1", "DMA", "a")

def test_rat_class1_allele_DMaa_no_star():
    assert parse("RT1-DMAa") == Allele.get("RT1", "DMA", "a")


def test_rat_class1_allele_95f():
    assert parse("RT1-9.5*f") == Allele.get("RT1", "9.5", "f")

def test_rat_class1_allele_95f_no_star():
    assert parse("RT1-9.5f") == Allele.get("RT1", "9.5", "f")

def test_rat_class1_allele_M3_1_av1():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    assert parse("RT1-M3-1*av1") == expected

def test_rat_class1_allele_M3_1_av1_no_star():
    expected = Allele.get("RT1", "M3-1", "av1")
    assert expected is not None
    assert parse("RT1-M3-1av1") == expected

"""
def test_RT1_Db_A_weird_uniprot_name():
    seq = "Class II RT1.D(A) beta chain"
    expected = Allele.get("RT1", "Db", "a")
    assert expected is not None
    assert parse(seq) == expected
"""
