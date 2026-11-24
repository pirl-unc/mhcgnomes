from mhcgnomes import Allele, Species, parse

from .common import eq_


def test_parse_DLA_as_dog_species():
    eq_(parse("DLA"), Species.get("DLA"))


def test_parse_Calu_as_dog_species():
    eq_(parse("Calu"), Species.get("Calu"))


def test_parse_dog_as_species():
    eq_(parse("dog"), Species.get("Canis lupus familiaris"))
    eq_(parse("wolf"), Species.get("Calu"))
    assert Species.get("dog") != Species.get("wolf")
    assert Species.get("dog") != Species.get("DLA")


def test_domestic_dog_scientific_and_common_identity_202():
    dog = Species.get("Canis lupus familiaris")
    wolf = Species.get("Canis lupus")
    canis_sp = Species.get("Canis sp.")

    assert dog is not None
    assert wolf is not None
    assert canis_sp is not None
    assert dog != wolf
    assert dog != canis_sp
    assert wolf != canis_sp

    for alias in (
        "dog",
        "Dog",
        "domestic dog",
        "Canis lupus familiaris",
        "canis lupus familiaris",
        "CANIS LUPUS FAMILIARIS",
        "canis_lupus_familiaris",
        "Canis_lupus_familiaris",
        "Canis familiaris",
        "canis familiaris",
        "canis_familiaris",
        "CanisLupusFamiliaris",
        "CanisFamiliaris",
    ):
        eq_(Species.get(alias), dog, f"Species.get({alias!r}) did not resolve to domestic dog")

    for wolf_alias in ("wolf", "gray wolf", "Canis lupus", "canis_lupus", "Calu"):
        eq_(Species.get(wolf_alias), wolf, f"Species.get({wolf_alias!r}) did not resolve to wolf")

    for genus_alias in ("canine", "DLA", "Canis sp.", "CanisSp"):
        eq_(
            Species.get(genus_alias),
            canis_sp,
            f"Species.get({genus_alias!r}) did not resolve to Canis sp.",
        )

    assert dog.is_dog
    assert canis_sp.is_dog
    assert not wolf.is_dog

    assert dog.is_child_of(wolf)
    assert dog.is_descendant_of(canis_sp)
    assert dog.compatible_with(wolf)
    assert dog.compatible_with(canis_sp)

    # DLA allele parsing stays compatible with domestic dog and wolf species constraints
    eq_(parse("DLA-88*001:01").species, canis_sp)
    eq_(parse("DLA-88*001:01", species="Canis lupus familiaris").species, dog)
    eq_(parse("DLA-DRB1*001:01", species="dog").species, dog)
    eq_(parse("DLA-DRB1*001:01", species="Canis lupus").species, wolf)
    eq_(parse("CanisFamiliaris-DRB1*001:01").species, dog)

    # Misspellings stay unresolved
    assert Species.get("canis lupis") is None
    assert Species.get("canis lupis familiaris") is None


def test_parse_dog_class2_allele_dla_dqa1_001_01():
    eq_(parse("DLA-DQA1*00101"), Allele.get("DLA", "DQA1", "001", "01"))


def test_normalized_string_dog_class2_allele_dla_dqa1_001_01_yes_alias():
    eq_(parse("DLA-DQA1*00101").to_string(use_old_species_prefix=True), "DLA-DQA1*001:01")


def test_only_2_digits_in_first_allele_field():
    # make sure it parses at all
    eq_(parse("DLA-DQA1*0101"), Allele.get("DLA", "DQA1", "01", "01"))
    # TODO:
    #   once we have normalization of allele field lengths, check that
    #   first allele field becomes three digit
    #
    #   eq_(parse("DLA-DQA1*0101").allele_fields[0], "001")


def test_species_code_calu_no_alias():
    eq_(parse("Calu-DQA1*00101").to_string(use_old_species_prefix=False), "Calu-DQA1*001:01")


def test_species_code_calu_yes_alias():
    eq_(parse("Calu-DQA1*00101").to_string(use_old_species_prefix=True), "DLA-DQA1*001:01")


def test_parse_dog_class1_allele_dla_88_508_01():
    expected = Allele.get("DLA", "88", "508", "01")
    parsed = parse("DLA-88*50801")
    eq_(parsed, expected)


def test_dla_88_first_field_uses_official_three_digit_width():
    historical = parse("DLA-88*01:01")
    canonical = parse("DLA-88*001:01")

    eq_(historical, canonical)
    eq_(historical.to_string(), "DLA-88*001:01")


def test_dla_88_wider_first_field_is_preserved():
    eq_(parse("DLA-88*501:01").to_string(), "DLA-88*501:01")


def test_compact_string_dog_class1_allele_dla_88_508_01():
    eq_(parse("DLA-88*50801").compact_string(), "88*50801")


def test_normalized_string_dog_class1_allele_dla_88_508_01_yes_alias():
    eq_(parse("DLA-88*50801").to_string(use_old_species_prefix=True), "DLA-88*508:01")


def test_normalized_string_dog_class1_allele_dla_88_508_01_no_alias():
    eq_(parse("DLA-88*50801").to_string(use_old_species_prefix=False), "DLA-88*508:01")
