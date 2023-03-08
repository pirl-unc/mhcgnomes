from mhcgnomes import (
    parse,
    Allele,
    Species
)


def test_parse_DLA_as_dog_species():
    assert parse("DLA") == Species.get("DLA")


def test_parse_Calu_as_dog_species():
    assert parse("Calu") == Species.get("Calu")


def test_parse_dog_as_species():
    assert parse("dog") == Species.get("Calu")

def test_parse_dog_class2_allele_dla_dqa1_001_01():
    assert parse("DLA-DQA1*00101") == Allele.get("DLA", "DQA1", "001", "01")

def test_normalized_string_dog_class2_allele_dla_dqa1_001_01_yes_alias():
    assert parse("DLA-DQA1*00101").to_string(use_old_species_prefix=True) == "DLA-DQA1*001:01"


def test_only_2_digits_in_first_allele_field():
    # make sure it parses at all
    assert parse("DLA-DQA1*0101") == Allele.get("DLA", "DQA1", "01", "01")
    # TODO:
    #   once we have normalization of allele field lengths, check that
    #   first allele field becomes three digit
    #
    #   assert parse("DLA-DQA1*0101").allele_fields[0] == "001"

def test_species_code_calu_no_alias():
    assert parse("Calu-DQA1*00101").to_string(use_old_species_prefix=False) == "Calu-DQA1*001:01"

def test_species_code_calu_yes_alias():
    assert parse("Calu-DQA1*00101").to_string(use_old_species_prefix=True) == "DLA-DQA1*001:01"


def test_parse_dog_class1_allele_dla_88_508_01():
    expected = Allele.get("DLA", "88", "508", "01")
    parsed = parse("DLA-88*50801")
    assert parsed == expected

def test_compact_string_dog_class1_allele_dla_88_508_01():
    assert parse("DLA-88*50801").compact_string() == "88*50801"

def test_normalized_string_dog_class1_allele_dla_88_508_01_yes_alias():
    assert parse("DLA-88*50801").to_string(use_old_species_prefix=True) ==        "DLA-88*508:01"


def test_normalized_string_dog_class1_allele_dla_88_508_01_no_alias():
    assert parse("DLA-88*50801").to_string(use_old_species_prefix=False) == "DLA-88*508:01"
