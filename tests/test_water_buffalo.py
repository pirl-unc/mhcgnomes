"""
Water buffalo (Bubalus bubalis) MHC loci.

Bubalus sits under Bos sp. because the species tree is a prefix-scope
hierarchy: IPD-MHC files water buffalo in the BoLA group and its class II
sequences are assigned to cattle loci by trans-species polymorphism. The
entry declares the loci with published buffalo sequences itself, so that
they round-trip as the literature writes them.

Sources:
  PMID 12580780  Polymorphisms in MHC-DRA and -DRB alleles of water buffalo
  PMID 22383896  Molecular characterization of MHC-DRB cDNA in water buffalo
  https://www.ebi.ac.uk/ipd/mhc/group/BoLA/species
"""

import pytest

from mhcgnomes import Species, parse

from .common import eq_

# Locus names as the papers and IPD-MHC write them
PUBLISHED_LOCI = ["DRA", "DRB", "DQA", "DQA1", "DQA2", "DQB"]


@pytest.mark.parametrize("gene_name", PUBLISHED_LOCI)
def test_published_buffalo_locus_round_trips(gene_name):
    """A locus the literature names must come back with the same name."""
    result = parse(f"Bubu-{gene_name}")
    eq_(result.species.name, "Bubalus bubalis")
    eq_(result.name, gene_name)
    eq_(result.to_string(), f"Bubu-{gene_name}")


@pytest.mark.parametrize("gene_name", PUBLISHED_LOCI)
def test_buffalo_declares_its_published_loci(gene_name):
    """
    Declared rather than inherited, so the ontology records that the buffalo
    locus itself has been characterized.
    """
    assert Species.get_by_latin_name("Bubalus bubalis").declares_gene(gene_name)


def test_buffalo_DRB_is_not_renamed_to_DRB3():
    """
    The cattle gene alias maps DRB -> DRB3, and buffalo used to inherit it.
    PMID 22383896 says only that "the Bubu-DRB sequence showed maximum
    homology with the BoLA-DRB3*0101 allele of cattle" -- homology, not
    identity -- and every paper writes the buffalo locus as Bubu-DRB.
    """
    eq_(parse("Bubu-DRB").name, "DRB")
    eq_(parse("Bubu-DRB").to_string(), "Bubu-DRB")


def test_cattle_DRB_is_still_renamed_to_DRB3():
    """The alias is right for cattle, where DRB3 is the expressed DRB locus."""
    eq_(parse("BoLA-DRB").name, "DRB3")


def test_inherited_cattle_loci_still_parse_for_buffalo():
    """
    Buffalo remains under Bos sp., so cattle loci it does not declare are
    still reachable. Detaching it would break these.
    """
    for gene_name in ["DRB3", "DQB1", "DRB1"]:
        result = parse(f"Bubu-{gene_name}")
        eq_(result.species.name, "Bubalus bubalis")
        assert not result.species.declares_gene(gene_name)


def test_buffalo_alleles_parse():
    eq_(parse("Bubu-DQA*01:01").species.name, "Bubalus bubalis")
    eq_(parse("Bubu-DRB*01:01").to_string(), "Bubu-DRB*01:01")


def test_bola_still_resolves_to_cattle():
    """The buffalo entry must not disturb the group prefix."""
    eq_(Species.get("BoLA").name, "Bos sp.")
    eq_(parse("BoLA class I").species.name, "Bos sp.")
    eq_(parse("BoLA-DRB3*011:01").species.name, "Bos sp.")


def test_no_speculative_DQB_loci():
    """
    A trans-species phylogeny paper labels buffalo sequences BoLA-DQB1/3/4,
    but IPD-MHC registers only BoLA-DQB. DQB3 and DQB4 are that analysis's
    locus labels, not designations, so they are deliberately absent.
    """
    assert parse("BoLA-DQB3", raise_on_error=False) is None
    assert parse("BoLA-DQB4", raise_on_error=False) is None
