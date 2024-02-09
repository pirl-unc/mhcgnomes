from mhcgnomes import parse, Allele


def test_sheep_class1_allele_vs_get():
    assert parse("Ovar-N*50001") == Allele.get("Ovar", "N", "500", "01")


def test_sheep_class1_allele_string():
    assert parse("Ovar-N*50001").to_string(use_old_species_prefix=False) == "Ovar-N*500:01"

def test_sheep_class1_allele_string_old_prefix():
    assert parse("Ovar-N*50001").to_string(use_old_species_prefix=True) == "OLA-N*500:01"

def test_sheep_class2_allele_vs_get():
    assert parse("Ovar-DRB1*0804") == Allele.get("Ovar", "DRB1", "08", "04")


def test_sheep_class2_allele_string():
    assert parse(
            "Ovar-DRB1*0804").to_string(use_old_species_prefix=False) == "Ovar-DRB1*08:04"


def test_sheep_class2_allele_string_old_prefix():
    assert parse("Ovar-DRB1*0804").to_string(use_old_species_prefix=True) == "OLA-DRB1*08:04"

