import pytest

from mhcgnomes import Species, parse

from .common import eq_


def test_HLA():
    for hla in ["HLA", "hla"]:
        species = Species.get(hla)
        assert species is not None, f"Could not find Species for '{hla}'"
        eq_(species.common_species_name, "human")


def test_human():
    for human in ["human", "Human", "HUMAN"]:
        species = Species.get(human)
        assert species is not None, f"Could not find Species for '{human}'"
        eq_(species.common_species_name, "human")


def test_RT1():
    eq_(Species.get("RT1").prefix, "RT1")


def test_Rano():
    eq_(Species.get("Rano").prefix, "Rano")


def test_T2c_in_BoLA():
    cow = Species.get("BoLA")
    assert "T2c" in cow.known_alleles[None]


def test_known_allele_SLA_3_ydy01():
    pig = Species.get("SLA")
    eq_(pig.get_known_allele(gene_name="3", allele_name="ydy01"), ("3", "YDY01"))


@pytest.mark.parametrize(
    "reported,species_name,gene_name,allele_name,canonical",
    [
        ("H2-Kbm1", "Mus musculus", "K", "bm1", "H2-K*bm1"),
        ("H2-K*bm8", "Mus musculus", "K", "bm8", "H2-K*bm8"),
        ("H2-D*bm13", "Mus musculus", "D", "bm13", "H2-D*bm13"),
        ("H2-K*wm7", "Mus musculus", "K", "wm7", "H2-K*wm7"),
        ("Anpl-UAA*SD", "Anas platyrhynchos", "UAA", "sd", "AnasPlat-UAA*sd"),
    ],
)
def test_published_non_roster_alleles_are_known(
    reported, species_name, gene_name, allele_name, canonical
):
    species = Species.get(species_name)
    assert species.get_known_allele(gene_name, allele_name) == (gene_name, allele_name)
    allele = parse(reported)
    assert allele.to_string() == canonical
    assert allele.is_class1
    assert allele.mhc_class == "Ia"


@pytest.mark.parametrize(
    "species_name,gene_name,allele_name",
    [
        ("Mus musculus", "K", "bm999"),
        ("Mus musculus", "K", "wm999"),
        ("Mus musculus", "D", "bm1"),
        ("Anas platyrhynchos", "UAA", "invented"),
    ],
)
def test_unpublished_single_field_names_are_not_known(species_name, gene_name, allele_name):
    assert Species.get(species_name).get_known_allele(gene_name, allele_name) is None
