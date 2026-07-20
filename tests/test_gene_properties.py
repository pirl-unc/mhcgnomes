import pytest

from mhcgnomes import Gene, Species, parse


@pytest.mark.parametrize(
    "gene_name",
    ["H", "J", "K", "L", "P", "V", "DRB6", "DRB7", "DRB8", "DRB9"],
)
def test_curated_human_pseudogene_loci(gene_name):
    gene = Gene.get("HLA", gene_name)

    assert gene.pseudogene_status is True
    assert gene.is_pseudogene


def test_human_gene_level_pseudogene_status_is_distinct_from_allele_annotation():
    allele = parse("HLA-H*02:01")

    assert allele.gene.pseudogene_status is True
    assert allele.gene.is_pseudogene
    assert not allele.annotation_pseudogene
    assert allele.is_pseudogene


def test_explicit_ps_annotation_still_marks_allele_without_gene_level_status():
    allele = parse("Caja-B5*01:01ps")

    assert allele.gene.pseudogene_status is None
    assert not allele.gene.is_pseudogene
    assert allele.annotation_pseudogene
    assert allele.is_pseudogene


def test_gene_pseudogene_status_is_species_specific_and_inherited():
    human_g = Gene.get("HLA", "G")
    rhesus_g = Gene.get("Mamu", "G")
    crab_eating_macaque_g = Gene.get("Mafa", "G")

    assert human_g.pseudogene_status is False
    assert not human_g.is_pseudogene
    assert rhesus_g.pseudogene_status is True
    assert rhesus_g.is_pseudogene
    assert crab_eating_macaque_g.pseudogene_status is True
    assert crab_eating_macaque_g.is_pseudogene


def test_descendant_specific_pseudogene_status_does_not_leak_to_sibling_species():
    bornean_orangutan_ap = Gene.get("Popy", "Ap")
    sumatran_orangutan_ap = Gene.get("Poab", "Ap")

    assert bornean_orangutan_ap.pseudogene_status is True
    assert bornean_orangutan_ap.is_pseudogene
    assert sumatran_orangutan_ap.pseudogene_status is None
    assert not sumatran_orangutan_ap.is_pseudogene


def test_gene_record_exposes_combined_pseudogene_status():
    hla_h_record = Gene.get("HLA", "H").to_record()
    hla_a_record = parse("HLA-A*02:01").to_record()
    annotated_record = parse("Caja-B5*01:01ps").to_record()

    assert hla_h_record["pseudogene_status"] is True
    assert hla_h_record["is_pseudogene"] is True
    assert hla_a_record["pseudogene_status"] is None
    assert hla_a_record["is_pseudogene"] is False
    assert annotated_record["pseudogene_status"] is True
    assert annotated_record["is_pseudogene"] is True


def test_gene_properties_and_families_are_immutable():
    human = Species.get("HLA")

    with pytest.raises(TypeError):
        human.gene_name_to_properties["H"] = {"pseudogene": False}
    with pytest.raises(TypeError):
        human.gene_name_to_properties["H"]["pseudogene"] = False
    with pytest.raises(TypeError):
        human.gene_family_name_to_gene_names["TAP"].add("TAPBP")


@pytest.mark.parametrize("species_prefix", ["HLA", "SLA", "Mamu", "Xetr"])
def test_tap_family_is_inherited_cross_species(species_prefix):
    species = Species.get(species_prefix)

    assert species.find_matching_gene_family_name("tap") == "TAP"
    assert species.get_gene_family_members("TAP") == ("TAP1", "TAP2")
